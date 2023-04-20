import os
from dotenv import load_dotenv

def run():
    test_file_path = "test_files"

    files = os.listdir(test_file_path)

    # Get unformarted files
    def get_file_contents():
        file_contents = []

        # Loop through each file and format its contents
        for file in files:
            with open(os.path.join(test_file_path, file), "r") as f:
                content = f.read()
                
                file_contents.append({
                    "filePath": os.path.relpath(os.path.join(test_file_path, file)),
                    "content": content
                })

        
        return file_contents

    print(get_file_contents())