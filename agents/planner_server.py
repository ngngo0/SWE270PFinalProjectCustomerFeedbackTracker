from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Planner")

@mcp.tool()
def create_plan(requirements: str) -> str:
    # Minimal plan: just echo requirements
    return f"PLAN:\n{requirements}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
