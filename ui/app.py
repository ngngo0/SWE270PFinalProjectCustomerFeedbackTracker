import json
import gradio as gr
import asyncio
from core.system_runner2 import run_system  # build_agent + workflow

def format_metrics(metrics_data: dict) -> str:
    """Format metrics data into a readable string"""
    if not metrics_data:
        return "No metrics available"
    
    metrics = metrics_data.get('metrics', {})
    duration = metrics_data.get('execution_time_seconds', 0)
    
    output = []
    output.append("="*70)
    output.append("MULTI-AGENT SYSTEM METRICS SUMMARY")
    output.append("="*70)
    output.append(f"Total Execution Time: {duration:.2f} seconds")
    output.append(f"Total API Calls: {metrics['total']['api_calls']}")
    output.append(f"Total Tokens Used: {metrics['total']['total_tokens']:,}")
    output.append(f"   - Input Tokens: {metrics['total']['input_tokens']:,}")
    output.append(f"   - Output Tokens: {metrics['total']['output_tokens']:,}")
    output.append("\n" + "-"*70)
    output.append("Per-Agent Breakdown:")
    output.append("-"*70)
    
    for agent in ['planner', 'developer', 'tester']:
        agent_metrics = metrics.get(agent, {})
        output.append(f"\n {agent.upper()} Agent:")
        output.append(f"   API Calls: {agent_metrics.get('api_calls', 0)}")
        output.append(f"   Total Tokens: {agent_metrics.get('total_tokens', 0):,}")
        output.append(f"   - Input: {agent_metrics.get('input_tokens', 0):,}")
        output.append(f"   - Output: {agent_metrics.get('output_tokens', 0):,}")
    
    output.append("\n" + "="*70)
    
    return "\n".join(output)

# Gradio interface function (synchronous from Gradio's perspective)
def interface_fn(description, requirements):
    """Main interface function that runs the multi-agent system"""
    try:
        # Run the system and get results
        result = asyncio.run(run_system(description, requirements))
        
        # Extract outputs
        plan_data = result.get("plan", {})
        code_data = result.get("code", {})
        tests_data = result.get("tests", {})
        metrics_data = result.get("metrics", {})
        
        # Format plan output
        plan_str = json.dumps(plan_data.get("raw", ""), indent=2)
        if "metadata" in plan_data:
            plan_str += f"\n\n--- Metadata ---\n{json.dumps(plan_data['metadata'], indent=2)}"
        
        # Format code output
        code_str = json.dumps(code_data.get("raw", ""), indent=2)
        if "metadata" in code_data:
            code_str += f"\n\n--- Metadata ---\n{json.dumps(code_data['metadata'], indent=2)}"
        
        # Format tests output
        tests_str = json.dumps(tests_data.get("raw", ""), indent=2)
        if "metadata" in tests_data:
            tests_str += f"\n\n--- Metadata ---\n{json.dumps(tests_data['metadata'], indent=2)}"
        
        # Format metrics
        metrics_str = format_metrics(metrics_data)
        
        return plan_str, code_str, tests_str, metrics_str
        
    except Exception as e:
        error_msg = f"Error occurred: {str(e)}\n\nPlease check the logs for more details."
        return error_msg, error_msg, error_msg, error_msg

# Create the Gradio interface (without custom CSS for compatibility)
with gr.Blocks(title="MCP Multi-Agent Software Generator") as app:
    gr.Markdown(
        """
        # Multi-Agent MCP Software Generator
        
        This system uses three specialized agents to generate complete software applications:
        - **Planner Agent**: Creates a structured project plan
        - **Developer Agent**: Generates executable code and documentation
        - **Tester Agent**: Creates and runs comprehensive test cases
        
        All agent communications and metrics are tracked and logged.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            # Inputs
            desc_input = gr.Textbox(
                label="Software Description", 
                lines=6,
                placeholder="Describe the software application you want to build...",
                value="""Customer Feedback Tracker is a business software application that allows businesses to collect and analyze customer feedback. The software provides a user-friendly interface for businesses to create and manage feedback forms, distribute them to customers via email or social media platforms, and collect responses. It also offers data visualization tools to analyze feedback data, identify trends and patterns, and generate actionable insights for improving products and services."""
            )
            
            req_input = gr.Textbox(
                label="Requirements (Optional)", 
                lines=4,
                placeholder="List any specific requirements or features..."
            )
            
            run_btn = gr.Button("🚀 Generate Software", variant="primary", size="lg")
            
            gr.Markdown(
                """
                ### Tips:
                - Be specific in your description
                - The process may take a few minutes
                - Check the console for real-time logs
                - Check `agent_communication.log` for detailed logs
                """
            )

    with gr.Row():
        with gr.Column():
            # Outputs
            with gr.Tab("Metrics & Performance"):
                metrics_out = gr.Textbox(
                    label="System Metrics",
                    lines=20,
                    max_lines=30
                )
            
            with gr.Tab("Planner Output"):
                plan_out = gr.Code(
                    label="Generated Plan",
                    language="json",
                    lines=20
                )
            
            with gr.Tab("Developer Output"):
                code_out = gr.Code(
                    label="Generated Code",
                    language="json",
                    lines=20
                )
            
            with gr.Tab("Tester Output"):
                tests_out = gr.Code(
                    label="Generated Tests",
                    language="json",
                    lines=20
                )

    # Hook up button
    run_btn.click(
        fn=interface_fn,
        inputs=[desc_input, req_input],
        outputs=[plan_out, code_out, tests_out, metrics_out]
    )
    
    gr.Markdown(
        """
        ---
        ### Log Files:
        - **agent_communication.log**: Detailed logs of all agent communications and tool calls
        - Check console output for real-time status updates
        """
    )

app.launch()