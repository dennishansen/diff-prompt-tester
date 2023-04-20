import json

def run():
    input_file = "parsers/parser.py"
    output_file = "parsers/parsers.json"

    # Load the existing parser (if any) from the output file
    try:
        with open(output_file, "r") as f:
            parser = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        parser = []

    # Read the text from the input file as a single prompt
    with open(input_file, "r") as f:
        prompt = f.read().strip()

    # Create a unique id
    id = len(parser)

    # Append the new prompt to the existing list of parser
    parser.append({ "id": id, "prompt": prompt })

    # Write the updated list of parser to the output file without a trailing comma
    with open(output_file, "w") as f:
        json.dump(parser, f, ensure_ascii=False, separators=(',', ': '), indent=4)
        f.write("\n")  # add a newline character for readability

    print("Completed")