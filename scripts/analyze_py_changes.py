import ast
import difflib
import os
import sys
import subprocess
from typing import Dict, List, Optional, Tuple
import re
from pathlib import Path
import github
from github import Github
import openai
import time

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
                
                # Create PR with OpenAI-generated documentation
                self.create_pr(file_path, doc_content)
                
            except Exception as e:
                print(f"Error generating documentation with LLM: {str(e)}")
                # Create simple PR instead
                self.create_simple_pr(file_path, changes)

        except Exception as e:
            print(f"Error analyzing changes: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_py_changes.py <file_path>")
        sys.exit(1)

    analyzer = CodeAnalyzer()
    file_path = sys.argv[1]

    analyzer.analyze_changes(file_path)
