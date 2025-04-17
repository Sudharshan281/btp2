import ast
import difflib
import os
import sys

def parse_ast(file_content):
    """Parse Python code into an Abstract Syntax Tree (AST)."""
    return ast.parse(file_content)

def extract_function_signatures(tree):
    """Extract function signatures from an AST."""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "lineno": node.lineno
            })
    return functions

def compare_asts(old_tree, new_tree):
    """Compare two ASTs and return meaningful differences."""
    old_functions = extract_function_signatures(old_tree)
    new_functions = extract_function_signatures(new_tree)

    added = [f for f in new_functions if f not in old_functions]
    removed = [f for f in old_functions if f not in new_functions]

    return {"added": added, "removed": removed}

def analyze_changes(old_file, new_file):
    """Analyze changes between two versions of a Python file."""
    with open(old_file, 'r') as f:
        old_content = f.read()
    with open(new_file, 'r') as f:
        new_content = f.read()

    old_tree = parse_ast(old_content)
    new_tree = parse_ast(new_content)

    return compare_asts(old_tree, new_tree)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyze_py_changes.py <old_file> <new_file>")
        sys.exit(1)

    old_file = sys.argv[1]
    new_file = sys.argv[2]

    if not os.path.exists(old_file) or not os.path.exists(new_file):
        print("Error: One or both files do not exist.")
        sys.exit(1)

    changes = analyze_changes(old_file, new_file)
    print("Changes detected:")
    print("Added functions:", changes["added"])
    print("Removed functions:", changes["removed"])