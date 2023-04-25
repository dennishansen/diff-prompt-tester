import pandas as pd
import matplotlib.pyplot as plt
import json

def run():
    #load the results from the json file
    with open("results/results.json", "r") as f:
        results = json.load(f)

    df = pd.DataFrame(results)
    average_distances = df.groupby(['diff_prompt_name', 'parser_name'])['distance'].mean().reset_index()

    fig, ax = plt.subplots()

    # Create a bar chart with prompt-parser pairs on the x-axis and average distances on the y-axis
    ax.bar(average_distances['diff_prompt_name'] + ' - ' + average_distances['parser_name'], average_distances['distance'])

    ax.set_xlabel('Prompt-Parser Pairs')
    ax.set_ylabel('Average Distance')
    ax.set_title('Average Distance for Different Prompt-Parser Pairs')

    plt.xticks(rotation=45)

    # Save the plot as an image
    plt.savefig('results/average_distances.png', bbox_inches='tight')

    with open('results/results.html', "w") as f:
        # Sort results by diff prompt, then request, then parser
        results = sorted(results, key=lambda result: (result['diff_prompt_name'], result['request'], result['parser_name']))

        f.write("<html><head><style>table {border-collapse: collapse;} .header {position: sticky; top:0px;  } th, td {border: 1px solid black; padding: 8px;} th {background-color: #f2f2f2;} td > pre {max-width: 400px; overflow-wrap: break-word; white-space: pre-wrap;} .message {max-width: 150px}</style></head><body>")
        f.write("<h1>Average Distances</h1>")
        f.write("<img src=\"average_distances.png\" alt=\"Average distances for different prompt-parser pairs\" />")
        f.write("<h1>Results</h1>")
        f.write("<table><tr class=\"header\"><th>Diff Prompt</th><th>Parser</th><th>Distance</th><th>Request</th><th>Response Message</th><th>Diff Response</th><th>Diffed Files</th><th>Correct Files</th><th>Diff with Correct</th></tr>")
        
        for result in results:
            f.write("<tr>")
            f.write(f"<td>{result['diff_prompt_name']}</td>")
            f.write(f"<td>{result['parser_name']}</td>")
            f.write(f"<td>{result['distance']}</td>")
            f.write(f"<td class=\"message\">{result['request']}</td>")
            f.write(f"<td class=\"message\">{result['diff_message']}</td>")
            f.write(f"<td><pre>{result['diff_response_raw']}</pre></td>")
            f.write(f"<td><pre>{result['diffed_files']}</pre></td>")
            f.write(f"<td><pre>{result['correct_files']}</pre></td>")
            f.write(f"<td><pre>{result['diff_with_corrected']}</pre></td>")
            f.write("</tr>")
        
        f.write("</table>")
        f.write("</body></html>")