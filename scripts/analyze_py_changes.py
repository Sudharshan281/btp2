import ast
import os
import sys
import subprocess
from typing import List, Dict, Any, Set
from github import Github

def get_github_token():
    return os.environ.get('GITHUB_TOKEN')

def get_repo_name():
    return os.environ.get('GITHUB_REPOSITORY')

def get_file_content(file_path: str) -> str:
    """Get the current content of a file."""
    try:
        # First try to read directly from filesystem
        if os.path.exists(file_path):
            print(f"File exists locally, reading directly")
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"Error reading file directly: {e}")
    
    # Fallback to git show
    try:
        print(f"Attempting to get file content using git show")
        result = subprocess.run(['git', 'show', f'HEAD:{file_path}'], 
                              capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting file content: {e}")
        return None

def get_previous_content(file_path: str) -> str:
    """Get the previous version of a file from git."""
    try:
        print(f"Attempting to get previous version of: {file_path}")
        result = subprocess.run(['git', 'show', f'HEAD^:{file_path}'], 
                              capture_output=True, text=True, check=True)
        print("Successfully retrieved previous version from git")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting previous version: {e}")
        return None

def extract_api_elements(content: str) -> Set[str]:
    """Extract API elements (functions, classes) from Python code."""
    if not content:
        return set()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print("Error parsing Python code")
        return set()
    
    elements = set()
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            elements.add(node.name)
    
    return elements

def find_changes(old_elements: Set[str], new_elements: Set[str]) -> List[Dict[str, Any]]:
    """Find changes between old and new API elements."""
    changes = []
    
    # Find added elements
    old_names = set(old_elements)
    for element in new_elements:
        if element not in old_names:
            changes.append({
                'type': 'added',
                'name': element,
                'description': f"New API element"
            })
    
    # Find removed elements
    new_names = set(new_elements)
    for element in old_names:
        if element not in new_names:
            changes.append({
                'type': 'removed',
                'name': element,
                'description': f"Removed API element"
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

def create_github_issue(title: str, body: str) -> None:
    """Create a GitHub issue with the specified title and body."""
    token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('GITHUB_REPOSITORY')
    
    if not token or not repo_name:
        print("Missing GitHub token or repository name")
        print("Would create issue with the following content:")
        print(f"Title: {title}")
        print(f"Body:\n{body}")
        return
    
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        issue = repo.create_issue(title=title, body=body)
        print(f"Created issue #{issue.number}: {title}")
    except Exception as e:
        print(f"Error creating GitHub issue: {e}")
        # Print the issue content that would have been created
        print("Would have created issue with:")
        print(f"Title: {title}")
        print(f"Body:\n{body}")

def analyze_changes(file_path: str) -> None:
    """Analyze changes between current and previous versions of a file."""
    print(f"Analyzing changes for {file_path}")
    
    try:
        current_content = get_file_content(file_path)
        if not current_content:
            error_msg = f"Could not read current content of {file_path}"
            print(error_msg)
            create_github_issue(
                f"Error: Failed to analyze {os.path.basename(file_path)}",
                f"Error message: {error_msg}"
            )
            return
        
        previous_content = get_previous_content(file_path)
        if not previous_content:
            print(f"No previous version found for {file_path}, treating as new file")
            current_elements = extract_api_elements(current_content)
            if current_elements:
                title = f"Documentation Needed: New File {os.path.basename(file_path)}"
                body = "New file detected with the following API elements:\n"
                body += "\n".join(f"- {elem}" for elem in sorted(current_elements))
                create_github_issue(title, body)
            return
        
        current_elements = extract_api_elements(current_content)
        previous_elements = extract_api_elements(previous_content)
        
        added = current_elements - previous_elements
        removed = previous_elements - current_elements
        
        if not (added or removed):
            print("No API changes detected")
            return
        
        print("Changes detected:")
        if added:
            print("Added:", ", ".join(sorted(added)))
        if removed:
            print("Removed:", ", ".join(sorted(removed)))
        
        title = f"Documentation Update: Changes in {os.path.basename(file_path)}"
        body = "The following API changes were detected:\n\n"
        if added:
            body += "Added:\n" + "\n".join(f"- {elem}" for elem in sorted(added)) + "\n\n"
        if removed:
            body += "Removed:\n" + "\n".join(f"- {elem}" for elem in sorted(removed))
        
        create_github_issue(title, body)
        
    except Exception as e:
        error_msg = f"Error analyzing changes: {str(e)}"
        print(error_msg)
        create_github_issue(
            f"Error: Failed to analyze {os.path.basename(file_path)}",
            f"An error occurred while analyzing changes:\n\n```\n{error_msg}\n```"
        )
        raise  # Re-raise to ensure workflow fails

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_py_changes.py <file_path>")
        sys.exit(1)
    
    analyze_changes(sys.argv[1])
