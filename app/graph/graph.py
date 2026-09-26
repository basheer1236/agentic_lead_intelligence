from langgraph.graph import END, START, StateGraph

from app.graph.state import LeadIntelligenceState
from app.graph.nodes import (
    initialize_node,
    relevance_node,
    project_node,
    rug_node,
    designer_resolution_node,
    designer_enrichment_node,
    lead_intelligence_node,
    persistence_node,
    route_enrichment_gate,
)


def route_after_relevance(state: LeadIntelligenceState):
    if state.get("article_relevant") is True:
        return "project_intelligence"

    return END


def build_graph():

    builder = StateGraph(LeadIntelligenceState)

    # -----------------------------------------
    # Nodes
    # -----------------------------------------

    builder.add_node("initialize", initialize_node)
    builder.add_node("relevance", relevance_node)
    builder.add_node("project_intelligence", project_node)
    builder.add_node("rug_intelligence", rug_node)
    builder.add_node("designer_resolution", designer_resolution_node)
    builder.add_node("designer_enrichment", designer_enrichment_node)
    builder.add_node("lead_intelligence", lead_intelligence_node)
    builder.add_node("persistence", persistence_node)

    # -----------------------------------------
    # Start
    # -----------------------------------------

    builder.add_edge(START, "initialize")
    builder.add_edge("initialize", "relevance")

    # -----------------------------------------
    # Relevance routing
    # -----------------------------------------

    builder.add_conditional_edges(
        "relevance",
        route_after_relevance,
        {
            "project_intelligence": "project_intelligence",
            END: END,
        },
    )

    # -----------------------------------------
    # Intelligence pipeline
    # -----------------------------------------

    builder.add_edge("project_intelligence", "rug_intelligence")
    builder.add_edge("rug_intelligence", "designer_resolution")

    # -----------------------------------------
    # Enrichment Gate Routing
    # -----------------------------------------

    builder.add_conditional_edges(
        "designer_resolution",
        route_enrichment_gate,
        {
            "enrich_designer": "designer_enrichment",
            "skip_enrichment": "lead_intelligence",
        },
    )

    builder.add_edge("designer_enrichment", "lead_intelligence")
    builder.add_edge("lead_intelligence", "persistence")

    # -----------------------------------------
    # End
    # -----------------------------------------

    builder.add_edge("persistence", END)

    return builder.compile()


graph = build_graph()