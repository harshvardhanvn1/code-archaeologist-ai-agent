"""Documentation analysis tool for identifying documentation gaps."""
from pathlib import Path
from typing import Dict, List, Any
import ast
from datetime import datetime


def analyze_documentation(repo_path: str) -> Dict[str, Any]:
    """
    Analyze repository documentation coverage and quality.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary containing documentation analysis results
    """
    try:
        repo_path = Path(repo_path).resolve()
        
        # Check for README
        readme_exists = any([
            (repo_path / name).exists()
            for name in ["README.md", "README.rst", "README.txt", "README"]
        ])
        
        # Find Python files
        python_files = list(repo_path.rglob("*.py"))
        
        # Filter out venv and other excluded directories
        excluded_dirs = {"venv", "env", ".git", "__pycache__", "node_modules"}
        python_files = [
            f for f in python_files
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]
        
        if not python_files:
            return {
                "coverage": 0.0,
                "has_readme": readme_exists,
                "total_files": 0,
                "documented_files": 0,
                "undocumented_files": [],
                "analysis_status": "no_python_files_found"
            }
        
        # Analyze each Python file
        file_analyses = []
        for py_file in python_files:
            analysis = _analyze_python_file(py_file)
            file_analyses.append(analysis)
        
        # Calculate statistics
        documented_files = [f for f in file_analyses if f["has_docstring"]]
        undocumented_files = [
            {
                "file": str(f["file"].relative_to(repo_path)),
                "functions": f["total_functions"],
                "classes": f["total_classes"]
            }
            for f in file_analyses
            if not f["has_docstring"] and (f["total_functions"] > 0 or f["total_classes"] > 0)
        ]
        
        # Calculate coverage percentage
        if python_files:
            coverage = len(documented_files) / len(python_files)
        else:
            coverage = 0.0
        
        # Calculate function/class documentation
        total_functions = sum(f["total_functions"] for f in file_analyses)
        documented_functions = sum(f["documented_functions"] for f in file_analyses)
        total_classes = sum(f["total_classes"] for f in file_analyses)
        documented_classes = sum(f["documented_classes"] for f in file_analyses)
        
        function_coverage = (
            documented_functions / total_functions if total_functions > 0 else 1.0
        )
        class_coverage = (
            documented_classes / total_classes if total_classes > 0 else 1.0
        )
        
        return {
            "coverage": round(coverage, 2),
            "has_readme": readme_exists,
            "total_files": len(python_files),
            "documented_files": len(documented_files),
            "undocumented_files": undocumented_files[:10],  # Top 10
            "function_coverage": round(function_coverage, 2),
            "class_coverage": round(class_coverage, 2),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "analysis_status": "completed",
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "coverage": 0.0,
            "has_readme": False,
            "total_files": 0,
            "analysis_status": "error"
        }


def _analyze_python_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single Python file for documentation."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Check for module docstring
        has_module_docstring = ast.get_docstring(tree) is not None
        
        # Count functions and their docstrings
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        documented_functions = sum(1 for f in functions if ast.get_docstring(f) is not None)
        
        # Count classes and their docstrings
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        documented_classes = sum(1 for c in classes if ast.get_docstring(c) is not None)
        
        return {
            "file": file_path,
            "has_docstring": has_module_docstring,
            "total_functions": len(functions),
            "documented_functions": documented_functions,
            "total_classes": len(classes),
            "documented_classes": documented_classes
        }
        
    except Exception:
        return {
            "file": file_path,
            "has_docstring": False,
            "total_functions": 0,
            "documented_functions": 0,
            "total_classes": 0,
            "documented_classes": 0
        }


if __name__ == "__main__":
    import json
    result = analyze_documentation(".")
    print(json.dumps(result, indent=2))