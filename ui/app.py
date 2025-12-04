import gradio as gr
import asyncio
from core.system_runner2 import run_system  # build_agent + workflow

# Gradio interface function (synchronous from Gradio's perspective)
def interface_fn(description, requirements):
    # run_system prints status in console
    result = asyncio.run(run_system(description, requirements))
    # return plan, code, tests as separate outputs
    return result["plan"], result["code"], result["tests"]

with gr.Blocks(title="MCP Multi-Agent Software Generator") as app:
    gr.Markdown("# Multi-Agent MCP Software Generator")

    # Inputs
    desc_input = gr.Textbox(label="Software Description", lines=4)
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
