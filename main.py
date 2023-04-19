import openai
import difflib
import os
import json
import Levenshtein
from tqdm import tqdm
from dotenv import load_dotenv
import concurrent.futures

DEBUG = False

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Get all files in the example_files directory
example_file_path = "example_files"
files = os.listdir(example_file_path)

# Load system prompts, example files, and user requests
with open("data/correct_system_prompt.txt", "r") as f:
    correct_system_prompt = f.read()

with open("data/diff_system_prompts.json", "r") as f:
    diff_system_prompts = json.load(f)

with open("data/example_requests.json", "r") as f:
    example_requests = json.load(f)

def call_gpt_agent(system_prompts, request):
    messages=[{"role": "system", "content": system_prompts}, {"role": "user", "content": request}]
    # print(json.dumps(messages, indent=4))
    # try: 
    response = openai.ChatCompletion.create(
        model="gpt-4-0314",
        messages=messages,
        temperature=0,
        max_tokens=2048,
    )
    return response.choices[0]['message']['content'].strip()
    # except openai.OpenAIError as error:
    #     print(f"An error occurred while calling the OpenAI API: {error}")
    # except Exception as error:
    #     print(f"An unexpected error occurred: {error}")
    # return None


# Get the user prompt with formatted files
def get_user_prompt(request):
    file_contents = []

    # Loop through each file and format its contents
    for file in files:
        with open(os.path.join(example_file_path, file), "r") as f:
            content = f.read()
            formatted_content = "\n".join([f"{i + 1}:{line}" for i, line in enumerate(content.split("\n"))])
            
            file_contents.append({
                "filePath": os.path.relpath(os.path.join(example_file_path, file)),
                "content": f"FILE_START:{os.path.relpath(os.path.join(example_file_path, file))}\n{formatted_content}"
            })

    # Join the formatted code for each file with a newline separator
    formated_files = "\n".join([file["content"] for file in file_contents])
    
    return f"MESSAGE: {request}\n{formated_files}\n"

# Get unformarted files
def get_file_contents(files):
    file_contents = []

    # Loop through each file and format its contents
    for file in files:
        with open(os.path.join(example_file_path, file), "r") as f:
            content = f.read()
            
            file_contents.append({
                "filePath": os.path.relpath(os.path.join(example_file_path, file)),
                "content": content
            })

    return file_contents

def parse_correct_response(response):
    lines = response.split("\n")
    message = lines[0].split("MESSAGE:")[-1].strip()
    content = "\n".join(lines[1:])
    return content, message

def parse_diff_response(response_string):
    lines = response_string.strip().split("\n")
    message = lines.pop(0).split(":")[1].strip()
    changes = []

    current_file = None
    current_hunk = {}

    for line in lines:
        if line.startswith("EDIT_FILE"):
            if current_file:
                if current_hunk:
                    current_file["hunks"].append(current_hunk)
                    current_hunk = {}
                changes.append(current_file)
            current_file = {"filePath": line.split(":")[1].strip(), "hunks": []}
        elif line.startswith("HUNK_START"):
            if current_hunk:
                current_file["hunks"].append(current_hunk)
            current_hunk = {"hunkStart": int(line.split(":")[1]), "lines": []}
        elif line.startswith("-"):
            if current_hunk:
                current_hunk["lines"].append({"type": "delete", "content": line[1:]})
        elif line.startswith("+"):
            if current_hunk:
                current_hunk["lines"].append({"type": "add", "content": line[1:]})
        else:
            if current_hunk:
                current_hunk["lines"].append({"type": "context", "content": line})

    if current_hunk and current_hunk["lines"]:
        current_file["hunks"].append(current_hunk)
    if current_file:
        changes.append(current_file)

    return (changes, message)



def apply_diff_changes(diff, files):

    # Split the response into individual lines
    lines = diff.strip().split("\n")

    # Iterate over the lines to extract the file edits
    file_edits = []
    for i in range(len(lines)):
        if lines[i].startswith("EDIT_FILE:"):
            file_path = lines[i].correct("EDIT_FILE:", "").strip()
            hunk_starts = [int(l.correct("HUNK_START:", "").strip()) for l in lines[i+1:] if l.startswith("HUNK_START:")]
            file_edits.append((file_path, hunk_starts))

    # Sort the file edits by the starting line of their hunks
    file_edits.sort(key=lambda x: x[1][0])

    # Iterate over the files to extract their contents and format them
    formatted_files = []
    for file in files:
        file_path = file["filePath"]
        file_content = file["content"]

        # Check if the file has any edits
        for edit_file_path, hunk_starts in file_edits:
            if file_path == edit_file_path:
                # Apply the edits to the file content
                lines = file_content.strip().split("\n")
                for hunk_start in hunk_starts:
                    # Find the line numbers affected by this hunk
                    start_line = hunk_start - 1
                    end_line = len(lines)
                    for j in range(i+1, len(lines)):
                        if lines[j].startswith("HUNK_START:"):
                            end_line = j - 1
                            break
                    # Apply the changes to the affected lines
                    for j in range(start_line, end_line):
                        if lines[j].startswith("-"):
                            lines[j] = ""
                        elif lines[j].startswith("+"):
                            lines[j] = lines[j][1:]
                # Format the edited file content
                file_content = "\n".join(lines)

        # Format the file content with PATH:<path> above it
        formatted_file = f"PATH:{file_path}\n{file_content}\n"
        formatted_files.append(formatted_file)

    # Combine the formatted files into a single string and return it
    return "".join(formatted_files)

def apply_changes2(file_contents, changes):
    for change in changes:
        file_path = change["filePath"]
        file_content = next(f["content"] for f in file_contents if f["filePath"] == file_path)

        for hunk in change["hunks"]:
            hunk_start = hunk["hunkStart"]
            line_num = hunk_start - 1

            for line in hunk["lines"]:
                if line["type"] == "delete":
                    del_lines = line["content"].strip().split("\n")
                    file_content = "\n".join(line for i, line in enumerate(file_content.split("\n")) if i < line_num or i >= line_num + len(del_lines))
                    line_num -= len(del_lines)
                elif line["type"] == "add":
                    add_lines = line["content"].strip().split("\n")
                    file_content = "\n".join(line for i, line in enumerate(file_content.split("\n")) if i < line_num) + "\n" + "\n".join(add_lines) + "\n" + "\n".join(line for i, line in enumerate(file_content.split("\n")) if i >= line_num)
                    line_num += len(add_lines)
                else:
                    line_num += 1

        for i, f in enumerate(file_contents):
            if f["filePath"] == file_path:
                file_contents[i]["content"] = file_content
                break

    return file_contents

def apply_changes(file_contents, changes):
    new_file_contents = []
    for file in file_contents:
        file_path = file["filePath"]
        file_content = file["content"]
        file_changes = next(c for c in changes if c["filePath"] == file_path)

        original_lines = file_content.split("\n")

        new_lines = []
        original_line_index = 0

        for hunk in file_changes["hunks"]:
            # Add unchanged lines before the current hunk
            while original_line_index < hunk["hunkStart"] - 1:
                new_lines.append(original_lines[original_line_index])
                original_line_index += 1

            for line in hunk["lines"]:
                if line["type"] == "delete":
                    original_line_index += 1
                elif line["type"] == "add":
                    new_lines.append(line["content"])
                else:
                    if original_line_index < len(original_lines):
                        new_lines.append(original_lines[original_line_index])
                    original_line_index += 1

        # Add remaining unchanged lines after the last hunk
        while original_line_index < len(original_lines):
            new_lines.append(original_lines[original_line_index])
            original_line_index += 1

        new_content = "\n".join(new_lines)
        new_file_contents.append({"filePath": file_path, "content": new_content})
    return new_file_contents


def get_diffed_file_string(file_contents):
    output_lines = []

    for file in file_contents:
        output_lines.append(f"PATH:{file['filePath']}")
        output_lines.extend(file["content"].strip().split("\n"))

    return "\n".join(output_lines)


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def run_tests():
    results = {}

    for system_prompt in tqdm(diff_system_prompts, desc="System Prompts", unit="prompt"):
        system_prompts_results = []
        
        # Loop through each user request
        for request in tqdm(example_requests, desc="User Requests", unit="request", leave=False):
            # Get the user prompt
            user_prompt = get_user_prompt(request)
            
            # Get the response from the correct system prompt
            correct_response = call_gpt_agent(correct_system_prompt, user_prompt)
            debug_print(f"Correct Response: \n{correct_response}")
            
            correct_files_string, correct_message = parse_correct_response(correct_response)
            debug_print(f"Correct Content String: \n{correct_files_string}")

            # Get the files from the diff system prompt
            diff_response_raw = call_gpt_agent(system_prompt["prompt"], user_prompt)
            debug_print("Diff Response: ")
            debug_print(diff_response_raw)

            diff_changes, message = parse_diff_response(diff_response_raw)
            file_contents = get_file_contents(files)
            debug_print("File Contents: ")
            debug_print(json.dumps(file_contents, indent=4))

            debug_print("Diff Changes: ")
            debug_print(json.dumps(diff_changes, indent=4))

            diffed_files = apply_changes(file_contents, diff_changes)
            debug_print("Diffed File Contents: ")
            debug_print(json.dumps(diffed_files, indent=4))
            
            diffed_files_string = get_diffed_file_string(diffed_files)
            debug_print("Changed File Contents String: ")
            debug_print(diffed_files_string)


            # Calculate the Levenshtein distance
            distance = Levenshtein.distance(correct_files_string, diffed_files_string)
            debug_print("Distance: ")
            debug_print(distance)

            # Calculate diff between the two files
            diff = "\n".join(difflib.unified_diff(correct_files_string.splitlines(), diffed_files_string.splitlines(), lineterm=""))
            debug_print("Diff: ")
            debug_print("\n".join(diff))

            # Record the results
            result = {
                "request": request,
                "distance": distance,
                "correct_files": correct_files_string,
                "diffed_files": diffed_files_string,
                "diff": diff
            }
            system_prompts_results.append(result)


        results[system_prompt["id"]] = system_prompts_results

        write_results(results)

        print("Completed")

def write_results(results):
    # Write the results to a json file
    with open("results/results.json", "w") as f:
        json.dump(results, f, indent=4)
    
    # Write the results to a markdown file
    with open('results/results_pretty.md', "w") as f:
        for key in results:
            f.write(f'# Prompt {key}:\n\n')
            for index, item in enumerate(results[key]):
                f.write(f'## Request:\n')
                f.write(item['request'])
                f.write('\n\n')
                f.write(f'### Distance:\n')
                f.write(str(item['distance']))
                f.write('\n\n')
                f.write(f'### Diff {index + 1}:\n')
                if item['diff'] == '':
                    f.write('Identical')
                else:
                    f.write('```\n')
                    f.write(item['diff'])
                    f.write('\n```')
                f.write('\n\n')