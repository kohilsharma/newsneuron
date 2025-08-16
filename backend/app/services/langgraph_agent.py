"""
LangGraph Agent for NewsNeuron
Orchestrates AI reasoning with hybrid retrieval capabilities
"""
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai

from app.config import settings
from app.services.hybrid_retriever import HybridRetriever


class LangGraphAgent:
    """
    LangGraph-based AI agent for NewsNeuron
    Handles conversational AI with hybrid retrieval context
    """
    
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever
        self.conversation_history = {}  # In-memory storage for now
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        else:
            print("Warning: OpenAI API key not configured")
    
    async def process_message(
        self,
        message: str,
        conversation_id: str,
        use_hybrid_search: bool = True,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message through the LangGraph agent
        
        Args:
            message: User message
            conversation_id: Conversation identifier
            use_hybrid_search: Whether to use hybrid retrieval
            user_id: Optional user identifier
        
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
            
            # Analyze query and determine approach
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
            
            return {
                "entities": entities,
                "intent": intent,
                "requires_search": any([
                    "what", "who", "when", "where", "how", "why",
                    "tell me", "find", "search", "show me"
                ]) in message.lower(),
                "is_temporal": any([
                    "recent", "latest", "today", "yesterday", "this week",
                    "timeline", "history", "evolution"
                ]) in message.lower()
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
        Generate response using LLM with context
        
        Args:
            message: User message
            conversation_history: Previous conversation
            context: Retrieved context
            query_analysis: Query analysis results
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            if not settings.openai_api_key:
                return {
                    "response": "I'm a NewsNeuron AI assistant. I can help you analyze news, create flashcards, explore timelines, and answer questions about current events. However, I need an OpenAI API key to be configured to provide intelligent responses.",
                    "sources": [],
                    "entities_mentioned": []
                }
            
            # Build system prompt
            system_prompt = self._build_system_prompt(query_analysis)
            
            # Build context prompt
            context_prompt = self._build_context_prompt(context)
            
            # Build conversation messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add recent conversation history (last 5 exchanges)
            recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            for exchange in recent_history[:-1]:  # Exclude current message
                if exchange["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": exchange["role"],
                        "content": exchange["content"]
                    })
            
            # Add context and current message
            user_message_with_context = f"{context_prompt}\n\nUser Question: {message}"
            messages.append({"role": "user", "content": user_message_with_context})
            
            # Generate response using OpenAI
            response = await openai.ChatCompletion.acreate(
                model=settings.default_llm_model.replace("openai/", ""),
                messages=messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )
            
            ai_response = response.choices[0].message.content
            
            # Extract metadata
            sources = self._extract_sources(context)
            entities_mentioned = query_analysis.get("entities", [])
            
            return {
                "response": ai_response,
                "sources": sources,
                "entities_mentioned": entities_mentioned
            }
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error while generating a response. Error: {str(e)}",
                "sources": [],
                "entities_mentioned": []
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
