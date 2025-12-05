import asyncio
import sys
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# -------------------------
# Load API key
# -------------------------
load_dotenv()

# -------------------------
# Initialize model
# -------------------------
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# -------------------------
# Log function
# -------------------------
async def log_status(message: str, status_callback=None):
    print(f"[STATUS] {message}")
    if status_callback:
        await status_callback(message)
    await asyncio.sleep(0)  # yield control to event loop

# -------------------------
# Run single agent with structured output
# -------------------------
async def run_agent(server_path: str, input_data: dict) -> dict:
    """
    Runs a single MCP agent and returns its structured output as a dictionary.
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_agent(model, tools)
            
            # Send structured input as JSON string
            messages = [HumanMessage(content=json.dumps(input_data))]
            result = await agent.ainvoke({"messages": messages})
            
            # Extract last message content
            last_msg = result["messages"][-1]
            if isinstance(last_msg, ToolMessage):
                # Get structured tool output
                tool_args = last_msg.additional_kwargs.get("function_call", {}).get("arguments", "{}")
                try:
                    final_output = json.loads(tool_args)
                except json.JSONDecodeError:
                    final_output = {"raw": tool_args}
            else:
                # Fall back to raw text output
                final_output = {"raw": last_msg.content}
            
            return final_output

# -------------------------
# Run the multi-agent workflow
# -------------------------
async def run_system(description: str, requirements: str, status_callback=None):
    input_data = {
        "description": description,
        "requirements": requirements
    }

    # Planner agent
    await log_status("Building planner agent...", status_callback)
    planner_output = await run_agent("agents/planner_server.py", input_data)
    await log_status("Planner completed!")

    # Developer agent
    await log_status("Building developer agent...", status_callback)
    developer_output = await run_agent("agents/developer_server.py", {"planner_output": planner_output})
    await log_status("Developer completed!")

    # Tester agent
    await log_status("Building tester agent...", status_callback)
    tester_output = await run_agent("agents/tester_server.py", {"developer_output": developer_output})
    await log_status("Tester completed!")

    return {
        "plan": planner_output,
        "code": developer_output,
        "tests": tester_output
    }

# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":
    description = input("Software description: ")
    requirements = input("Requirements: ")
    result = asyncio.run(run_system(description, requirements))

    print("\n--- PLAN ---\n", json.dumps(result["plan"], indent=2))
    print("\n--- CODE ---\n", json.dumps(result["code"], indent=2))
    print("\n--- TESTS ---\n", json.dumps(result["tests"], indent=2))
