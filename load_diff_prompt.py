import json

input_file = "diff_system_prompt.txt"
output_file = "diff_system_prompts.json"

# Load the existing prompts (if any) from the output file
try:
    with open(output_file, "r") as f:
        prompts = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    prompts = []

# Read the text from the input file as a single prompt
with open(input_file, "r") as f:
    prompt_text = f.read().strip()

# Append the new prompt to the existing list of prompts
prompts.append(prompt_text)

# Write the updated list of prompts to the output file without a trailing comma
with open(output_file, "w") as f:
    json.dump(prompts, f, ensure_ascii=False, separators=(',', ': '), indent=4)
    f.write("\n")  # add a newline character for readability


print("Done!")