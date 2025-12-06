from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Planner")

@mcp.tool()
def create_plan(requirements: str) -> str:
    """
    Generates a structured project plan from raw requirements.
    Splits requirements into milestones, features, tasks, and suggested files.
    Outputs JSON.
    """
    import json
    import re

    # Split requirements into lines
    lines = [line.strip() for line in requirements.split("\n") if line.strip()]

    # Naive feature extraction (can be replaced by LLM or NLP)
    features = []
    for line in lines:
        # extract phrases like "login system", "analytics dashboard", etc.
        matches = re.findall(r"\b[a-zA-Z\s]{2,}\b", line)
        features.extend(matches)

    # Remove duplicates
    features = list(dict.fromkeys(features))

    # Create milestones with tasks and suggested filenames
    milestones = []
    for feature in features:
        feature_clean = feature.lower().replace(" ", "_")
        milestones.append({
            "milestone": feature,
            "tasks": [f"Implement {feature}", f"Write tests for {feature}"],
            "files": [f"{feature_clean}.py", f"test_{feature_clean}.py"]
        })

    plan = {
        "features": features,
        "milestones": milestones
    }

    return json.dumps(plan, indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")
