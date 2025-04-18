import ast
import os
import sys
import subprocess
from typing import List, Dict, Any
from github import Github

def get_github_token():
    return os.environ.get('GITHUB_TOKEN')

def get_repo_name():
    return os.environ.get('GITHUB_REPOSITORY')

def get_file_content(file_path: str) -> str:
    try:
        # First try to read the file directly
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read()
        
        # If file doesn't exist locally, try git show
        result = subprocess.run(['git', 'show', f'HEAD:{file_path}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception as e:
        print(f"Error getting file content: {e}")
        return ""

def get_previous_version(file_path: str) -> str:
    try:
        result = subprocess.run(['git', 'show', f'HEAD^:{file_path}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception as e:
        print(f"Error getting previous version: {e}")
        return ""

def extract_api_elements(content: str) -> List[Dict[str, Any]]:
    """Extract API elements (functions and classes) from Python code."""
    tree = ast.parse(content)
    elements = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            elements.append({
                'name': node.name,
                'type': 'function' if isinstance(node, ast.FunctionDef) else 'class',
                'docstring': ast.get_docstring(node),
                'line': node.lineno
            })
    
    return elements

def find_changes(old_elements: List[Dict[str, Any]], new_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find changes between old and new API elements."""
    changes = []
    
    # Find added elements
    old_names = {e['name'] for e in old_elements}
    for element in new_elements:
        if element['name'] not in old_names:
            changes.append({
                'type': 'added',
                'name': element['name'],
                'description': f"New {element['type']} at line {element['line']}"
            })
    
    # Find removed elements
    new_names = {e['name'] for e in new_elements}
    for element in old_elements:
        if element['name'] not in new_names:
            changes.append({
                'type': 'removed',
                'name': element['name'],
                'description': f"Removed {element['type']}"
            })
    
    return changes

def create_readme_issue(py_file: str, changes: List[Dict[str, Any]]):
    """Create a GitHub issue about README updates needed."""
    token = get_github_token()
    repo_name = get_repo_name()
    
    if not token or not repo_name:
        print("Missing GitHub token or repository name")
        print("Would create issue with the following content:")
        print(f"Title: README Update Needed for {os.path.basename(py_file)}")
        print("Changes:")
        for change in changes:
            print(f"- {change['type'].title()}: {change['name']}")
        return
        
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # Format changes for the issue
        changes_text = "\n".join([
            f"- {change['type'].title()}: {change['name']} ({change.get('description', '')})"
            for change in changes
        ])
        
        issue_title = f"README Update Needed for {os.path.basename(py_file)}"
        issue_body = f"""
The following changes in `{py_file}` require updates to the README.md file:

{changes_text}

Please review and update the README.md file to reflect these changes.
"""
        
        repo.create_issue(
            title=issue_title,
            body=issue_body,
            labels=["documentation", "readme"]
        )
        print(f"Created issue for README updates")
    except Exception as e:
        print(f"Error creating issue: {str(e)}")
        print("Would create issue with the following content:")
        print(f"Title: {issue_title}")
        print(f"Body: {issue_body}")

def create_api_failure_issue(py_file: str, error: str):
    """Create a GitHub issue when API key fails."""
    token = get_github_token()
    repo_name = get_repo_name()
    
    if not token or not repo_name:
        print("Missing GitHub token or repository name")
        print("Would create issue with the following content:")
        print(f"Title: API Key Failure for {os.path.basename(py_file)}")
        print(f"Error: {error}")
        return
        
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        issue_title = f"API Key Failure for {os.path.basename(py_file)}"
        issue_body = f"""
The API key failed while processing changes in `{py_file}`.

Error: {error}

Please check the API key configuration and try again.
"""
        
        repo.create_issue(
            title=issue_title,
            body=issue_body,
            labels=["bug", "api"]
        )
        print(f"Created issue for API key failure")
    except Exception as e:
        print(f"Error creating issue: {str(e)}")
        print("Would create issue with the following content:")
        print(f"Title: {issue_title}")
        print(f"Body: {issue_body}")

def analyze_changes(file_path: str):
    """Analyze changes in a Python file and check if README needs updates."""
    print(f"Analyzing changes for {file_path}")
    
    try:
        # Get file contents
        current_content = get_file_content(file_path)
        previous_content = get_previous_version(file_path)
        
        if not current_content:
            error_msg = f"Could not get current content for {file_path}"
            print(error_msg)
            create_api_failure_issue(file_path, error_msg)
            return
            
        # Extract API elements from both versions
        current_elements = extract_api_elements(current_content)
        previous_elements = extract_api_elements(previous_content) if previous_content else []
        
        # Find changes
        changes = find_changes(previous_elements, current_elements)
        
        if not changes:
            print("No changes detected")
            return
            
        print(f"Detected {len(changes)} changes:")
        for change in changes:
            print(f"- {change['type']}: {change['name']}")
        
        # Create issue for the changes
        create_readme_issue(file_path, changes)
        
    except Exception as e:
        error_msg = f"Error analyzing changes: {str(e)}"
        print(error_msg)
        create_api_failure_issue(file_path, error_msg)
        raise  # Re-raise the exception to ensure the workflow fails

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_py_changes.py <file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    try:
        analyze_changes(file_path)
    except Exception as e:
        print(f"Error in main: {str(e)}")
        create_api_failure_issue(file_path, str(e))
        sys.exit(1)
