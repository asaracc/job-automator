"""
scripts/map_project.py
Utility to generate a visual map of the project structure.
This script walks through the project directory, captures the folder/file hierarchy, and extracts
comments from the first line of code files to create an annotated tree view.
The output is then injected into the README.md under a specific section for easy reference.
"""
import os
import re


def generate_map():
    # --- Configuration ---
    root_dir_name = os.path.basename(os.getcwd())
    # Folders to ignore for a clean map
    ignore = {
        '.git',
        '__pycache__',
        'zzz_output',
        '.venv',
        'venv',
        '.vscode',
        'assets',
        'playwright_data'
    }

    raw_structure = []
    max_label_length = 0

    # --- Step 1: Collect Data ---
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ignore]
        rel_path = os.path.relpath(root, '.')
        level = 0 if rel_path == '.' else rel_path.count(os.sep) + 1

        # Directory Label
        folder_display = f"{os.path.basename(root)}/" if rel_path != '.' else f"{root_dir_name}/"
        indent = "│   " * (level - 1) + ("├── " if level > 0 else "")
        dir_label = f"{indent}{folder_display}"
        raw_structure.append({'label': dir_label, 'comment': '', 'is_dir': True})
        max_label_length = max(max_label_length, len(dir_label))

        # File Labels
        sub_indent = "│   " * level + "├── "
        for f in sorted(files):
            if f.endswith(('.pyc', '.pyo')) or f in ['map_project.py', 'setup_project.py']:
                continue

            file_path = os.path.join(root, f)
            comment = ""
            try:
                with open(file_path, 'r', encoding='utf-8') as src:
                    first_line = src.readline().strip()
                    if first_line.startswith(('#', '//')):
                        comment = first_line.lstrip('#/ ').strip()
            except (IOError, OSError, UnicodeDecodeError):
                # Capturamos apenas erros de arquivo ou leitura
                pass

            file_label = f"{sub_indent}{f}"
            raw_structure.append({'label': file_label, 'comment': comment, 'is_dir': False})
            max_label_length = max(max_label_length, len(file_label))

    # --- Step 2: Build Aligned String ---
    tree_lines = []
    for item in raw_structure:
        if item['comment']:
            spacing = " " * (max_label_length - len(item['label']) + 4)
            line = f"{item['label']}{spacing}# {item['comment']}"
        else:
            line = item['label']
        tree_lines.append(line)

    final_tree = "\n".join(tree_lines)
    update_readme_section(final_tree)


def update_readme_section(tree_content):
    file_path = "README.md"
    section_header = "## Project Map"

    # We define exactly what the block looks like
    new_section_block = f"{section_header}\n\n```text\n{tree_content}\n```"

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex logic:
        # Search for '## Project Map' and capture everything after it
        # until the end of the file OR until another section starts (if any)
        pattern = r"## Project Map.*?(?=\n## |$)"

        if re.search(pattern, content, flags=re.DOTALL):
            # If found, replace the old section with the new one
            new_content = re.sub(pattern, new_section_block, content, flags=re.DOTALL)
            print("🔄 Project Map updated in place.")
        else:
            # If the header doesn't exist at all, append it
            new_content = content.rstrip() + "\n\n" + new_section_block
            print("➕ Project Map section created at the bottom.")
    else:
        new_content = f"# Job Automator\n\nAutomated application tool.\n\n{new_section_block}"
        print("📝 New README.md created.")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content.strip() + "\n")


if __name__ == "__main__":
    generate_map()
