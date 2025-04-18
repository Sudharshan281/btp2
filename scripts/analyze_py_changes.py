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
from openai import OpenAI

class APIAnalyzer:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_name = os.getenv('GITHUB_REPOSITORY')
        self.github = Github(self.github_token) if self.github_token else None
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None

    def parse_ast(self, file_content: str) -> Optional[ast.AST]:
        """Parse Python code into an Abstract Syntax Tree (AST)."""
        try:
            return ast.parse(file_content)
        except SyntaxError as e:
            print(f"SyntaxError parsing: {e}")
            return None

    def extract_api_elements(self, tree: ast.AST) -> Dict:
        """Extract all relevant API elements from an AST."""
        elements = {
            "functions": [],
            "classes": [],
            "methods": [],
            "decorators": []
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function signature
                args = [arg.arg for arg in node.args.args]
                returns = None
                if node.returns:
                    returns = ast.unparse(node.returns)
                
                # Get docstring
                docstring = ast.get_docstring(node)
                
                # Get decorators
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
                # Get class docstring
                docstring = ast.get_docstring(node)
                
                # Get class decorators
                decorators = [ast.unparse(d) for d in node.decorator_list]
                
                elements["classes"].append({
                    "name": node.name,
                    "docstring": docstring,
                    "decorators": decorators,
                    "lineno": node.lineno
                })

        return elements

    def find_readme(self, file_path: str) -> Optional[str]:
        """Find the relevant README file for a given Python file."""
        current_dir = Path(file_path).parent
        max_depth = 3  # Maximum number of parent directories to check
        
        for _ in range(max_depth):
            readme_path = current_dir / "README.md"
            if readme_path.exists():
                return str(readme_path)
            current_dir = current_dir.parent
        
        return None

    def generate_doc_update_with_llm(self, changes: Dict, file_path: str, current_doc: str) -> Optional[str]:
        """Generate documentation update using OpenAI's LLM."""
        if not self.openai_client:
            print("OpenAI API key not configured")
            return None

        # Prepare the prompt for the LLM
        prompt = f"""
        I have a Python API file with the following changes:
        
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
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical documentation writer. Update the documentation to reflect API changes while maintaining the same format and style."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating documentation with LLM: {e}")
            return None

    def generate_doc_update(self, changes: Dict, file_path: str) -> Optional[str]:
        """Generate documentation update based on API changes."""
        readme_path = self.find_readme(file_path)
        if not readme_path:
            return None

        try:
            with open(readme_path, 'r') as f:
                current_doc = f.read()
        except FileNotFoundError:
            current_doc = ""

        # Try to use LLM for documentation update
        llm_update = self.generate_doc_update_with_llm(changes, file_path, current_doc)
        if llm_update:
            return llm_update

        # Fallback to basic update if LLM fails
        update = []
        if changes["added"]:
            update.append("### New API Elements")
            for element in changes["added"]:
                if "functions" in element:
                    for func in element["functions"]:
                        update.append(f"- Added function `{func['name']}`")
                        if func["docstring"]:
                            update.append(f"  ```python\n  {func['docstring']}\n  ```")
                
                if "classes" in element:
                    for cls in element["classes"]:
                        update.append(f"- Added class `{cls['name']}`")
                        if cls["docstring"]:
                            update.append(f"  ```python\n  {cls['docstring']}\n  ```")

        if changes["removed"]:
            update.append("### Removed API Elements")
            for element in changes["removed"]:
                if "functions" in element:
                    for func in element["functions"]:
                        update.append(f"- Removed function `{func['name']}`")
                
                if "classes" in element:
                    for cls in element["classes"]:
                        update.append(f"- Removed class `{cls['name']}`")

        return "\n".join(update) if update else None

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

    def analyze_changes(self, old_file: str, new_file: str) -> Dict:
        """Analyze changes between two versions of a Python file."""
        try:
            with open(old_file, 'r') as f:
                old_content = f.read()
        except FileNotFoundError:
            old_content = ""

        try:
            with open(new_file, 'r') as f:
                new_content = f.read()
        except FileNotFoundError:
            print(f"Error: {new_file} does not exist.")
            return None

        old_tree = self.parse_ast(old_content)
        new_tree = self.parse_ast(new_content)

        if old_tree is None or new_tree is None:
            return None

        old_elements = self.extract_api_elements(old_tree)
        new_elements = self.extract_api_elements(new_tree)

        changes = {
            "added": [],
            "removed": []
        }

        # Compare functions
        old_funcs = {f["name"]: f for f in old_elements["functions"]}
        new_funcs = {f["name"]: f for f in new_elements["functions"]}
        
        for name, func in new_funcs.items():
            if name not in old_funcs:
                changes["added"].append({"functions": [func]})
        
        for name, func in old_funcs.items():
            if name not in new_funcs:
                changes["removed"].append({"functions": [func]})

        # Compare classes
        old_classes = {c["name"]: c for c in old_elements["classes"]}
        new_classes = {c["name"]: c for c in new_elements["classes"]}
        
        for name, cls in new_classes.items():
            if name not in old_classes:
                changes["added"].append({"classes": [cls]})
        
        for name, cls in old_classes.items():
            if name not in new_classes:
                changes["removed"].append({"classes": [cls]})

        return changes

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyze_py_changes.py <old_file> <new_file>")
        sys.exit(1)

    analyzer = APIAnalyzer()
    old_file = sys.argv[1]
    new_file = sys.argv[2]

    changes = analyzer.analyze_changes(old_file, new_file)
    
    if changes:
        doc_update = analyzer.generate_doc_update(changes, new_file)
        if doc_update:
            print("Documentation update required:")
            print(doc_update)
            
            # Create PR if running in GitHub Actions
            if analyzer.github_token:
                branch_name = f"docs-update/api-changes-{os.getenv('GITHUB_RUN_ID')}"
                pr = analyzer.create_pull_request(
                    title="API Documentation Updates Required",
                    body=doc_update,
                    branch_name=branch_name
                )
                if pr:
                    print(f"Created PR: {pr.html_url}")
    else:
        print("No API changes detected.")
