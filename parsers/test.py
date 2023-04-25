import os
import json
from source.test import get_file_contents
from parsers import parser

# Get all files in the test_files directory
test_file_path = "test_files"
files = os.listdir(test_file_path)
file_contents = get_file_contents(files)

# Load example_response from txt file
with open("parsers/example_response.txt", "r") as f:
    diff_response_raw = f.read()

def run():

    diffed_files, diff_message, diff_raw = parser.parse(diff_response_raw, file_contents)

    print('\n\nOriginal Files:\n')
    for file in file_contents:
        print(f"PATH:{file['filePath']}\n{file['content']}\n")
    print(f"\nDiff:\n\n{diff_raw}\n")
    print(f"\nDiffed Files:\n")
    for file in diffed_files:
        print(f"PATH:{file['filePath']}\n{file['content']}\n")