import json

def run():
    input_file = "prompts/diff_prompt.txt"
    output_file = "prompts/diff_prompts.json"

    # Load the existing diff_prompts (if any) from the output file
    try:
        with open(output_file, "r") as f:
            diff_prompts = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        diff_prompts = []

    # Read the text from the input file as a single diff_ rompt
    with open(input_file, "r") as f:
        diff_prompt = f.read().strip()

    # Create a unique id
    id = len(diff_prompts)

    # Append the new diff_prompt to the existing list of diff prompts
    diff_prompts.append({ "id": id, "diff_prompt": diff_prompt })

    # Write the updated list of diff prompts to the output file without a trailing comma
    with open(output_file, "w") as f:
        json.dump(diff_prompts, f, ensure_ascii=False, separators=(',', ': '), indent=4)
        f.write("\n")  # add a newline character for readability

    print("Completed")