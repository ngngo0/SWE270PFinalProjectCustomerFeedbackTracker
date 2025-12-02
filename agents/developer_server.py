import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Developer")
BASE_PATH = "generated/code"
os.makedirs(BASE_PATH, exist_ok=True)

@mcp.tool()
def write_file(filename: str, content: str) -> str:
  full_path = os.path.join(BASE_PATH, filename)
  os.makedirs(os.path.dirname(full_path), exist_ok=True)
  with open(full_path, "w", encoding="utf-8") as f:
      f.write(content)
  return f"File written: {full_path}"

@mcp.tool()
def read_file(filename: str) -> str:
  full_path = os.path.join(BASE_PATH, filename)
  if not os.path.exists(full_path):
      return f"File not found: {full_path}"
  with open(full_path, "r", encoding="utf-8") as f:
      return f.read()

@mcp.tool()
def list_files() -> list[str]:
  result = []
  for root, dirs, files in os.walk(BASE_PATH):
      for file in files:
          path = os.path.relpath(os.path.join(root, file), BASE_PATH)
          result.append(path)
  return result

@mcp.tool()
def create_folder(path: str) -> str:
  full_path = os.path.join(BASE_PATH, path)
  os.makedirs(full_path, exist_ok=True)
  return f"Folder created: {full_path}"

if __name__ == "__main__":
  mcp.run(transport="stdio")
