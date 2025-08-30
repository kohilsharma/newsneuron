from __future__ import annotations

from typing import Any

from app.services.hybrid_retriever import HybridRetriever
from .state import AgentState


class QueryAnalyzerNode:
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever

    async def __call__(self, state: AgentState) -> AgentState:
        query = state.get("user_query", "")
        entities = self.retriever.extract_entities(query)
        # Basic intent heuristic mirrors existing implementation
        q = query.lower()
        if any(w in q for w in ["timeline", "history", "evolution", "over time"]):
            intent = "timeline"
        elif any(w in q for w in ["summary", "summarize", "flashcard", "brief"]):
            intent = "summary"
        elif any(w in q for w in ["search", "find", "show me", "look for"]):
            intent = "search"
        elif any(w in q for w in ["related", "connected", "similar"]):
            intent = "relationship"
        else:
            intent = "general"
        state["intent"] = intent
        state["entities"] = entities
        return state


class VectorRetrieverNode:
    def __init__(self, retriever: HybridRetriever, limit: int = 8):
        self.retriever = retriever
        self.limit = limit

    async def __call__(self, state: AgentState) -> AgentState:
        query = state.get("user_query", "")
        vr = await self.retriever.vector_search(query, limit=self.limit)
        state["vector_results"] = vr
        return state


class GraphRetrieverNode:
    def __init__(self, retriever: HybridRetriever, max_depth: int = 2):
        self.retriever = retriever
        self.max_depth = max_depth

    async def __call__(self, state: AgentState) -> AgentState:
        entities = state.get("entities", [])
        if entities:
            gr = await self.retriever.graph_search(entities, max_depth=self.max_depth)
        else:
            gr = []
        state["graph_results"] = gr
        return state


class SynthesizerNode:
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever

    async def __call__(self, state: AgentState) -> AgentState:
        vr = state.get("vector_results", [])
        gr = state.get("graph_results", [])
        state["synthesized_context"] = self.retriever.synthesize_results(vr, gr)
        return state


class ResponseGeneratorNode:
    def __init__(self, agent: Any):
        self.agent = agent

    async def __call__(self, state: AgentState) -> AgentState:
        # Reuse agent's response generation with provided context
        query = state.get("user_query", "")
        conversation_history = []  # Empty history for workflow calls
        context = {
            "articles": state.get("vector_results", []),
            "graph_results": state.get("graph_results", []),
            "query_entities": state.get("entities", []),
        }
        query_analysis = {"entities": state.get("entities", []), "intent": state.get("intent", "general")}
        result = await self.agent._generate_response(query, conversation_history, context, query_analysis)
        state["response_text"] = result.get("response", "")
        return state


