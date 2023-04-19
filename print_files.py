import openai
import os
import json
import Levenshtein
from dotenv import load_dotenv

example_file_path = "example_files"

files = os.listdir(example_file_path)

# Get unformarted files
def get_file_contents():
    file_contents = []

    # Loop through each file and format its contents
    for file in files:
        with open(os.path.join(example_file_path, file), "r") as f:
            content = f.read()
            
            file_contents.append({
                "filePath": os.path.relpath(os.path.join(example_file_path, file)),
                "content": content
            })

    
    return file_contents

print(get_file_contents())