import json
import gradio as gr
import asyncio
from core.system_runner2 import run_system  # build_agent + workflow

# Gradio interface function (synchronous from Gradio's perspective)
def interface_fn(description, requirements):
    # run_system prints status in console
    result = asyncio.run(run_system(description, requirements))
    # return plan, code, tests as separate outputs
        # Convert dict outputs to formatted strings
    plan_str = json.dumps(result["plan"]["raw"], indent=2)
    code_str = json.dumps(result["code"]["raw"], indent=2)
    tests_str = json.dumps(result["tests"]["raw"], indent=2)
    return plan_str, code_str, tests_str

with gr.Blocks(title="MCP Multi-Agent Software Generator") as app:
    gr.Markdown("# Multi-Agent MCP Software Generator")

    # Inputs
    desc_input = gr.Textbox(label="Software Description", lines=4, value="""Customer Feedback Tracker is a business software application that allows businesses to collect and analyze customer feedback. The software provides a user-friendly interface for businesses to create and manage feedback forms, distribute them to customers via email or social media platforms, and collect responses. It also offers data visualization tools to analyze feedback data, identify trends and patterns, and generate actionable insights for improving products and services.""")
    req_input = gr.Textbox(label="Requirements", lines=4)
    run_btn = gr.Button("Generate Software")

    # Outputs
    plan_out = gr.Textbox(label="Planner Output")
    code_out = gr.Code(label="Generated Code")
    tests_out = gr.Code(label="Generated Tests")

    # Hook up button
    run_btn.click(
        fn=interface_fn,
        inputs=[desc_input, req_input],
        outputs=[plan_out, code_out, tests_out]
    )

app.launch()
