import asyncio
import sys
import os
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
# Run single agent
# -------------------------
async def run_agent(server_path: str, input_text: str) -> str:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_agent(model, tools)
            
            # Wrap input_text as a HumanMessage
            messages = [HumanMessage(content=input_text)]
            
            # Run the agent
            result = await agent.ainvoke({"messages": messages})

            final_message = result["messages"][-1].content
            print(final_message)
        

# -------------------------
# Run the multi-agent workflow
# -------------------------
async def run_system(description: str, requirements: str,  status_callback=None):
    message = f"Description:\n{description}\nRequirements:\n{requirements}"

    # Planner agent
    await log_status("Building planner agent...", status_callback)
    planner = await run_agent("agents/planner_server.py", message)
    await log_status("Planner completed!")

    # Developer agent
    await log_status("Building developer agent...", status_callback)
    developer = await run_agent("agents/developer_server.py", planner)
    await log_status("Developer completed!")

    # Tester agent
    await log_status("Building tester agent...", status_callback)
    tester = await run_agent("agents/tester_server.py", developer)
    await log_status("Tester completed!")

    return {
        "plan": planner,
        "code": developer,
        "tests": tester
    }

# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":
    description = input("Software description: ")
    requirements = input("Requirements: ")
    result = asyncio.run(run_system(description, requirements))

    print("\n--- PLAN ---\n", result["plan"])
    print("\n--- CODE ---\n", result["code"])
    print("\n--- TESTS ---\n", result["tests"])
