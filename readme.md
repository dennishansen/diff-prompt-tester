# Diff Prompt tester
This project is intended to drive the development of a prompt/parser that enables GPT to make changes file/code in a compact diff format instead of overwriting entire files. It does this by enables the comparison of how accurately different prompts/parser combinations make file changes as compared to overwriting the entire file. Each prompt/parser is tested against a set of reqeusts and the output files are compared using a leventein distance to a request for the entire. This request for the entire file is requested in the same message thread after the diff is requested. The project consists of several scripts that perform specific tasks, such as running tests, loading and updating parsers, and generating an HTML file with the results.

## Installation
Clone the repository.
Install the required packages using the following command:
```
pip install -r requirements.txt
```

## Usage
To run a specific script, use the following command:
```
python main.py <script_name>
```
Replace <script_name> with the name of the script you want to run. Below is a list of available scripts and their descriptions.

## Scripts

### test
This script tests each prompt/parser combinations defined in the `prompts/diff_prompts` file against a series of requests defined in the `requests/requests.json` file. It calculates the accuracy of each parser/prompt combination by comparing the output with the correct response, records the results to the `results/` directory as a JSON file and an HTML report. An errors.txt file is generated in the results folder to aid debugging.

Command: python main.py test

### load_parser
This script updates a specific parser in the "parsers/diff_prompts.json" file.

Command: python main.py load_parser

### test_parser
This script runs tests on a specific parser and prints the results.

Command: python main.py test_parser

### test_json_parser
This script tests the JSON functionality of a specific parser and prints the results.

Command: python main.py test_json_parser

### print_prompt
This script prints the prompt associated with a specific parser.

Command: python main.py print_prompt

### print_files
This script prints the test files' contents.

Command: python main.py print_files

### load_prompt
This script loads a new prompt into the "prompts/diff_prompts.json" file.

Command: python main.py load_prompt

### write_html
This script reads the results from a JSON file, calculates the average distances for each prompt-parser pair, creates a bar chart, and writes an HTML file with the results.

Command: python main.py write_html


## Contributing
- Add your parsers and see if you can beat the benchmark. Pull request your benchmark in
- Would love to improve prompt/parser scoring. For example, it could make to manually cache some 'correct' files.