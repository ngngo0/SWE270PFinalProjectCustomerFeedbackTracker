import asyncio
import sys
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Any
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# -------------------------
# Log function
# -------------------------
async def log_status(message: str, status_callback=None):
    print(f"[STATUS] {message}")
    if status_callback:
        await status_callback(message)
    await asyncio.sleep(0)  # yield control to event loop

# -------------------------
# Build agent function
# -------------------------
async def build_agent(server_path: str):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path]
    )
    async with stdio_client(server_params) as (read, write):
        session = ClientSession(read, write)
        await session.initialize()
        tools = await load_mcp_tools(session)
        return (session, tools)


# -------------------------
# LangGraph workflow
# -------------------------
class SoftwareState(TypedDict):
    messages: str
    plan: str
    code: str
    tests: str
    planner: Any
    developer: Any
    tester: Any

async def planner_agent(state):
    session, tools = state["planner"]
    agent = create_react_agent(model, tools)
    resp = await agent.ainvoke({"messages": state["messages"]})
    return {"plan": resp["messages"][-1].content}

async def developer_agent(state):
    session, tools = state["developer"]
    agent = create_react_agent(model, tools)
    resp = await agent.ainvoke({"messages": state["plan"]})
    return {"code": resp["messages"][-1].content}

async def tester_agent(state):
    session, tools = state["tester"]
    agent = create_react_agent(model, tools)
    resp = await agent.ainvoke({"messages": state["code"]})
    return {"tests": resp["messages"][-1].content}

graph = StateGraph(SoftwareState)
graph.add_node("planner", planner_agent)
graph.add_node("developer", developer_agent)
graph.add_node("tester", tester_agent)
graph.set_entry_point("planner")
graph.add_edge("planner", "developer")
graph.add_edge("developer", "tester")
graph.add_edge("tester", END)
workflow = graph.compile()

# -------------------------
# Run system
# -------------------------
async def run_system(description: str, requirements: str, status_callback=None):
    await log_status("Building planner agent...", status_callback)
    planner = await build_agent("agents/planner_server.py")

    await log_status("Building developer agent...", status_callback)
    developer = await build_agent("agents/developer_server.py")

    await log_status("Building tester agent...", status_callback)
    tester = await build_agent("agents/tester_server.py")

    state = {
        "messages": f"Description:\n{description}\nRequirements:\n{requirements}",
        "planner": planner,
        "developer": developer,
        "tester": tester
    }

    await log_status("Running workflow...", status_callback)
    result = await workflow.ainvoke(state)
    await log_status("Workflow completed!", status_callback)
    return result


# -------------------------
# CLI test
# -------------------------
if __name__ == "__main__":
    description = input("Software description: ")
    requirements = input("Requirements: ")
    result = asyncio.run(run_system(description, requirements))
    print("\n--- PLAN ---\n", result["plan"])
    print("\n--- CODE ---\n", result["code"])
    print("\n--- TESTS ---\n", result["tests"])
