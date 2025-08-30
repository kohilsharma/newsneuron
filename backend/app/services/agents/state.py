from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """State dictionary carried across LangGraph nodes."""
    user_query: str
    intent: str
    entities: List[str]
    vector_results: List[Dict[str, Any]]
    graph_results: List[Dict[str, Any]]
    synthesized_context: str
    response_text: str
    error: str


