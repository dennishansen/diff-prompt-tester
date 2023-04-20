import json
from source.debug import debug

def get_changes(response_string):
    lines = response_string.strip().split("\n")
    message = lines.pop(0).split(":")[1].strip()
    diff_raw = "\n".join(lines)
    changes = []

    current_file = None
    current_hunk = {}

    for line in lines:
        if line.startswith("EDIT_FILE"):
            if current_file:
                if current_hunk:
                    current_file["hunks"].append(current_hunk)
                    current_hunk = {}
                changes.append(current_file)
            current_file = {"filePath": line.split(":")[1].strip(), "hunks": []}
        elif line.startswith("HUNK_START"):
            if current_hunk:
                current_file["hunks"].append(current_hunk)
            current_hunk = {"hunkStart": int(line.split(":")[1]), "lines": []}
        elif line.startswith("-"):
            if current_hunk:
                current_hunk["lines"].append({"type": "delete", "content": line[1:]})
        elif line.startswith("+"):
            if current_hunk:
                current_hunk["lines"].append({"type": "add", "content": line[1:]})
        else:
            if current_hunk:
                current_hunk["lines"].append({"type": "context", "content": line})

    if current_hunk and current_hunk["lines"]:
        current_file["hunks"].append(current_hunk)
    if current_file:
        changes.append(current_file)

    return changes, message, diff_raw

def apply_diff(file_contents, changes):
    new_file_contents = []
    for file in file_contents:
        file_path = file["filePath"]
        file_content = file["content"]
        file_changes = next(c for c in changes if c["filePath"] == file_path)
        original_lines = file_content.split("\n")
        new_lines = []
        original_line_index = 0

        for hunk in file_changes["hunks"]:
            # Add unchanged lines before the current hunk
            while original_line_index < hunk["hunkStart"] - 1:
                new_lines.append(original_lines[original_line_index])
                original_line_index += 1

            for line in hunk["lines"]:
                if line["type"] == "delete":
                    original_line_index += 1
                elif line["type"] == "add":
                    new_lines.append(line["content"])
                else:
                    if original_line_index < len(original_lines):
                        new_lines.append(original_lines[original_line_index])
                    original_line_index += 1

        # Add remaining unchanged lines after the last hunk
        while original_line_index < len(original_lines):
            new_lines.append(original_lines[original_line_index])
            original_line_index += 1

        new_content = "\n".join(new_lines)
        new_file_contents.append({"filePath": file_path, "content": new_content})
    return new_file_contents

def parse(response, file_contents):
    changes, message, diff_raw = get_changes(response)
    debug(f"Diff Changes:\n{json.dumps(changes, indent=4)}")

    diffed_files = apply_diff(file_contents, changes)
    debug(f"Diffed File Contents:\n{json.dumps(diffed_files, indent=4)}")

    return diffed_files, message, diff_raw