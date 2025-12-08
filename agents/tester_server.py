import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Tester")
print("CWD:", os.getcwd())
BASE_PATH = "generated/tests"
BASE_CODE_PATH = "generated"

os.makedirs(BASE_PATH, exist_ok=True)
os.makedirs(BASE_CODE_PATH, exist_ok=True)


# --- Utility functions ---
@mcp.tool()
def find_python_files(base_path: str) -> list[str]:
    """Return all .py files inside a folder (recursively)."""
    py_files = []
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith(".py"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, base_path)
                py_files.append(rel)
    return py_files

@mcp.tool()
def test_filename_for(source_filename: str) -> str:
    """Convert my_module.py -> test_my_module.py and keep folder structure."""
    dir_name = os.path.dirname(source_filename)
    base = os.path.basename(source_filename)
    test_name = "test_" + base
    return os.path.join(dir_name, test_name)


@mcp.tool()
def generate_tests(code: str) -> str:
    """
    A smarter test generator: extracts functions and creates basic test stubs.
    """
    import ast

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "Could not parse file for test generation."

    functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]

    out = ["import pytest\n"]
    for fn in functions:
        out.append(f"\n\ndef test_{fn}():\n    # TODO: write real test\n    assert False  # placeholder\n")

    return "\n".join(out).strip()


@mcp.tool()
def write_file(filename: str, content: str) -> str:
    full_path = os.path.join(BASE_PATH, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written: {full_path}"


@mcp.tool()
def read_file(filename: str) -> str:
    full_path = os.path.join(BASE_CODE_PATH, filename)
    if not os.path.exists(full_path):
        return f"File not found: {full_path}"
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


@mcp.tool()
def list_files() -> list[str]:
    result = []
    for root, dirs, files in os.walk(BASE_CODE_PATH):
        for file in files:
            path = os.path.relpath(os.path.join(root, file), BASE_PATH)
            result.append(path)
    return result


@mcp.tool()
def create_folder(path: str) -> str:
    full_path = os.path.join(BASE_PATH, path)
    os.makedirs(full_path, exist_ok=True)
    return f"Folder created: {full_path}"


# --- NEW: Generate tests for the entire generated/ folder ---

@mcp.tool()
def generate_tests_for_all() -> list[str]:
    """
    Looks at generated/ for .py files,
    reads them, generates tests, and writes them into generated/tests/.
    """
    py_files = find_python_files(BASE_CODE_PATH)
    results = []

    for file in py_files:
        # Read source code
        source = read_file(file)
        if source.startswith("File not found"):
            continue

        # Generate tests
        test_code = generate_tests(source)

        # Determine test file path
        test_file = test_filename_for(file)

        # Write tests
        write_result = write_file(test_file, test_code)
        results.append(write_result)

    return results


if __name__ == "__main__":
    mcp.run(transport="stdio")
