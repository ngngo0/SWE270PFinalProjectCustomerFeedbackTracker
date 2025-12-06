import asyncio
import sys
import os
import json
import logging
from datetime import datetime
from typing import Optional, Callable
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
# Configure Logging
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_communication.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -------------------------
# Metrics Tracking Class
# -------------------------
class MetricsTracker:
    """Track API calls and token usage across all agents"""
    
    def __init__(self):
        self.metrics = {
            'planner': {'api_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0},
            'developer': {'api_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0},
            'tester': {'api_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0},
            'total': {'api_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
        }
        self.start_time = None
        self.end_time = None
    
    def start_tracking(self):
        """Start tracking execution time"""
        self.start_time = datetime.now()
        logger.info(f"=== Metrics tracking started at {self.start_time} ===")
    
    def end_tracking(self):
        """End tracking and calculate duration"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"=== Metrics tracking ended at {self.end_time} (Duration: {duration:.2f}s) ===")
    
    def record_api_call(self, agent_name: str, input_tokens: int = 0, output_tokens: int = 0):
        """Record an API call with token usage"""
        if agent_name not in self.metrics:
            return
        
        self.metrics[agent_name]['api_calls'] += 1
        self.metrics[agent_name]['input_tokens'] += input_tokens
        self.metrics[agent_name]['output_tokens'] += output_tokens
        self.metrics[agent_name]['total_tokens'] += (input_tokens + output_tokens)
        
        # Update totals
        self.metrics['total']['api_calls'] += 1
        self.metrics['total']['input_tokens'] += input_tokens
        self.metrics['total']['output_tokens'] += output_tokens
        self.metrics['total']['total_tokens'] += (input_tokens + output_tokens)
        
        logger.info(f"[{agent_name.upper()}] API Call #{self.metrics[agent_name]['api_calls']} - "
                   f"Input: {input_tokens} tokens, Output: {output_tokens} tokens")
    
    def get_summary(self) -> dict:
        """Get complete metrics summary"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        return {
            'metrics': self.metrics,
            'execution_time_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }
    
    def print_summary(self):
        """Print formatted metrics summary"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        print("\n" + "="*70)
        print("📊 MULTI-AGENT SYSTEM METRICS SUMMARY")
        print("="*70)
        print(f"⏱️  Total Execution Time: {duration:.2f} seconds")
        print(f"🔢 Total API Calls: {self.metrics['total']['api_calls']}")
        print(f"📝 Total Tokens Used: {self.metrics['total']['total_tokens']:,}")
        print(f"   - Input Tokens: {self.metrics['total']['input_tokens']:,}")
        print(f"   - Output Tokens: {self.metrics['total']['output_tokens']:,}")
        print("\n" + "-"*70)
        print("Per-Agent Breakdown:")
        print("-"*70)
        
        for agent in ['planner', 'developer', 'tester']:
            metrics = self.metrics[agent]
            print(f"\n🤖 {agent.upper()} Agent:")
            print(f"   API Calls: {metrics['api_calls']}")
            print(f"   Total Tokens: {metrics['total_tokens']:,}")
            print(f"   - Input: {metrics['input_tokens']:,}")
            print(f"   - Output: {metrics['output_tokens']:,}")
        
        print("\n" + "="*70 + "\n")

# Global metrics tracker
metrics_tracker = MetricsTracker()

# -------------------------
# Initialize model with callback
# -------------------------
def create_model_with_tracking(agent_name: str):
    """Create a model instance with token tracking"""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )
    return model

# -------------------------
# Enhanced logging function
# -------------------------
async def log_status(message: str, level: str = "INFO", agent: str = "SYSTEM", status_callback=None):
    """Enhanced logging with levels and agent identification"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] [{agent}] {message}"
    
    if level == "INFO":
        logger.info(formatted_msg)
    elif level == "ERROR":
        logger.error(formatted_msg)
    elif level == "WARNING":
        logger.warning(formatted_msg)
    elif level == "DEBUG":
        logger.debug(formatted_msg)
    
    if status_callback:
        await status_callback(formatted_msg)
    await asyncio.sleep(0)

# -------------------------
# Enhanced agent runner with detailed logging
# -------------------------
async def run_agent(
    server_path: str, 
    input_data: dict, 
    system_prompt: str, 
    agent_name: str,
    status_callback: Optional[Callable] = None
) -> dict:
    """
    Runs an MCP agent with comprehensive logging and metrics tracking
    """
    await log_status(f"Initializing {agent_name} agent...", agent=agent_name, status_callback=status_callback)
    await log_status(f"Server path: {server_path}", level="DEBUG", agent=agent_name, status_callback=status_callback)
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path]
    )

    tool_calls_count = 0
    iteration_count = 0

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            try:
                await session.initialize()
                await log_status("MCP session initialized successfully", agent=agent_name, status_callback=status_callback)
                
                tools = await load_mcp_tools(session)
                await log_status(f"Loaded {len(tools)} tools: {list(tools.keys())}", agent=agent_name, status_callback=status_callback)
                
                model = create_model_with_tracking(agent_name)
                agent = create_agent(model, tools)

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=json.dumps(input_data, indent=2))
                ]
                
                await log_status(f"Starting agent execution loop", agent=agent_name, status_callback=status_callback)
                await log_status(f"Input data keys: {list(input_data.keys())}", level="DEBUG", agent=agent_name, status_callback=status_callback)

                # ---- ENHANCED TOOL EXECUTION LOOP ----
                while True:
                    iteration_count += 1
                    await log_status(f"Iteration #{iteration_count}", level="DEBUG", agent=agent_name, status_callback=status_callback)
                    
                    # Record API call (estimate tokens based on message length)
                    input_tokens = sum(len(str(m.content)) // 4 for m in messages)  # Rough estimate
                    
                    result = await agent.ainvoke({"messages": messages})
                    last_msg = result["messages"][-1]
                    
                    # Estimate output tokens
                    output_tokens = len(str(last_msg.content)) // 4
                    metrics_tracker.record_api_call(agent_name, input_tokens, output_tokens)

                    # If the assistant is calling a tool:
                    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                        for tool_call in last_msg.tool_calls:
                            tool_calls_count += 1
                            tool_name = tool_call.get('name', 'unknown')
                            args = tool_call.get('args', {})
                            
                            await log_status(
                                f"Tool call #{tool_calls_count}: {tool_name} with args: {json.dumps(args, indent=2)[:100]}...",
                                agent=agent_name,
                                status_callback=status_callback
                            )

                            tool_fn = tools.get(tool_name)
                            if tool_fn is None:
                                error_msg = f"Unknown tool: {tool_name}"
                                await log_status(error_msg, level="ERROR", agent=agent_name, status_callback=status_callback)
                                raise RuntimeError(error_msg)

                            # Execute tool
                            try:
                                tool_output = await tool_fn.ainvoke(args)
                                await log_status(
                                    f"Tool {tool_name} executed successfully. Output length: {len(str(tool_output))} chars",
                                    agent=agent_name,
                                    status_callback=status_callback
                                )
                            except Exception as e:
                                error_msg = f"Tool execution failed: {str(e)}"
                                await log_status(error_msg, level="ERROR", agent=agent_name, status_callback=status_callback)
                                raise

                            # Append tool result back to agent
                            messages.append(
                                ToolMessage(
                                    content=str(tool_output),
                                    tool_call_id=tool_call.get('id', '')
                                )
                            )
                        continue

                    # No more tools → final answer
                    await log_status(
                        f"Agent completed after {iteration_count} iterations and {tool_calls_count} tool calls",
                        agent=agent_name,
                        status_callback=status_callback
                    )
                    
                    final_response = {
                        "raw": last_msg.content,
                        "metadata": {
                            "iterations": iteration_count,
                            "tool_calls": tool_calls_count,
                            "agent": agent_name
                        }
                    }
                    
                    await log_status(f"Final response length: {len(last_msg.content)} chars", agent=agent_name, status_callback=status_callback)
                    return final_response
                    
            except Exception as e:
                error_msg = f"Agent execution failed: {str(e)}"
                await log_status(error_msg, level="ERROR", agent=agent_name, status_callback=status_callback)
                raise

# -------------------------
# Enhanced multi-agent workflow
# -------------------------
async def run_system(description: str, requirements: str, status_callback=None):
    """
    Run the complete multi-agent workflow with comprehensive tracking
    """
    metrics_tracker.start_tracking()
    
    await log_status("="*70, agent="SYSTEM", status_callback=status_callback)
    await log_status("MULTI-AGENT SYSTEM EXECUTION STARTED", agent="SYSTEM", status_callback=status_callback)
    await log_status("="*70, agent="SYSTEM", status_callback=status_callback)
    
    input_data = {
        "description": description,
        "requirements": requirements
    }
    
    await log_status(f"Project Description: {description[:100]}...", agent="SYSTEM", status_callback=status_callback)
    await log_status(f"Requirements: {requirements[:100]}...", agent="SYSTEM", status_callback=status_callback)

    try:
        # === PLANNER AGENT ===
        await log_status("\n" + "="*70, agent="SYSTEM", status_callback=status_callback)
        await log_status("PHASE 1: PLANNING", agent="SYSTEM", status_callback=status_callback)
        await log_status("="*70, agent="SYSTEM", status_callback=status_callback)
        
        planner_output = await run_agent(
            "agents/planner_server.py", 
            input_data, 
            "You are a planner agent. Create a detailed, structured plan for this software based on the requirements provided.",
            "planner",
            status_callback
        )
        await log_status("Planner phase completed successfully", agent="SYSTEM", status_callback=status_callback)

        # === DEVELOPER AGENT ===
        await log_status("\n" + "="*70, agent="SYSTEM", status_callback=status_callback)
        await log_status("PHASE 2: DEVELOPMENT", agent="SYSTEM", status_callback=status_callback)
        await log_status("="*70, agent="SYSTEM", status_callback=status_callback)
        await log_status("Passing planner output to developer...", agent="SYSTEM", status_callback=status_callback)
        
        developer_output = await run_agent(
            "agents/developer_server.py", 
            {"planner_output": planner_output, "original_requirements": input_data}, 
            "You are a software developer. Given this plan, create a comprehensive README and a fully functional application with a local host version that can be deployed.",
            "developer",
            status_callback
        )
        await log_status("Developer phase completed successfully", agent="SYSTEM", status_callback=status_callback)

        # === TESTER AGENT ===
        await log_status("\n" + "="*70, agent="SYSTEM", status_callback=status_callback)
        await log_status("PHASE 3: TESTING", agent="SYSTEM", status_callback=status_callback)
        await log_status("="*70, agent="SYSTEM", status_callback=status_callback)
        await log_status("Passing developer output to tester...", agent="SYSTEM", status_callback=status_callback)
        
        tester_output = await run_agent(
            "agents/tester_server.py", 
            {"developer_output": developer_output, "planner_output": planner_output}, 
            "You are a software tester. Examine the files in the generated folder, write comprehensive test cases, and execute them to identify any bugs or issues.",
            "tester",
            status_callback
        )
        await log_status("Tester phase completed successfully", agent="SYSTEM", status_callback=status_callback)

        # === COMPLETION ===
        metrics_tracker.end_tracking()
        
        await log_status("\n" + "="*70, agent="SYSTEM", status_callback=status_callback)
        await log_status("ALL PHASES COMPLETED SUCCESSFULLY", agent="SYSTEM", status_callback=status_callback)
        await log_status("="*70, agent="SYSTEM", status_callback=status_callback)
        
        # Print metrics summary
        metrics_tracker.print_summary()
        
        return {
            "plan": planner_output,
            "code": developer_output,
            "tests": tester_output,
            "metrics": metrics_tracker.get_summary()
        }
        
    except Exception as e:
        metrics_tracker.end_tracking()
        await log_status(f"SYSTEM EXECUTION FAILED: {str(e)}", level="ERROR", agent="SYSTEM", status_callback=status_callback)
        metrics_tracker.print_summary()
        raise

# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":
    description = input("Software description: ")
    requirements = input("Requirements: ")
    result = asyncio.run(run_system(description, requirements))

    print("\n" + "="*70)
    print("FINAL OUTPUTS")
    print("="*70)
    print("\n--- PLAN ---\n", json.dumps(result["plan"], indent=2))
    print("\n--- CODE ---\n", json.dumps(result["code"], indent=2))
    print("\n--- TESTS ---\n", json.dumps(result["tests"], indent=2))
    print("\n--- METRICS ---\n", json.dumps(result["metrics"], indent=2))