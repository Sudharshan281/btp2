import argparse
import ast
import subprocess
import sys
from pathlib import Path

def get_definitions(node):
    """Extracts top-level function and class names from an AST node."""
    definitions = set()
    if node is None:
        return definitions
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions.add(item.name)
    return definitions

def get_file_content_at_ref(git_ref, file_path):
    """Gets the content of a file at a specific git reference."""
    try:
        # Use 'git show' which handles paths relative to repo root
        result = subprocess.run(
            ['git', 'show', f'{git_ref}:{file_path}'],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Handle cases where the file might not exist at that ref (e.g., added/deleted)
        # Or other git errors
        print(f"Error getting content for {file_path} at {git_ref}: {e.stderr}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error getting content for {file_path} at {git_ref}: {e}", file=sys.stderr)
        return None


def parse_code(code_content, file_path):
    """Parses Python code content into an AST."""
    if code_content is None:
        return None
    try:
        return ast.parse(code_content)
    except SyntaxError as e:
        print(f"SyntaxError parsing {file_path}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error parsing {file_path}: {e}", file=sys.stderr)
        return None


def analyze_changes(base_ref, head_ref, file_paths):
    """Analyzes changes between base and head for given files."""
    added_defs = {}
    removed_defs = {}

    for file_path in file_paths:
        print(f"Analyzing file: {file_path}", file=sys.stderr)

        base_content = get_file_content_at_ref(base_ref, file_path)
        head_content = get_file_content_at_ref(head_ref, file_path)

        # Handle file addition/deletion
        if base_content is None and head_content is None:
            print(f"Skipping {file_path}: Could not retrieve content at either ref.", file=sys.stderr)
            continue
        elif base_content is None: # File added
             print(f"File added: {file_path}", file=sys.stderr)
             head_ast = parse_code(head_content, f"{file_path} (HEAD)")
             if head_ast:
                 current_defs = get_definitions(head_ast)
                 if current_defs:
                     added_defs[file_path] = list(current_defs)
             continue # No need to compare if it's a new file
        elif head_content is None: # File removed
            print(f"File removed: {file_path}", file=sys.stderr)
            base_ast = parse_code(base_content, f"{file_path} (BASE)")
            if base_ast:
                original_defs = get_definitions(base_ast)
                if original_defs:
                    removed_defs[file_path] = list(original_defs)
            continue # No need to compare if file is removed

        # File modified
        print(f"File modified: {file_path}", file=sys.stderr)
        base_ast = parse_code(base_content, f"{file_path} (BASE)")
        head_ast = parse_code(head_content, f"{file_path} (HEAD)")

        original_defs = get_definitions(base_ast)
        current_defs = get_definitions(head_ast)

        added = current_defs - original_defs
        removed = original_defs - current_defs

        if added:
            added_defs[file_path] = list(added)
        if removed:
            removed_defs[file_path] = list(removed)

    return added_defs, removed_defs

def format_report(added_defs, removed_defs, head_ref):
    """Formats the analysis results into a Markdown report."""
    report_lines = [f"### API Change Report ({head_ref[:7]})"] # Use short SHA

    if not added_defs and not removed_defs:
        report_lines.append("\nNo significant top-level function/class changes detected.")
        return "\n".join(report_lines)

    report_lines.append("\nDetected potential changes:")

    if added_defs:
        report_lines.append("\n**Added Functions/Classes:**")
        for file, defs in added_defs.items():
            for definition in sorted(defs):
                report_lines.append(f"- `+ {definition}` in `{file}`")

    if removed_defs:
        report_lines.append("\n**Removed Functions/Classes:**")
        for file, defs in removed_defs.items():
            for definition in sorted(defs):
                report_lines.append(f"- `- {definition}` in `{file}`")

    return "\n".join(report_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Python code changes using AST.")
    parser.add_argument("--base-ref", required=True, help="Base Git reference (e.g., commit SHA)")
    parser.add_argument("--head-ref", required=True, help="Head Git reference (e.g., commit SHA)")
    parser.add_argument("--files", required=True, help="Space-separated list of changed Python files")
    # Future enhancement: Add --api-dirs to filter files further if needed

    args = parser.parse_args()

    # Split the files string into a list, handling potential empty input
    changed_files = [f for f in args.files.split() if f.endswith('.py')]

    if not changed_files:
        print("No Python files provided for analysis.", file=sys.stderr)
        # Output an empty report content so the next step knows nothing happened
        print(f"::set-output name=report_content::")
        sys.exit(0)

    print(f"Starting analysis between {args.base_ref} and {args.head_ref}", file=sys.stderr)
    print(f"Files to analyze: {changed_files}", file=sys.stderr)

    added, removed = analyze_changes(args.base_ref, args.head_ref, changed_files)

    report = format_report(added, removed, args.head_ref)

    print("\n--- Generated Report ---", file=sys.stderr)
    print(report, file=sys.stderr)
    print("--- End Report ---", file=sys.stderr)


    # Output the report for the GitHub Action step
    # Escape special characters for multiline output in GitHub Actions
    report_escaped = report.replace('%', '%25').replace('\n', '%0A').replace('\r', '%0D')
    print(f"::set-output name=report_content::{report_escaped}")

    # Create the actual report file to be committed by create-pull-request action
    report_path = Path("docs/api_change_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    print(f"Report saved to {report_path}", file=sys.stderr)
