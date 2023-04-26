import openai
import difflib
import os
import json
import Levenshtein
import concurrent.futures
from tqdm import tqdm
from dotenv import load_dotenv
from source.debug import debug
from source.deterministic_hash import deterministic_hash
from results import write_html_results

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
    tests_with_error = []

    # Flatten perumtations of prompts, requests, and parsers into experiements
    for prompt in diff_prompts:
        for parser in prompt["parsers"]:
            for request in requests:
                test = {
                    # Create id that is a hash of the prompt, parser, and request
                     "id": deterministic_hash(f"{prompt['prompt']}{parser['parser']}{request}"),
                    "prompt": prompt,
                    "parser": parser,
                    "request": request
                }
                tests.append(test)
    
    # Load existing test results
    with open("results/results.json", "r") as f:
        old_results = json.load(f)

    # Add results for tests that have already been run in the old results
    test_ids_ran = [result["id"] for result in old_results]
    tests_to_skip = [test for test in tests if test["id"] in test_ids_ran]
    for test in tests_to_skip:
        results.append([result for result in old_results if result["id"] == test["id"]][0])

    # Queue up everything else to run
    tests_to_run = [test for test in tests if test["id"] not in test_ids_ran]

    # Print whats being skipped and whats being run
    print(f"Skipping {len(tests_to_skip)} tests")
    print(f"Running {len(tests_to_run)} tests")

    # Overwrite the results file with the new results based on the new test set
    write_json_results(results)

    # Get the file contents
    file_contents = get_file_contents(files)
    debug(f"File Contents:\n{json.dumps(file_contents, indent=4)}")


    # Run tests
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a function that processes a test with the required arguments
        process_test_partial = lambda test: process_test(test, file_contents)
        
        # Run tests in parallel
        for result, error in tqdm(executor.map(process_test_partial, tests_to_run), total=len(tests_to_run), desc="Tests", unit="test"):
            if result is not None:
                results.append(result)
                write_json_results(results)
            else:
                tests_with_error.append(error)

    write_html_results.run()

    # Print tests that ran
    if len(tests_to_run) - len(tests_with_error) > 0:
        print(f"Successfully ran {len(results)} tests")
    else:
        print("No tests were run")
    
    # Print tests with errors
    if len(tests_with_error) > 0:
        print(f"{len(tests_with_error)} tests failed to run")
        # Write the tests with errors to a file
        with open("results/errors.txt", "w") as f:
            for test_with_error in tests_with_error:
                error_string = f"Error: {test_with_error['error']}\nPrompt: {test_with_error['prompt_name']}\nParser: {test_with_error['parser_name']}\nRequest: {test_with_error['request']}\nDiff Response:\n\n{test_with_error['diff_response']}\n\n\n"
                f.write(error_string)


def write_json_results(results):
    with open("results/results.json", "w") as f:
        json.dump(results, f, indent=4)


def process_test(test, file_contents):
    prompt = test["prompt"]
    parser = test["parser"]
    request = test["request"]
    id = test["id"]
    
    # Get the prompts
    user_prompt = get_user_prompt(request)

    # Set the initial messages
    messages = [{"role": "system", "content": prompt["prompt"]}, {"role": "user", "content": user_prompt}]

    # Get the files from the diff system prompt
    diff_response_raw = call_gpt_agent(messages)
    debug(f"Diff Response:\n{diff_response_raw}")

    # Get the functions from the parser
    parser_string = parser["parser"]

    # Store the functions string in a JSON object
    parser_json = {"functions": parser_string}

    # Convert the JSON object back into a string
    functions_string_from_json = json.loads(json.dumps(parser_json))["functions"]


    try:
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
            "id": id,
            "diff_prompt_name": prompt["name"],
            "parser_name": parser["name"],
            "request": request,
            "distance": distance,
            "correct_files": correct_files_string,
            "correct_message": correct_message,
            "diff_response_raw": diff_raw,
            "diff_message": diff_message,
            "diffed_files": diffed_files_string,
            "diff_with_corrected": diff_with_corrected if diff_with_corrected else "None"
        }

        return result, None
    except Exception as e:
        error = {
            "error": str(e),
            "prompt_name": prompt["name"],
            "parser_name": parser["name"],
            "request": request,
            "diff_response": diff_response_raw,
        }
        return None, error