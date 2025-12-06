import asyncio
import sys
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
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
async def run_agent(server_path: str, input_data: dict, system_prompt: str) -> dict:
    """
    Runs an MCP agent with full tool execution until completion.
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

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=json.dumps(input_data))]

            # ---- TOOL EXECUTION LOOP ----
            while True:
                result = await agent.ainvoke({"messages": messages})
                last_msg = result["messages"][-1]

                # If the assistant is calling a tool:
                if isinstance(last_msg, ToolMessage):
                    tool_name = last_msg.name
                    args = last_msg.arguments

                    tool_fn = tools.get(tool_name)
                    if tool_fn is None:
                        raise RuntimeError(f"Unknown tool: {tool_name}")

                    # Execute tool
                    tool_output = await tool_fn(**args)

                    # Append tool result back to agent
                    messages.append(
                        ToolMessage(
                            name=tool_name,
                            content=json.dumps(tool_output)
                        )
                    )
                    continue

                # No more tools → final answer
                return {"raw": last_msg.content}

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
    planner_output = await run_agent("agents/planner_server.py", input_data, 
                                     "You are a planner agent, create a plan for this software based on these requirements")
    await log_status("Planner completed!")

    # Developer agent
    await log_status("Building developer agent...", status_callback)
    developer_output = await run_agent("agents/developer_server.py", {"planner_output": planner_output}, "You are a software developer. Given this plan, make a readme, and the full application with a local host version I can spin up.")
    await log_status("Developer completed!")

    # Tester agent
    await log_status("Building tester agent...", status_callback)
    tester_output = await run_agent("agents/tester_server.py", {"developer_output": developer_output}, "You are a software tester. Given the files in the generated folder, write test cases and run the test cases to make sure there are no bugs.")
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
