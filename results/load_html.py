import json
from source.test import write_html_results

def run():
    #load the results from the json file
    with open("results/results.json", "r") as f:
        results = json.load(f)

    write_html_results(results)

    print("Completed")