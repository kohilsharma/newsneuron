from __future__ import annotations

from typing import Optional

from langgraph.graph import StateGraph

from app.services.hybrid_retriever import HybridRetriever
from app.services.langgraph_agent import LangGraphAgent
from .state import AgentState
from .nodes import (
    QueryAnalyzerNode,
    VectorRetrieverNode,
    GraphRetrieverNode,
    SynthesizerNode,
    ResponseGeneratorNode,
)


def build_agent_workflow(
    retriever: HybridRetriever,
    agent: LangGraphAgent,
) -> StateGraph:
    graph = StateGraph(AgentState)

    qa = QueryAnalyzerNode(retriever)
    vr = VectorRetrieverNode(retriever)
    gr = GraphRetrieverNode(retriever)
    syn = SynthesizerNode(retriever)
    rg = ResponseGeneratorNode(agent)

    graph.add_node("query_analyzer", qa)
    graph.add_node("vector_retriever", vr)
    graph.add_node("graph_retriever", gr)
    graph.add_node("synthesizer", syn)
    graph.add_node("response_generator", rg)

    graph.set_entry_point("query_analyzer")
    graph.add_edge("query_analyzer", "vector_retriever")
    graph.add_edge("query_analyzer", "graph_retriever")
    graph.add_edge("vector_retriever", "synthesizer")
    graph.add_edge("graph_retriever", "synthesizer")
    graph.add_edge("synthesizer", "response_generator")

    return graph.compile()


