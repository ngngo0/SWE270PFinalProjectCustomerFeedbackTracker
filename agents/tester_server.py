from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Tester")

@mcp.tool()
def generate_tests(code: str) -> str:
    # Minimal: wrap code in a dummy test function
    return f"def test_generated():\n    # TODO: write real tests\n    pass"

if __name__ == "__main__":
    mcp.run(transport="stdio")
