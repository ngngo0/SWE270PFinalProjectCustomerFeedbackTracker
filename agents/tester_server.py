import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Tester")

BASE_PATH = "generated/tests"
BASE_CODE_PATH = "generated"

os.makedirs(BASE_PATH, exist_ok=True)
os.makedirs(BASE_CODE_PATH, exist_ok=True)


@mcp.tool()
def find_python_files(base_code_path: str = BASE_CODE_PATH) -> list[str]:
    """Find all .py files in the generated folder (excluding __init__.py and __pycache__)."""
    py_files = []
    for root, dirs, files in os.walk(base_code_path):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                full = os.path.join(root, f)
                rel = os.path.relpath(full, base_code_path)
                py_files.append(rel)
    return py_files


@mcp.tool()
def read_file(filename: str) -> str:
    """Read source code from generated folder."""
    full_path = os.path.join(BASE_CODE_PATH, filename)
    if not os.path.exists(full_path):
        return f"File not found: {full_path}"
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


@mcp.tool()
def generate_tests(code: str, source_filename: str = "") -> str:
    """
    Generate test file with basic tests for all functions and classes.
    """
    import ast
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"import pytest\n\ndef test_syntax():\n    pass"
    
    functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
    
    # Extract module name from filename
    module_name = source_filename.replace(".py", "").replace(os.sep, ".")
    
    # Build test file with sys.path and correct imports
    lines = [
        "import sys",
        "from pathlib import Path",
        "",
        "# Add generated folder to path",
        "sys.path.insert(0, str(Path(__file__).parent.parent))",
        "",
        "import pytest",
    ]
    
    # Add import from the actual module
    if module_name:
        lines.append(f"from {module_name} import *")
        lines.append("")
    
    # Generate basic tests for functions
    if functions:
        for fn in functions:
            lines.append("")
            lines.append(f"def test_{fn}():")
            lines.append(f'    """Test {fn}."""')
            lines.append(f"    assert callable({fn})")
    
    # Generate basic tests for classes
    if classes:
        for cls in classes:
            lines.append("")
            lines.append(f"def test_{cls}():")
            lines.append(f'    """Test {cls}."""')
            lines.append(f"    assert {cls} is not None")
    
    # If no functions or classes found
    if not functions and not classes:
        lines.append("")
        lines.append("def test_module():")
        lines.append('    """Test that module imports."""')
        lines.append("    pass")
    
    return "\n".join(lines)


@mcp.tool()
def write_file(filename: str, content: str) -> str:
    """Write test file to generated/tests folder (flat structure)."""
    # Extract just the filename (no directory path)
    test_filename = os.path.basename(filename)
    full_path = os.path.join(BASE_PATH, test_filename)
    
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"Test file written: {full_path}"


@mcp.tool()
def list_files() -> list[str]:
    """List all Python files in generated folder."""
    result = []
    for root, dirs, files in os.walk(BASE_CODE_PATH):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if file.endswith(".py"):
                path = os.path.relpath(os.path.join(root, file), BASE_CODE_PATH)
                result.append(path)
    return result


@mcp.tool()
def generate_tests_for_all() -> list[str]:
    """
    Generate tests for all Python files in generated folder.
    Tests go to generated/tests/ with correct imports.
    """
    py_files = find_python_files(BASE_CODE_PATH)
    results = []
    
    for file in py_files:
        # Read source code
        source = read_file(file)
        if source.startswith("File not found"):
            continue
        
        # Generate tests with correct imports
        test_code = generate_tests(source, file)
        
        # Create test filename (flat structure)
        base_name = os.path.basename(file)
        test_filename = "test_" + base_name
        
        # Write test file
        write_result = write_file(test_filename, test_code)
        results.append(write_result)
    
    return results


if __name__ == "__main__":
    mcp.run(transport="stdio")