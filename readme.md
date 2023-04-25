
# Diff Prompt tester
This project is intended to drive the development of a prompt/parser that enables GPTs/AutoGPTs/LLMs make changes to files/code in a compact diff format instead of overwriting entire files which severely clog the context window, limited the scale of projects LLMs can work on. This project seeks to acheive this by testing how similar the resulting files of each diff prompt+parser combination is to the output of prompts that return the entire file. This takes place by first asking GPT for code changes using the diff format, and then in the same thread, asking for the complete files. The resulting files's similarity is then compared using the Levenshtein distance. The project also consists of several scripts that perform specific tasks, such as running tests, loading and updating parsers, and generating an HTML file with the results.

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
This script tests each prompt/parser combinations defined in the `prompts/diff_prompts` file against a series of requests defined in the `requests/requests.json` file on how accurately it can make changes to the files in the `test-files` directory. It calculates the accuracy of each parser/prompt combination by comparing the resulting files with 'correct' response, recording the results to the `results/*` directory as a JSON file and an HTML report. Tests that have already run are skipped and tests that encounter errors are written to `results/errors.txt`.

Command: python main.py test

### load_prompt
This script loads a new prompt from the `prompts/diff_prompts.txt` into the `prompts/diff_prompts.json` file to queue for testing. This must be done before loading a related parser.

Command: python main.py load_prompt

### load_parser
This script loads the `parsers/parser.py` file into the `parsers/diff_prompts.json` file to queue for tests.

Command: python main.py load_parser

### test_parser
This script runs test the `parsers/parser.py` test against the `parsers/example_response.txt` for quick debugging.

Command: python main.py test_parser

### print_request_prompt
This script prints the request prompt that is sent to GPT to generate diff changes for. This is helpful to get a prompt to throw in the OpenAI playground for quick debugging

Command: python main.py print_prompt

### write_html
This script reads the `results/results.json` file and re-writes the HTML results. This makes testing new HTML format quick.

Command: python main.py write_html


## Contributing
- Add your parsers and see if you can beat the benchmark. Pull request your benchmark in
- Would love to improve prompt/parser scoring. Currently, subsequent test runs vary a decent amount in terms of scores. For example, it could make to manually cache some 'correct' files.
- Parelellizing tests!