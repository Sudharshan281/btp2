import ast
import difflib
import os
import sys
import subprocess
from typing import Dict, List, Optional, Tuple, Any
import re
from pathlib import Path
import github
from github import Github
import openai
import time
import json
import requests

class CodeAnalyzer:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_name = os.getenv('GITHUB_REPOSITORY')
        self.github = Github(self.github_token) if self.github_token else None
        self.openai_client = openai
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client.api_key = os.getenv('OPENAI_API_KEY')

    def parse_ast(self, file_content: str) -> Optional[ast.AST]:
        """Parse Python code into an Abstract Syntax Tree (AST)."""
        try:
            tree = ast.parse(file_content)
            return tree
        except SyntaxError as e:
            print(f"SyntaxError parsing: {e}")
            return None

    def extract_code_elements(self, tree: ast.AST) -> Dict:
        """Extract all relevant code elements from an AST."""
        elements = {
            "functions": [],
            "classes": [],
            "methods": [],
            "imports": [],
            "constants": []
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function signature
                args = [arg.arg for arg in node.args.args]
                returns = ast.unparse(node.returns) if node.returns else None
                docstring = ast.get_docstring(node)
                decorators = [ast.unparse(d) for d in node.decorator_list]
                
                elements["functions"].append({
                    "name": node.name,
                    "args": args,
                    "returns": returns,
                    "docstring": docstring,
                    "decorators": decorators,
                    "lineno": node.lineno
                })
            
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                decorators = [ast.unparse(d) for d in node.decorator_list]
                bases = [ast.unparse(b) for b in node.bases]
                
                elements["classes"].append({
                    "name": node.name,
                    "docstring": docstring,
                    "decorators": decorators,
                    "bases": bases,
                    "lineno": node.lineno
                })
            
            elif isinstance(node, ast.Import):
                for name in node.names:
                    elements["imports"].append({
                        "name": name.name,
                        "alias": name.asname,
                        "lineno": node.lineno
                    })
            
            elif isinstance(node, ast.Assign):
                if isinstance(node.targets[0], ast.Name):
                    elements["constants"].append({
                        "name": node.targets[0].id,
                        "value": ast.unparse(node.value),
                        "lineno": node.lineno
                    })

        return elements

    def find_doc_file(self, file_path: str) -> Optional[str]:
        """Find the relevant documentation file for a given Python file."""
        current_dir = Path(file_path).parent
        max_depth = 3
        
        # First try to find README.md
        for _ in range(max_depth):
            readme_path = current_dir / "README.md"
            if readme_path.exists():
                return str(readme_path)
            current_dir = current_dir.parent
        
        # If no README, try to find docstring in the file
        return file_path

    def generate_doc_update(self, changes: Dict, file_path: str) -> Optional[str]:
        """Generate documentation update based on code changes."""
        doc_path = self.find_doc_file(file_path)
        if not doc_path:
            return None

        try:
            with open(doc_path, 'r') as f:
                current_doc = f.read()
        except FileNotFoundError:
            current_doc = ""

        # Prepare the prompt for the LLM
        prompt = f"""
        I have a Python file with the following changes:
        
        Added elements:
        {changes.get('added', [])}
        
        Removed elements:
        {changes.get('removed', [])}
        
        Current documentation:
        {current_doc}
        
        Please update the documentation to reflect these changes. Keep the same format and style as the current documentation.
        Only include the updated documentation content, no explanations or notes.
        """

        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical documentation writer. Update the documentation to reflect code changes while maintaining the same format and style."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating documentation with LLM: {e}")
            return None

    def create_pull_request(self, title: str, body: str, branch_name: str):
        """Create a pull request with the documentation updates."""
        if not self.github or not self.repo_name:
            print("GitHub token or repository not configured")
            return

        repo = self.github.get_repo(self.repo_name)
        
        # Create a new branch
        main_branch = repo.get_branch("main")
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=main_branch.commit.sha
        )

        # Create PR
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch_name,
            base="main"
        )
        
        return pr

    def create_simple_pr(self, file_path: str, changes: List[str]) -> None:
        """Create a simple PR with basic documentation update message."""
        if not self.github or not self.repo_name:
            print("GitHub credentials not available")
            return

        try:
            repo = self.github.get_repo(self.repo_name)
            branch_name = f"docs-update-{int(time.time())}"
            
            # Create new branch
            main_branch = repo.get_branch("main")
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=main_branch.commit.sha
            )

            # Create simple documentation
            doc_content = f"""# Documentation Update Needed

The file `{file_path}` has been modified. Please review and update the documentation for the following changes:

{chr(10).join(f"- {change}" for change in changes)}

This is an automated PR created because the OpenAI API key is not available. Please manually update the documentation as needed.
"""

            # Create or update documentation file
            doc_path = f"src/api/{Path(file_path).stem}.md"
            try:
                contents = repo.get_contents(doc_path, ref=branch_name)
                repo.update_file(
                    path=doc_path,
                    message="Update documentation",
                    content=doc_content,
                    sha=contents.sha,
                    branch=branch_name
                )
            except github.GithubException:
                repo.create_file(
                    path=doc_path,
                    message="Create documentation",
                    content=doc_content,
                    branch=branch_name
                )

            # Create PR
            pr = repo.create_pull(
                title=f"Docs: Update documentation for {file_path}",
                body="This PR was created automatically to track documentation updates needed for recent code changes.",
                head=branch_name,
                base="main"
            )
            print(f"Created PR #{pr.number}")

        except Exception as e:
            print(f"Error creating PR: {str(e)}")

    def create_documentation_issue(self, file_path: str, changes: List[str]) -> None:
        """Create a GitHub issue to track documentation updates needed."""
        if not self.github or not self.repo_name:
            print("GitHub credentials not available")
            return

        try:
            repo = self.github.get_repo(self.repo_name)
            
            # Create issue content
            issue_title = f"Documentation Update Needed for {file_path}"
            issue_body = f"""# Documentation Update Needed

The file `{file_path}` has been modified. Please review and update the documentation for the following changes:

{chr(10).join(f"- {change}" for change in changes)}

This is an automated issue created because the OpenAI API key is not available. Please manually update the documentation as needed.

## Steps to Update Documentation:
1. Review the changes in `{file_path}`
2. Update the corresponding documentation in `src/api/{Path(file_path).stem}.md`
3. Create a pull request with the documentation updates
"""

            # Create issue
            issue = repo.create_issue(
                title=issue_title,
                body=issue_body,
                labels=["documentation", "help wanted"]
            )
            print(f"Created issue #{issue.number}")

        except Exception as e:
            print(f"Error creating issue: {str(e)}")

    def analyze_changes(self, file_path: str) -> None:
        """Analyze changes in a Python file and generate documentation."""
        print(f"Analyzing changes for {file_path}")
        
        try:
            # Get current content
            with open(file_path, 'r', encoding='utf-8') as f:
                new_content = f.read()

            # Get previous version from git
            try:
                old_content = subprocess.run(
                    ['git', 'show', f'HEAD^:{file_path}'],
                    capture_output=True,
                    text=True
                ).stdout
            except subprocess.CalledProcessError:
                print(f"Could not find previous version of {file_path}")
                return

            # Extract changes
            changes = []
            for line in difflib.unified_diff(
                old_content.splitlines(),
                new_content.splitlines(),
                fromfile='old',
                tofile='new',
                lineterm=''
            ):
                if line.startswith('+') and not line.startswith('+++'):
                    changes.append(line[1:].strip())

            # Try to use OpenAI for documentation
            try:
                if not self.openai_client.api_key:
                    raise Exception("No OpenAI API key available")
                
                response = self.openai_client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a documentation generator. Create clear, concise documentation for Python code changes."},
                        {"role": "user", "content": f"Generate documentation for these changes:\n{chr(10).join(changes)}"}
                    ]
                )
                doc_content = response.choices[0].message.content
                
                # Create documentation file
                doc_path = f"src/api/{Path(file_path).stem}.md"
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                
                print(f"Created documentation at {doc_path}")
                
            except Exception as e:
                print(f"Error generating documentation with LLM: {str(e)}")
                # Create issue instead
                self.create_documentation_issue(file_path, changes)

        except Exception as e:
            print(f"Error analyzing changes: {str(e)}")

def get_github_token():
    return os.environ.get('GITHUB_TOKEN')

def get_openai_key():
    return os.environ.get('OPENAI_API_KEY')

def get_repo_name():
    return os.environ.get('GITHUB_REPOSITORY')

def get_file_content(file_path: str) -> str:
    try:
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

def check_readme_updates(py_file: str, changes: List[Dict[str, Any]]) -> bool:
    """Check if README.md needs updates based on Python file changes."""
    readme_path = os.path.join(os.path.dirname(py_file), 'README.md')
    if not os.path.exists(readme_path):
        return True  # README needs to be created
        
    current_readme = get_file_content(readme_path)
    if not current_readme:
        return True
        
    # Check if any new functions/classes are not documented in README
    for change in changes:
        if change['type'] == 'added':
            if change['name'] not in current_readme:
                return True
                
    return False

def create_readme_issue(py_file: str, changes: List[Dict[str, Any]]):
    """Create a GitHub issue about README updates needed."""
    token = get_github_token()
    repo_name = get_repo_name()
    
    if not token or not repo_name:
        print("Missing GitHub token or repository name")
        return
        
    g = Github(token)
    try:
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

def analyze_changes(file_path: str):
    """Analyze changes in a Python file and check if README needs updates."""
    print(f"Analyzing changes for {file_path}")
    
    # Get file contents
    current_content = get_file_content(file_path)
    previous_content = get_previous_version(file_path)
    
    if not current_content:
        print(f"Could not get current content for {file_path}")
        return
        
    # Extract API elements from both versions
    current_elements = extract_api_elements(current_content)
    previous_elements = extract_api_elements(previous_content) if previous_content else []
    
    # Find changes
    changes = find_changes(previous_elements, current_elements)
    
    # Check if README needs updates
    if check_readme_updates(file_path, changes):
        print("README needs updates")
        create_readme_issue(file_path, changes)
    else:
        print("README is up to date")

def generate_documentation_with_llm(changes):
    """Generate documentation using OpenAI's GPT model."""
    try:
        client = openai.OpenAI()  # Will use OPENAI_API_KEY from environment
        
        prompt = f"""
        Please analyze these code changes and suggest documentation updates:
        {json.dumps(changes, indent=2)}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes code changes and suggests documentation updates."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating documentation with LLM: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_py_changes.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    analyzer = CodeAnalyzer()
    analyzer.analyze_changes(file_path)
