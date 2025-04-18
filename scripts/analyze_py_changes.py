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

def extract_api_elements(content: str) -> Dict[str, Dict[str, Any]]:
    """Extract API elements (functions, classes) from Python code with their signatures and docstrings."""
    if not content:
        return {}
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print("Error parsing Python code")
        return {}
    
    elements = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Get function signature
            args = []
            for arg in node.args.args:
                arg_type = ast.unparse(arg.annotation) if arg.annotation else 'Any'
                args.append(f"{arg.arg}: {arg_type}")
            
            # Get return type
            return_type = ast.unparse(node.returns) if node.returns else 'Any'
            
            # Get docstring
            docstring = ast.get_docstring(node) or ""
            
            elements[node.name] = {
                'type': 'function',
                'signature': f"({', '.join(args)}) -> {return_type}",
                'docstring': docstring
            }
        elif isinstance(node, ast.ClassDef):
            # Get class docstring
            docstring = ast.get_docstring(node) or ""
            
            elements[node.name] = {
                'type': 'class',
                'docstring': docstring
            }
    
    return elements

def find_changes(old_elements: Dict[str, Dict[str, Any]], new_elements: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find changes between old and new API elements."""
    changes = []
    
    # Find added elements
    for name, element in new_elements.items():
        if name not in old_elements:
            changes.append({
                'type': 'added',
                'name': name,
                'description': f"New {element['type']} with signature: {element.get('signature', '')}"
            })
    
    # Find removed elements
    for name, element in old_elements.items():
        if name not in new_elements:
            changes.append({
                'type': 'removed',
                'name': name,
                'description': f"Removed {element['type']}"
            })
    
    # Find modified elements
    for name, new_element in new_elements.items():
        if name in old_elements:
            old_element = old_elements[name]
            if new_element['type'] != old_element['type']:
                changes.append({
                    'type': 'modified',
                    'name': name,
                    'description': f"Changed from {old_element['type']} to {new_element['type']}"
                })
            elif new_element.get('signature') != old_element.get('signature'):
                changes.append({
                    'type': 'modified',
                    'name': name,
                    'description': f"Signature changed from {old_element.get('signature', '')} to {new_element.get('signature', '')}"
                })
            elif new_element.get('docstring') != old_element.get('docstring'):
                changes.append({
                    'type': 'modified',
                    'name': name,
                    'description': "Docstring updated"
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
                for name, element in current_elements.items():
                    body += f"- {name} ({element['type']})\n"
                    if element.get('signature'):
                        body += f"  Signature: {element['signature']}\n"
                create_github_issue(title, body)
            return
        
        current_elements = extract_api_elements(current_content)
        previous_elements = extract_api_elements(previous_content)
        
        changes = find_changes(previous_elements, current_elements)
        
        if not changes:
            print("No API changes detected")
            return
        
        print("Changes detected:")
        for change in changes:
            print(f"{change['type'].title()}: {change['name']} - {change['description']}")
        
        title = f"Documentation Update: Changes in {os.path.basename(file_path)}"
        body = "The following API changes were detected:\n\n"
        for change in changes:
            body += f"- {change['type'].title()}: {change['name']}\n"
            body += f"  {change['description']}\n\n"
        
        create_github_issue(title, body)
        
    except Exception as e:
        error_msg = f"Error analyzing changes: {str(e)}"
        print(error_msg)
        create_github_issue(
            f"Error: Failed to analyze {os.path.basename(file_path)}",
            f"Error message: {error_msg}"
        )

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_py_changes.py <file_path>")
        sys.exit(1)
    
    analyze_changes(sys.argv[1])
