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

    # Continue to ask for a name until a unique name is given
    while True:
        name = input("Enter a unique name for the diff prompt: ")

        # Check if the name is unique
        if not any(prompt["name"] == name for prompt in diff_prompts):
            break

        print("A diff prompt with that name already exists")

    # Append the new diff_prompt to the existing list of diff prompts
    diff_prompts.append({ "name": name, "prompt": diff_prompt, "parsers": [] })

    # Write the updated list of diff prompts to the output file without a trailing comma
    with open(output_file, "w") as f:
        json.dump(diff_prompts, f, ensure_ascii=False, separators=(',', ': '), indent=4)
        f.write("\n")

    print("Completed")