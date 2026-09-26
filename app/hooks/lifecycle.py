"""
Lifecycle hooks for graph node execution monitoring and iteration limit enforcement.
"""

from app.config.settings import settings
from app.errors import StateValidationError


def pre_node_hook(node_name: str, state: dict) -> dict:
    """
    Hook executed prior to running any graph node.
    Enforces maximum graph iteration limits.
    """
    iteration = state.get("iteration_count", 0) + 1
    max_iterations = getattr(settings, "max_agent_iterations", 5)

    if iteration > max_iterations:
        raise StateValidationError(
            f"Graph execution halted: maximum iterations ({max_iterations}) exceeded at node '{node_name}'."
        )

    state_copy = dict(state)
    state_copy["iteration_count"] = iteration
    return state_copy


def post_node_hook(node_name: str, node_output: dict, state: dict) -> dict:
    """
    Hook executed following graph node execution.
    Logs telemetry metadata.
    """
    tool_results = list(state.get("tool_results", []))
    tool_results.append({
        "hook": "post_node_hook",
        "node": node_name,
        "status": node_output.get("status", "completed"),
    })

    updated = dict(node_output)
    updated["tool_results"] = tool_results
    return updated
