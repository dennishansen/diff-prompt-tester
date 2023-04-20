import argparse
import sys
import os

# Add the my_project directory to sys.path
project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Import scripts based on command-line arguments
def run_script(script_name):
    if script_name == 'test':
        from source import test
        test.run()
    elif script_name == 'load_parser':
        from parsers import load
        load.run()
    elif script_name == 'test_parser':
        from parsers import test
        test.run()
    elif script_name == 'test_json_parser':
        from parsers import test
        test.test_json()
    elif script_name == 'print_prompt':
        from scripts import print_prompt
        print_prompt.run()
    elif script_name == 'print_files':
        from scripts import print_files
        print_files.run()
    elif script_name == 'load_prompt':
        from prompts import load
        load.run()
    elif script_name == 'load_html':
        from results import load_html
        load_html.run()
    else:
        print(f"Unknown script: {script_name}")
        sys.exit(1)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run a script from the my_project/scripts directory.")
parser.add_argument("script_name", help="Name of the script to run (e.g., 'script1', 'script2')")
args = parser.parse_args()

# Run the specified script
run_script(args.script_name)
