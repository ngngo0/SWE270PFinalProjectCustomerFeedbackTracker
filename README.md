# Final Project Group 12 Customer Feedback Tracker

Multi-agent system where agents communicate via the Model Context Protocol (MCP) to make a Customer Feedback Tracker App

[Canvas Instructions](https://canvas.eee.uci.edu/courses/75936/assignments/1675802)


The **Customer Feedback Tracker** app is a business software application that allows businesses to collect and analyze customer feedback. The software provides a user-friendly interface for businesses to create and manage feedback forms, distribute them to customers via email or social media platforms, and collect responses. It also offers data visualization tools to analyze feedback data, identify trends and patterns, and generate actionable insights for improving products and services.

### The core components of the project include:
1. Multi-Agent System with MCP Integration
   -  Design and implement a multi-agent system that uses the MCP for communication
between agents.
   -  Define the roles of each agent, the tools they have access to, and the collaboration
pattern among them.
   - Include the necessary tooling, servers, and clients required to support the MCP
framework.
2. User Interface
   - Receive the description and requirements of a software application.
   - Return executable code for the software application.
   - Return executable test cases corresponding to the generated code.
3. LLM Usage Tracking
   - Track and report the usage of the Large Language Model, including the number of API
calls and the total tokens used.

## For Devs:

- Reference folder: 
  - our A6 in class submission to guide our implementation

Run these in this order(these are for windows):

Create the venv environment:
`python -m venv venv`

Run the venv environment(windows):
`venv\Scripts\activate`

Download these:
`python -m pip install langchain-mcp-adapters gradio langgraph langchain-google-genai python-dotenv`

Check if these downloaded:
`python -c "import langchain_mcp_adapters; print('OK')"`

Start the ui:
`python -m ui.app`

Make sure to refresh the UI whenever you make changes to the `system_runner.py`