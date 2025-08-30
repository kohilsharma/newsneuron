"""
RAG-Enhanced Agent for NewsNeuron
Enhanced version with better RAG transparency and verification
"""
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import settings
from app.services.hybrid_retriever import HybridRetriever
from app.services.openrouter_client import get_openrouter_client


class RAGEnhancedAgent:
    """
    Enhanced LangGraph agent with better RAG transparency
    Shows exactly what context is retrieved and how it's used
    """

    def __init__(self, retriever: HybridRetriever, debug_mode: bool = True):
        self.retriever = retriever
        self.conversation_history = {}
        self.openrouter_client = get_openrouter_client()
        self.debug_mode = debug_mode

    async def process_message_with_rag_details(
        self,
        message: str,
        conversation_id: str,
        use_hybrid_search: bool = True,
        show_context: bool = True
    ) -> Dict[str, Any]:
        """
        Process message with detailed RAG information
        
        Args:
            message: User message
            conversation_id: Conversation identifier
            use_hybrid_search: Whether to use hybrid retrieval
            show_context: Whether to include retrieved context in response
        
        Returns:
            Enhanced response with RAG details
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

            # Step 1: Analyze query
            if self.debug_mode:
                print(f"🔍 Step 1: Analyzing query: '{message}'")
            
            query_analysis = await self._analyze_query(message)
            
            if self.debug_mode:
                print(f"   📝 Intent: {query_analysis.get('intent')}")
                print(f"   🏷️  Entities: {query_analysis.get('entities', [])}")
                print(f"   🔎 Requires search: {query_analysis.get('requires_search')}")

            # Step 2: Gather context
            rag_details = {
                "context_retrieved": False,
                "articles_found": 0,
                "entities_identified": [],
                "graph_results": 0,
                "context_used": "",
                "search_time": 0
            }

            context = {"articles": [], "entities": [], "graph_results": []}
            
            if use_hybrid_search:
                if self.debug_mode:
                    print(f"🔍 Step 2: Gathering context via hybrid search...")
                
                import time
                start_time = time.time()
                context = await self._gather_context(message, query_analysis)
                search_time = time.time() - start_time
                
                rag_details.update({
                    "context_retrieved": True,
                    "articles_found": len(context.get("articles", [])),
                    "entities_identified": context.get("query_entities", []),
                    "graph_results": len(context.get("graph_results", [])),
                    "search_time": search_time
                })
                
                if self.debug_mode:
                    print(f"   📚 Articles found: {rag_details['articles_found']}")
                    print(f"   🏷️  Entities: {rag_details['entities_identified']}")
                    print(f"   🔗 Graph results: {rag_details['graph_results']}")
                    print(f"   ⏱️  Search time: {search_time:.2f}s")

            # Step 3: Build enhanced context prompt
            if self.debug_mode:
                print(f"🔍 Step 3: Building context prompt...")
            
            context_prompt = self._build_enhanced_context_prompt(context, show_context)
            rag_details["context_used"] = context_prompt
            
            if self.debug_mode:
                print(f"   📄 Context prompt length: {len(context_prompt)} chars")

            # Step 4: Generate response
            if self.debug_mode:
                print(f"🔍 Step 4: Generating response...")
            
            response = await self._generate_enhanced_response(
                message=message,
                conversation_history=self.conversation_history[conversation_id],
                context=context,
                query_analysis=query_analysis,
                context_prompt=context_prompt
            )

            # Step 5: Add RAG transparency info
            if show_context and rag_details["context_retrieved"]:
                response["rag_details"] = rag_details
                response["context_preview"] = context_prompt[:500] + "..." if len(context_prompt) > 500 else context_prompt

            # Add assistant response to history
            self.conversation_history[conversation_id].append({
                "role": "assistant",
                "content": response["response"],
                "timestamp": datetime.now().isoformat(),
                "sources": response.get("sources", []),
                "entities_mentioned": response.get("entities_mentioned", []),
                "rag_used": rag_details["context_retrieved"]
            })

            if self.debug_mode:
                print(f"✅ Response generated with {len(response.get('sources', []))} sources")

            return response

        except Exception as e:
            print(f"❌ Error in RAG-enhanced processing: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "sources": [],
                "entities_mentioned": [],
                "rag_details": {"error": str(e)}
            }

    def _build_enhanced_context_prompt(self, context: Dict[str, Any], include_markers: bool = True) -> str:
        """
        Build enhanced context prompt with RAG markers for verification
        """
        if not context or not any(context.values()):
            return "Context: No specific articles or entities found for this query."

        context_parts = []
        
        if include_markers:
            context_parts.append("🔍 RETRIEVED CONTEXT (from NewsNeuron knowledge base):")
            context_parts.append("")

        # Add articles context with enhanced details
        articles = context.get("articles", [])
        if articles:
            context_parts.append("📚 Relevant Articles:")
            for i, article in enumerate(articles[:5], 1):
                title = article.get("title", "Unknown")
                source = article.get("source", "Unknown source")
                similarity = article.get("similarity_score")
                
                article_info = f"{i}. {title} (Source: {source}"
                if similarity:
                    article_info += f", Similarity: {similarity:.3f}"
                article_info += ")"
                context_parts.append(article_info)

                # Add content snippet
                content = article.get("content", "")
                if content:
                    snippet = content[:300] + "..." if len(content) > 300 else content
                    context_parts.append(f"   Content: {snippet}")
                
                context_parts.append("")

        # Add entities context
        entities = context.get("query_entities", [])
        if entities:
            context_parts.append(f"🏷️ Identified Entities: {', '.join(entities)}")
            context_parts.append("")

        # Add graph results context
        graph_results = context.get("graph_results", [])
        if graph_results:
            context_parts.append("🔗 Entity Relationships:")
            for result in graph_results[:3]:
                entity = result.get("entity", "Unknown")
                related = result.get("related_entities", [])
                if related:
                    related_names = [r.get("name", "") for r in related[:3]]
                    context_parts.append(f"  • {entity} is related to: {', '.join(related_names)}")
            context_parts.append("")

        if include_markers:
            context_parts.append("📋 Instructions: Use the above retrieved information to provide accurate, contextual responses. Always cite sources when referencing specific information.")

        return "\n".join(context_parts) if context_parts else "Context: Limited information available."

    async def _generate_enhanced_response(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        context: Dict[str, Any],
        query_analysis: Dict[str, Any],
        context_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate response with enhanced RAG awareness
        """
        try:
            if not self.openrouter_client.is_available():
                return {
                    "response": "I'm a NewsNeuron AI assistant. Configure OPENROUTER_API_KEY to enable intelligent responses.",
                    "sources": [],
                    "entities_mentioned": []
                }

            # Build enhanced system prompt
            system_prompt = self._build_enhanced_system_prompt(query_analysis, len(context.get("articles", [])))

            # Build conversation messages
            messages = [{"role": "system", "content": system_prompt}]

            # Add recent conversation history
            recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            for exchange in recent_history[:-1]:
                if exchange["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": exchange["role"],
                        "content": exchange["content"]
                    })

            # Add context and current message
            user_message_with_context = f"{context_prompt}\n\nUser Question: {message}"
            messages.append({"role": "user", "content": user_message_with_context})

            # Generate response
            response = await self.openrouter_client.chat_completion(
                messages=messages,
                model=settings.default_llm_model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )

            ai_response = self.openrouter_client.extract_message_content(response)

            # Extract sources and entities
            sources = self._extract_enhanced_sources(context)
            entities_mentioned = query_analysis.get("entities", [])

            return {
                "response": ai_response,
                "sources": sources,
                "entities_mentioned": entities_mentioned,
                "model_used": settings.default_llm_model
            }

        except Exception as e:
            print(f"Error generating enhanced response: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error while generating a response. Error: {str(e)}",
                "sources": [],
                "entities_mentioned": []
            }

    def _build_enhanced_system_prompt(self, query_analysis: Dict[str, Any], articles_count: int) -> str:
        """Build enhanced system prompt with RAG awareness"""
        
        base_prompt = """You are NewsNeuron, an AI assistant specialized in news analysis and information retrieval. You have access to a knowledge base of articles and entity relationships.

IMPORTANT RAG INSTRUCTIONS:
- You have been provided with retrieved context from the NewsNeuron knowledge base
- ALWAYS prioritize information from the retrieved context over your training data
- When referencing specific information, cite the source articles provided
- If no relevant context is provided, clearly state that you don't have specific information
- Use phrases like "According to the retrieved articles..." or "Based on the sources provided..."

Your capabilities include:
- Analyzing news articles and extracting key insights
- Understanding relationships between entities (people, organizations, locations, events)
- Providing contextual answers based on retrieved information
- Creating timeline visualizations and summaries

Guidelines:
- Be accurate and fact-based, prioritizing retrieved sources
- Be clear about what information comes from retrieved sources vs general knowledge
- Provide source citations when referencing specific information
- If asked about recent events, rely on the retrieved context"""

        intent = query_analysis.get("intent", "general")
        if intent == "timeline":
            base_prompt += "\n\nThe user is asking about timeline or chronological information. Focus on dates, sequence of events, and story evolution from the retrieved sources."
        elif intent == "summary":
            base_prompt += "\n\nThe user wants a summary. Provide concise, structured key points based on the retrieved information."
        
        if articles_count > 0:
            base_prompt += f"\n\nYou have been provided with {articles_count} relevant articles. Use this information to provide accurate, contextual responses."

        return base_prompt

    def _extract_enhanced_sources(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract enhanced source information"""
        sources = []
        articles = context.get("articles", [])

        for article in articles[:5]:
            source = {
                "title": article.get("title", "Unknown"),
                "url": article.get("url"),
                "source": article.get("source"),
                "published_date": article.get("published_date"),
                "id": article.get("id"),
                "similarity_score": article.get("similarity_score"),
                "snippet": article.get("content", "")[:200] + "..." if article.get("content") else None
            }
            sources.append(source)

        return sources

    # Include other methods from original agent
    async def _analyze_query(self, message: str) -> Dict[str, Any]:
        """Analyze user query to determine intent and entities"""
        try:
            entities = self.retriever.extract_entities(message)
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
        """Classify user intent based on message content"""
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

    async def _gather_context(self, message: str, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gather context using hybrid retrieval"""
        try:
            context = {"articles": [], "entities": [], "graph_results": []}

            if not query_analysis.get("requires_search"):
                return context

            intent = query_analysis.get("intent", "general")

            if intent == "timeline" and query_analysis.get("entities"):
                search_results = await self.retriever.hybrid_search(
                    query=message,
                    search_type="graph",
                    limit=10,
                    include_entities=True
                )
            elif intent in ["search", "explanation"]:
                search_results = await self.retriever.hybrid_search(
                    query=message,
                    search_type="hybrid",
                    limit=8,
                    include_entities=True
                )
            else:
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
            return {"articles": [], "entities": [], "graph_results": []}
