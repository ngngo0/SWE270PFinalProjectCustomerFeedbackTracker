# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

import asyncio

import os
load_dotenv()
api_key = os.getenv("API_KEY")

# os.environ["GOOGLE_API_KEY"] = ""
os.environ["GOOGLE_API_KEY"] = api_key



model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

server_params = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["math_server.py"],
)

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools)
            # agent_response1 = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            # 1. Addition, subtraction, and multiplication
            # Define all math test prompts
            math_prompts = [
                # "Compute (5 + 3 - 2) * 4",
                # "Calculate (10 / 2 + 3) ^ 2",
                # "What is (15 % 4 * 2) - 1?",
                # "Find result of (20 // 3 + 4) * 2",
                # "Compute sqrt(16) + 2 * 5",
                # "Evaluate (3 ^ 3 - 5) / 2",
                # "Calculate (22 % 5) + (10 // 3) + 1",
                # "What is sqrt(49) ^ 2 - 10?",
                # "Find result of (6 * 3 / 2) + 4",
                "Compute ((8 + 4) / 2 * 3) - sqrt(9)"
            ]

            # Collect responses from agent calls
            res = ""

            # Loop through each math prompt and invoke the agent
            for i, prompt in enumerate(math_prompts, start=1):
                response = await agent.ainvoke({"messages": prompt})
                res = parse_model_response(response)
                # print(f"✅ agent_test_{i}_response:", response)
            return res
        
# Function to parse model response
def parse_model_response(data):
    answer = data["messages"][-1].content
    return answer.split()[-1].rstrip(".")


    return final_response
# Run the async function
if __name__ == "__main__":
    result = asyncio.run(run_agent())
    print(result)