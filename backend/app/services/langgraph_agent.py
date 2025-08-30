"""
LangGraph Agent for NewsNeuron
Orchestrates AI reasoning with hybrid retrieval capabilities
"""
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import settings
from app.services.hybrid_retriever import HybridRetriever
from app.services.openrouter_client import get_openrouter_client
from app.services.enhanced_rag_prompt import EnhancedRAGFormatter


class LangGraphAgent:
    """
    LangGraph-based AI agent for NewsNeuron
    Handles conversational AI with hybrid retrieval context
    """

    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever
        self.conversation_history = {}  # In-memory storage for now
        # Use our custom OpenRouter client (no OpenAI dependency)
        self.openrouter_client = get_openrouter_client()

    async def process_message(
        self,
        message: str,
        conversation_id: str,
        use_hybrid_search: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a chat message through the LangGraph agent
        
        Args:
            message: User message
            conversation_id: Conversation identifier
            use_hybrid_search: Whether to use hybrid retrieval
        
        Returns:
            Dictionary with response and context information
        """
        try:
            # Initialize conversation history if needed
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []

            # Add user message to history
            self.conversation_history[conversation_id].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })

            # Prefer LangGraph workflow if available
            try:
                from app.services.agents.state import AgentState
                from app.services.agents.workflow import build_agent_workflow

                workflow = build_agent_workflow(self.retriever, self)
                state = {"user_query": message}
                result_state = await workflow.ainvoke(state)

                response = {
                    "response": result_state.get("response_text", ""),
                    "sources": self._extract_sources({
                        "articles": result_state.get("vector_results", []),
                        "graph_results": result_state.get("graph_results", []),
                        "query_entities": result_state.get("entities", []),
                    }),
                    "entities_mentioned": result_state.get("entities", [])
                }
            except Exception:
                # Analyze query and determine approach (fallback)
                query_analysis = await self._analyze_query(message)

                # Gather context using hybrid retrieval
                context = {}
                if use_hybrid_search:
                    context = await self._gather_context(message, query_analysis)

                # Generate response using LLM
                response = await self._generate_response(
                    message=message,
                    conversation_history=self.conversation_history[conversation_id],
                    context=context,
                    query_analysis=query_analysis
                )

            # Add assistant response to history
            self.conversation_history[conversation_id].append({
                "role": "assistant",
                "content": response["response"],
                "timestamp": datetime.now().isoformat(),
                "sources": response.get("sources", []),
                "entities_mentioned": response.get("entities_mentioned", [])
            })

            # Limit conversation history to prevent memory issues
            if len(self.conversation_history[conversation_id]) > 20:
                self.conversation_history[conversation_id] = \
                    self.conversation_history[conversation_id][-20:]

            return response

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error while processing your message. Please try again.",
                "sources": [],
                "entities_mentioned": []
            }

    async def _analyze_query(self, message: str) -> Dict[str, Any]:
        """
        Analyze user query to determine intent and entities
        
        Args:
            message: User message to analyze
        
        Returns:
            Dictionary with query analysis results
        """
        try:
            # Extract entities using retriever
            entities = self.retriever.extract_entities(message)

            # Simple intent classification (can be enhanced with ML models)
            intent = self._classify_intent(message)

            message_lower = message.lower()
            return {
                "entities": entities,
                "intent": intent,
                "requires_search": any(kw in message_lower for kw in [
                    "what", "who", "when", "where", "how", "why",
                    "tell me", "find", "search", "show me"
                ]),
                "is_temporal": any(kw in message_lower for kw in [
                    "recent", "latest", "today", "yesterday", "this week",
                    "timeline", "history", "evolution"
                ])
            }

        except Exception as e:
            print(f"Error analyzing query: {str(e)}")
            return {
                "entities": [],
                "intent": "general",
                "requires_search": True,
                "is_temporal": False
            }

    def _classify_intent(self, message: str) -> str:
        """
        Classify user intent based on message content
        
        Args:
            message: User message
        
        Returns:
            Intent category string
        """
        message_lower = message.lower()

        if any(word in message_lower for word in ["timeline", "history", "evolution", "over time"]):
            return "timeline"
        elif any(word in message_lower for word in ["summary", "summarize", "flashcard", "brief"]):
            return "summary"
        elif any(word in message_lower for word in ["search", "find", "look for", "show me"]):
            return "search"
        elif any(word in message_lower for word in ["explain", "what is", "tell me about"]):
            return "explanation"
        elif any(word in message_lower for word in ["related", "connected", "similar"]):
            return "relationship"
        else:
            return "general"

    async def _gather_context(
        self,
        message: str,
        query_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gather context using hybrid retrieval
        
        Args:
            message: User message
            query_analysis: Results from query analysis
        
        Returns:
            Dictionary with gathered context
        """
        try:
            context = {
                "articles": [],
                "entities": [],
                "graph_results": []
            }

            if not query_analysis.get("requires_search"):
                return context

            # Determine search strategy based on intent
            intent = query_analysis.get("intent", "general")

            if intent == "timeline" and query_analysis.get("entities"):
                # Focus on graph search for timeline queries
                search_results = await self.retriever.hybrid_search(
                    query=message,
                    search_type="graph",
                    limit=10,
                    include_entities=True
                )
            elif intent in ["search", "explanation"]:
                # Use hybrid search for comprehensive results
                search_results = await self.retriever.hybrid_search(
                    query=message,
                    search_type="hybrid",
                    limit=8,
                    include_entities=True
                )
            else:
                # Default to vector search
                search_results = await self.retriever.hybrid_search(
                    query=message,
                    search_type="vector",
                    limit=5,
                    include_entities=True
                )

            context.update(search_results)

            return context

        except Exception as e:
            print(f"Error gathering context: {str(e)}")
            return {
                "articles": [],
                "entities": [],
                "graph_results": []
            }

    async def _generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        context: Dict[str, Any],
        query_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate response using enhanced RAG prompt with strict source grounding
        
        Args:
            message: User message
            conversation_history: Previous conversation
            context: Retrieved context
            query_analysis: Query analysis results
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            if not self.openrouter_client.is_available():
                return {
                    "response": "I'm a NewsNeuron AI assistant. Configure OPENROUTER_API_KEY to enable intelligent responses.",
                    "sources": [],
                    "entities_mentioned": [],
                    "rag_quality": {"error": "OpenRouter not available"}
                }

            # Extract articles from context
            articles = context.get("articles", [])
            
            # If no articles found, return appropriate response
            if not articles:
                return {
                    "response": "Based on the provided articles, there is insufficient information to answer this question.",
                    "sources": [],
                    "entities_mentioned": query_analysis.get("entities", []),
                    "rag_quality": {"no_sources": True}
                }

            # Generate enhanced RAG prompt with strict citation requirements
            user_intent = query_analysis.get("intent", "general")
            enhanced_prompt = EnhancedRAGFormatter.generate_prompt(
                articles=articles,
                question=message,
                intent=user_intent
            )

            # Build conversation messages with enhanced RAG approach
            messages = [
                {"role": "user", "content": enhanced_prompt}
            ]

            # Generate response using OpenRouter
            response = await self.openrouter_client.chat_completion(
                messages=messages,
                model=settings.default_llm_model,
                max_tokens=settings.max_tokens,
                temperature=0.3  # Lower temperature for more factual responses
            )

            ai_response = self.openrouter_client.extract_message_content(response)

            # Extract enhanced sources with validation
            sources = self._extract_enhanced_sources(context)
            entities_mentioned = query_analysis.get("entities", [])
            
            # Validate RAG response quality
            rag_quality = EnhancedRAGFormatter.validate_response(ai_response, articles)
            
            # Add source summary for transparency
            source_summary = EnhancedRAGFormatter.create_source_summary(articles)

            return {
                "response": ai_response,
                "sources": sources,
                "entities_mentioned": entities_mentioned,
                "rag_quality": rag_quality,
                "source_summary": source_summary,
                "model_used": settings.default_llm_model,
                "articles_used": len(articles)
            }

        except Exception as e:
            print(f"Error generating enhanced RAG response: {str(e)}")
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "sources": [],
                "entities_mentioned": [],
                "rag_quality": {"error": str(e)}
            }

    def _build_system_prompt(self, query_analysis: Dict[str, Any]) -> str:
        """Build system prompt based on query analysis"""
        intent = query_analysis.get("intent", "general")

        base_prompt = """You are NewsNeuron, an AI assistant specialized in news analysis and information retrieval. You combine semantic understanding with knowledge graph relationships to provide comprehensive, contextual answers about current events and news.

Your capabilities include:
- Analyzing news articles and extracting key insights
- Understanding relationships between entities (people, organizations, locations, events)
- Creating timeline visualizations of story evolution
- Generating concise flashcard summaries
- Performing semantic search across news content

Always be:
- Accurate and fact-based
- Concise but comprehensive
- Clear about sources and confidence levels
- Helpful in suggesting related information or follow-up questions"""

        if intent == "timeline":
            base_prompt += "\n\nThe user is asking about timeline or chronological information. Focus on dates, sequence of events, and story evolution."
        elif intent == "summary":
            base_prompt += "\n\nThe user wants a summary or flashcard-style information. Provide concise, structured key points."
        elif intent == "relationship":
            base_prompt += "\n\nThe user is interested in relationships and connections. Highlight how entities, events, or topics are related."

        return base_prompt

    def _build_context_prompt(self, context: Dict[str, Any]) -> str:
        """Build context prompt from retrieved information"""
        if not context or not any(context.values()):
            return "Context: No specific articles or entities found for this query."

        context_parts = []

        # Add articles context
        articles = context.get("articles", [])
        if articles:
            context_parts.append("Relevant Articles:")
            for i, article in enumerate(articles[:5], 1):
                title = article.get("title", "Unknown")
                source = article.get("source", "Unknown source")
                context_parts.append(f"{i}. {title} (Source: {source})")

                # Add snippet of content if available
                content = article.get("content", "")
                if content:
                    snippet = content[:200] + "..." if len(content) > 200 else content
                    context_parts.append(f"   Summary: {snippet}")

        # Add entities context
        entities = context.get("query_entities", [])
        if entities:
            context_parts.append(f"Identified Entities: {', '.join(entities)}")

        # Add graph results context
        graph_results = context.get("graph_results", [])
        if graph_results:
            context_parts.append("Entity Relationships:")
            for result in graph_results[:3]:
                entity = result.get("entity", "Unknown")
                related = result.get("related_entities", [])
                if related:
                    related_names = [r.get("name", "") for r in related[:3]]
                    context_parts.append(f"  {entity} is related to: {', '.join(related_names)}")

        return "\n".join(context_parts) if context_parts else "Context: Limited information available."

    def _extract_sources(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract source information from context"""
        sources = []
        articles = context.get("articles", [])

        for article in articles[:5]:  # Limit to 5 sources
            source = {
                "title": article.get("title", "Unknown"),
                "url": article.get("url"),
                "source": article.get("source"),
                "published_date": article.get("published_date"),
                "id": article.get("id")
            }
            sources.append(source)

        return sources
    
    def _extract_enhanced_sources(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract enhanced source information with additional metadata for citation validation"""
        sources = []
        articles = context.get("articles", [])

        for article in articles[:5]:  # Limit to 5 sources
            title = article.get("title", "Unknown")
            source_name = title  # This will be used for citation matching
            
            source = {
                "title": title,
                "source_name": source_name,  # For citation validation
                "url": article.get("url"),
                "source": article.get("source"),
                "published_date": article.get("published_date"),
                "id": article.get("id"),
                "similarity_score": article.get("similarity_score"),
                "snippet": article.get("content", "")[:200] + "..." if article.get("content") else None
            }
            sources.append(source)

        return sources
