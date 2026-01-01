"""
visualizer.py

Plugin module for visualizing pipeline structure and execution paths.
Outputs Mermaid diagrams that can be rendered in markdown viewers.
"""

def design_view(steps, output_path="pipeline_design.mmd"):
    """
    Generates a Mermaid diagram showing event-based and linear flow.

    Args:
        steps (list): Compiled step dicts.
        output_path (str): Path to write the Mermaid diagram.
    """
    edges = []

    for step in steps:
        name = step.get("name", step.get("action", "unnamed")).replace(" ", "_")

        # Event-based dependencies
        for source in step.get("on", [] if isinstance(step.get("on"), list) else [step.get("on")]):
            if source:
                edges.append(f"    {source} --> {name}")

        # Trigger-based forward chaining
        if "trigger" in step:
            edges.append(f"    {name} --> {step['trigger']}")

    if not edges:
        edges = [f"    {steps[i].get('name')} --> {steps[i+1].get('name')}" for i in range(len(steps)-1)]

    content = ["graph TD"]
    content.extend(edges)

    with open(output_path, "w") as f:
        f.write("\n".join(content))
    print(f"[Visualizer] Design written to {output_path}")


def execution_view(logs, output_path="pipeline_execution.mmd"):
    """
    Generates a Mermaid diagram based on executed steps and event traces.

    Args:
        logs (list): List of execution entries with 'name', 'result', 'fired_events'
        output_path (str): Path to output Mermaid diagram
    """
    content = ["graph TD"]
    for entry in logs:
        name = entry["name"].replace(" ", "_")
        label = f"{name}\\n{entry.get('result', '')}"
        if entry.get("error"):
            label += "\\n[ERROR]"
        content.append(f'    {name}["{label}"]')

        for event in entry.get("fired_events", []):
            content.append(f"    {name} --> {event}")

    with open(output_path, "w") as f:
        f.write("\n".join(content))
    print(f"[Visualizer] Execution view written to {output_path}")
