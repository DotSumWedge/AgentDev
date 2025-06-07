import os
import argparse
from pathlib import Path

# --- Configuration ---
# Add directories or files you want to ignore by default.
# This helps keep the context file clean and focused.
DEFAULT_IGNORE_PATTERNS = [
    '.git',
    '__pycache__',
    'node_modules',
    '.vscode',
    '.idea',
    'dist',
    'build',
    '.DS_Store',
    '*.pyc',
    '*.swp',
    '*.env'
]
# -------------------

def should_ignore(path, ignore_patterns):
    """Check if a file or directory path matches any of the ignore patterns."""
    path_parts = path.parts
    for pattern in ignore_patterns:
        # Check for direct name match in any part of the path (e.g., '.git')
        if pattern in path_parts:
            return True
        # Check for glob patterns (e.g., '*.pyc')
        if any(part.endswith(pattern.strip('*')) for part in path_parts if pattern.startswith('*')):
            return True
    return False


def create_context_file(directory_path, output_file, use_ignore_list=True):
    """
    Walks through a directory, reads all non-ignored files, and writes their
    paths and contents to a single Markdown file.
    """
    input_path = Path(directory_path)
    if not input_path.is_dir():
        print(f"Error: The path '{directory_path}' is not a valid directory.")
        return

    ignore_list = DEFAULT_IGNORE_PATTERNS if use_ignore_list else []
    
    try:
        with open(output_file, 'w', encoding='utf-8', errors='ignore') as md_file:
            md_file.write(f"# Context for Directory: `{input_path.resolve()}`\n\n")

            # Using Path.rglob for a more Pythonic way to traverse files
            for file_path in sorted(input_path.rglob('*')):
                if file_path.is_file():
                    relative_path = file_path.relative_to(input_path)
                    
                    if use_ignore_list and should_ignore(relative_path, ignore_list):
                        print(f"Ignoring: {relative_path}")
                        continue

                    print(f"Processing: {relative_path}")
                    
                    md_file.write(f"---\n\n")
                    md_file.write(f"**File:** `{relative_path}`\n\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                            content = f_in.read()
                            # Use a language hint based on file extension for better syntax highlighting
                            lang = file_path.suffix.lstrip('.')
                            md_file.write(f"```{lang}\n")
                            md_file.write(content.strip())
                            md_file.write(f"\n```\n\n")
                    except Exception:
                        # This will catch binary files or other read errors
                        md_file.write("```\n")
                        md_file.write("[Could not read file content (e.g., binary file, permission error)]")
                        md_file.write("\n```\n\n")

        print(f"\n✅ Success! All context has been compiled into '{output_file}'")

    except IOError as e:
        print(f"Error: Could not write to the file '{output_file}'. Reason: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Compile all file contents in a directory into a single Markdown file for context.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'directory_path',
        help="The path to the directory you want to process."
    )
    parser.add_argument(
        '-o', '--output',
        default='directory_context.md',
        help="The name of the output Markdown file. (default: directory_context.md)"
    )
    parser.add_argument(
        '--no-ignore',
        action='store_false',
        dest='use_ignore_list',
        help="Include all files, even those in the default ignore list (like .git, node_modules, etc.)."
    )
    
    args = parser.parse_args()
    
    create_context_file(args.directory_path, args.output, args.use_ignore_list)

if __name__ == '__main__':
    main()