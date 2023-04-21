import os
import json
from source.test import get_file_contents
from parsers import parser

# Get all files in the test_files directory
test_file_path = "test_files"
files = os.listdir(test_file_path)
file_contents = get_file_contents(files)

diff_response_raw = """MESSAGE:I have implemented a multiply function using the add function in the utils.py file and updated the main.py file to use the new function.	
EDIT_FILE:test_files/utils.py
HUNK_START:1
def add_numbers(num1, num2):
    return num1 + num2
+def multiply_numbers(num1, num2):
+    result = 0
+    for _ in range(num2):
+        result = add_numbers(result, num1)
+    return result

EDIT_FILE:test_files/main.py
HUNK_START:1
from utils import add_numbers
+from utils import multiply_numbers
+
num1 = 5
num2 = 10
-result = add_numbers(num1, num2)
+result = multiply_numbers(num1, num2)
-print(f"The sum of \{num1\} and \{num2\} is \{result\}.")
+print(f"The product of \{num1\} and \{num2\} is \{result\}.")"""

def run():

    print(file_contents)

    diffed_files, diff_message, diff_raw = parser.parse(diff_response_raw, file_contents)

    print('\n\nOriginal Files:\n')
    for file in file_contents:
        print(f"PATH:{file['filePath']}\n{file['content']}\n")
    print(f"\nDiff:\n\n{diff_raw}\n")
    print(f"\nDiffed Files:\n")
    for file in diffed_files:
        print(f"PATH:{file['filePath']}\n{file['content']}\n")

def test_json():
    # load prompts JSON
    with open("prompts/diff_prompts.json", "r") as f:
        prompts = json.load(f)
    
    # Get the first prompt
    parser_string = prompts[0]["parsers"][0]["parser"]

    # Store the functions string in a JSON object
    parser_json = {"functions": parser_string}

    # Convert the JSON object back into a string
    functions_string_from_json = json.loads(json.dumps(parser_json))["functions"]

    # Define the functions using exec()
    exec(functions_string_from_json, globals())

    # Call the functions
    diffed_files, diff_message, diff_raw = parse(diff_response_raw, file_contents)

    print('\n\nOriginal Files:\n')
    for file in file_contents:
        print(f"PATH:{file['filePath']}\n{file['content']}\n")
    print(f"\nDiff:\n\n{diff_raw}\n")
    print(f"\nDiffed Files:\n")
    for file in diffed_files:
        print(f"PATH:{file['filePath']}\n{file['content']}\n")