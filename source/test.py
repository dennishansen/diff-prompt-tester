import openai
import difflib
import os
import json
import Levenshtein
from tqdm import tqdm
from dotenv import load_dotenv
from source.debug import debug

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Get all files in the test_files directory
test_file_path = "test_files"
files = os.listdir(test_file_path)

# Load system prompts, example files, and user requests
with open("prompts/full_file_prompt.txt", "r") as f:
    full_file_prompt = f.read()

with open("prompts/diff_prompts.json", "r") as f:
    diff_prompts = json.load(f)

with open("requests/requests.json", "r") as f:
    requests = json.load(f)

def call_gpt_agent(messages):
    # print(json.dumps(messages, indent=4))
    try: 
        response = openai.ChatCompletion.create(
            model="gpt-4-0314",
            messages=messages,
            temperature=0,
            max_tokens=2048,
        )
        return response.choices[0]['message']['content'].strip()
    except openai.OpenAIError as error:
        print(f"An error occurred while calling the OpenAI API: {error}")
    except Exception as error:
        print(f"An unexpected error occurred: {error}")
    return None

# Get the user prompt with formatted files
def get_user_prompt(request):
    file_contents = []

    # Loop through each file and format its contents
    for file in files:
        with open(os.path.join(test_file_path, file), "r") as f:
            content = f.read()
            formatted_content = "\n".join([f"{i + 1}:{line}" for i, line in enumerate(content.split("\n"))])
            
            file_contents.append({
                "filePath": os.path.relpath(os.path.join(test_file_path, file)),
                "content": f"FILE_START:{os.path.relpath(os.path.join(test_file_path, file))}\n{formatted_content}"
            })

    # Join the formatted code for each file with a newline separator
    formated_files = "\n".join([file["content"] for file in file_contents])
    
    return f"MESSAGE: {request}\n{formated_files}\n"

# Get unformarted files
def get_file_contents(files):
    file_contents = []

    # Loop through each file and format its contents
    for file in files:
        with open(os.path.join(test_file_path, file), "r") as f:
            content = f.read()
            
            file_contents.append({
                "filePath": os.path.relpath(os.path.join(test_file_path, file)),
                "content": content
            })

    return file_contents

def parse_correct_response(response):
    lines = response.split("\n")
    message = lines[0].split("MESSAGE:")[-1].strip()
    content = "\n".join(lines[1:])
    return content, message

def get_diffed_file_string(file_contents):
    output_lines = []

    for file in file_contents:
        output_lines.append(f"PATH:{file['filePath']}")
        output_lines.extend(file["content"].strip().split("\n"))

    return "\n".join(output_lines)

def run():
    results = []
    tests = []

    # Flatten perumtations of prompts, requests, and parsers into experiements
    for prompt in diff_prompts:
        for parser in prompt["parsers"]:
            for request in requests:
                test = {
                    "prompt": prompt,
                    "parser": parser,
                    "request": request
                }
                tests.append(test)

    # Run tests
    for test in tqdm(tests, desc="Tests", unit="test"):
        prompt = test["prompt"]
        parser = test["parser"]
        request = test["request"]
        
        # Get the prompts
        user_prompt = get_user_prompt(request)

        # Set the initial messages
        messages = [{"role": "system", "content": prompt["prompt"]}, {"role": "user", "content": user_prompt}]

        # Get the files from the diff system prompt
        diff_response_raw = call_gpt_agent(messages)
        debug(f"Diff Response:\n{diff_response_raw}")

        file_contents = get_file_contents(files)
        debug(f"File Contents:\n{json.dumps(file_contents, indent=4)}")

        # Get the functions from the parser
        parser_string = parser["parser"]

        # Store the functions string in a JSON object
        parser_json = {"functions": parser_string}

        # Convert the JSON object back into a string
        functions_string_from_json = json.loads(json.dumps(parser_json))["functions"]

        # Load the functions into the namespace
        exec(functions_string_from_json, globals())


        # Parse the diff response
        diffed_files, diff_message, diff_raw = parse(diff_response_raw, file_contents)
        debug(f"Diffed File Contents:\n{json.dumps(diffed_files, indent=4)}")
        
        diffed_files_string = get_diffed_file_string(diffed_files)
        debug(f"Changed File Contents String:\n{diffed_files_string}")


        # Append messages to get the full file prompt
        messages.append({"role": "assistant", "content": diff_response_raw})
        messages.append({"role": "user", "content": full_file_prompt})


        # Get the response from the correct system prompt
        correct_response = call_gpt_agent(messages)
        debug(f"Correct Response: \n{correct_response}")
        
        correct_files_string, correct_message = parse_correct_response(correct_response)
        debug(f"Correct Content String: \n{correct_files_string}")

        # Calculate the Levenshtein distance
        distance = Levenshtein.distance(correct_files_string, diffed_files_string)
        debug(f"Distance:\n{distance}")

        # Calculate diff between the two files
        diff_with_corrected = "\n".join(difflib.unified_diff(correct_files_string.splitlines(), diffed_files_string.splitlines(), lineterm=""))
        debug(f"Diff:\n{diff_with_corrected}")

        # Record the results
        result = {
            "diff_prompt_name": prompt["name"],
            "parser_name": parser["name"],
            "request": request,
            "distance": distance,
            "correct_files": correct_files_string,
            "correct_message": correct_message,
            "diff_response_raw": diff_raw,
            "diff_message": diff_message,
            "diffed_files": diffed_files_string,
            "diff_with_corrected": diff_with_corrected
        }

        results.append(result)

        write_json_results(results)
        write_html_results(results)

def write_json_results(results):
    with open("results/results.json", "w") as f:
        json.dump(results, f, indent=4)

def write_html_results(results):
    with open('results/results.html', "w") as f:
        f.write("<html><head><style>table {border-collapse: collapse;} .header {position: sticky; top:0px;  } th, td {border: 1px solid black; padding: 8px;} th {background-color: #f2f2f2;} td > pre {max-width: 400px; overflow-wrap: break-word; white-space: pre-wrap;} .message {max-width: 150px}</style></head><body>")
        f.write("<table><tr class=\"header\"><th>Diff Prompt</th><th>Parser</th><th>Distance</th><th>Request</th><th>Response Message</th><th>Diff Response</th><th>Diffed Files</th><th>Correct Files</th><th>Diff with Correct</th></tr>")
        
        for result in results:
            f.write("<tr>")
            f.write(f"<td>{result['diff_prompt_name']}</td>")
            f.write(f"<td>{result['parser_name']}</td>")
            f.write(f"<td>{result['distance']}</td>")
            f.write(f"<td class=\"message\">{result['request']}</td>")
            f.write(f"<td class=\"message\">{result['diff_message']}</td>")
            f.write(f"<td><pre>{result['diff_response_raw']}</pre></td>")
            f.write(f"<td><pre>{result['diffed_files']}</pre></td>")
            f.write(f"<td><pre>{result['correct_files']}</pre></td>")
            f.write(f"<td><pre>{result['diff_with_corrected']}</pre></td>")
            f.write("</tr>")
        
        f.write("</table>")
        f.write("</body></html>")