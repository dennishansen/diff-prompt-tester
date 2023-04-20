from source.main import get_user_prompt
# import json

def run():
    # with open("../data/example_requests.json", "r") as f:
        # example_requests = json.load(f)

    print(get_user_prompt(input("Enter a prompt: ")))