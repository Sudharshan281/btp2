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

class CodeAnalyzer:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_name = os.getenv('GITHUB_REPOSITORY')
        self.github = Github(self.github_token) if self.github_token else None
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None

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
            response = self.openai_client.chat.completions.create(
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

    def analyze_changes(self, file_path: str) -> Dict:
        """Analyze changes between two versions of a Python file using AST."""
        print(f"\nAnalyzing changes for {file_path}")
        
        # Get the current content
        try:
            with open(file_path, 'r') as f:
                new_content = f.read()
        except FileNotFoundError:
            print(f"Error: {file_path} does not exist.")
            return None

        # Get the previous version from git
        try:
            result = subprocess.run(
                ['git', 'show', 'HEAD^:' + file_path],
                capture_output=True,
                text=True
            )
            old_content = result.stdout if result.returncode == 0 else ""
        except Exception as e:
            print(f"Error getting previous version: {e}")
            old_content = ""

        # Parse ASTs
        old_tree = self.parse_ast(old_content)
        new_tree = self.parse_ast(new_content)

        if new_tree is None:
            return None

        # Extract elements from both versions
        old_elements = self.extract_code_elements(old_tree) if old_tree else {"functions": [], "classes": [], "imports": [], "constants": []}
        new_elements = self.extract_code_elements(new_tree)

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
            elif func != old_funcs[name]:
                changes["added"].append({"functions": [func]})
                changes["removed"].append({"functions": [old_funcs[name]]})
        
        for name, func in old_funcs.items():
            if name not in new_funcs:
                changes["removed"].append({"functions": [func]})

        # Compare classes
        old_classes = {c["name"]: c for c in old_elements["classes"]}
        new_classes = {c["name"]: c for c in new_elements["classes"]}
        
        for name, cls in new_classes.items():
            if name not in old_classes:
                changes["added"].append({"classes": [cls]})
            elif cls != old_classes[name]:
                changes["added"].append({"classes": [cls]})
                changes["removed"].append({"classes": [old_classes[name]]})
        
        for name, cls in old_classes.items():
            if name not in new_classes:
                changes["removed"].append({"classes": [cls]})

        # Compare imports
        old_imports = {i["name"]: i for i in old_elements["imports"]}
        new_imports = {i["name"]: i for i in new_elements["imports"]}
        
        for name, imp in new_imports.items():
            if name not in old_imports:
                changes["added"].append({"imports": [imp]})
        
        for name, imp in old_imports.items():
            if name not in new_imports:
                changes["removed"].append({"imports": [imp]})

        # Compare constants
        old_constants = {c["name"]: c for c in old_elements["constants"]}
        new_constants = {c["name"]: c for c in new_elements["constants"]}
        
        for name, const in new_constants.items():
            if name not in old_constants:
                changes["added"].append({"constants": [const]})
            elif const != old_constants[name]:
                changes["added"].append({"constants": [const]})
                changes["removed"].append({"constants": [old_constants[name]]})
        
        for name, const in old_constants.items():
            if name not in new_constants:
                changes["removed"].append({"constants": [const]})

        return changes

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_py_changes.py <file_path>")
        sys.exit(1)

    analyzer = CodeAnalyzer()
    file_path = sys.argv[1]

    changes = analyzer.analyze_changes(file_path)
    
    if changes:
        doc_update = analyzer.generate_doc_update(changes, file_path)
        if doc_update:
            print("\nDocumentation update generated:")
            print(doc_update)
            
            # Create PR if running in GitHub Actions
            if analyzer.github_token:
                branch_name = f"docs-update/{os.path.basename(file_path)}-{os.getenv('GITHUB_RUN_ID')}"
                pr = analyzer.create_pull_request(
                    title=f"Documentation Update for {os.path.basename(file_path)}",
                    body=doc_update,
                    branch_name=branch_name
                )
                if pr:
                    print(f"Created PR: {pr.html_url}")
    else:
        print("No significant changes detected.")
