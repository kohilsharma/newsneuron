"""
RAG Verification Service for NewsNeuron
Helps verify that the AI agent is actually using retrieved context
"""
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from app.services.hybrid_retriever import HybridRetriever
from app.services.langgraph_agent import LangGraphAgent


class RAGVerifier:
    """
    Service to verify and debug RAG functionality
    """
    
    def __init__(self, agent: LangGraphAgent):
        self.agent = agent
        self.retriever = agent.retriever
    
    async def test_rag_vs_no_rag(self, query: str) -> Dict[str, Any]:
        """
        Compare responses with and without RAG to verify RAG is working
        
        Args:
            query: Test query
        
        Returns:
            Comparison results showing RAG vs no-RAG responses
        """
        print(f"🔍 Testing RAG vs No-RAG for query: '{query}'")
        
        # Test WITH RAG
        print("📚 Testing WITH RAG...")
        start_time = time.time()
        rag_response = await self.agent.process_message(
            message=query,
            conversation_id=f"rag-test-{uuid.uuid4()}",
            use_hybrid_search=True
        )
        rag_time = time.time() - start_time
        
        # Test WITHOUT RAG (just model knowledge)
        print("🧠 Testing WITHOUT RAG...")
        start_time = time.time()
        no_rag_response = await self.agent.process_message(
            message=query,
            conversation_id=f"no-rag-test-{uuid.uuid4()}",
            use_hybrid_search=False
        )
        no_rag_time = time.time() - start_time
        
        return {
            "query": query,
            "with_rag": {
                "response": rag_response["response"],
                "sources_count": len(rag_response.get("sources", [])),
                "sources": rag_response.get("sources", []),
                "entities": rag_response.get("entities_mentioned", []),
                "response_time": rag_time
            },
            "without_rag": {
                "response": no_rag_response["response"],
                "sources_count": len(no_rag_response.get("sources", [])),
                "sources": no_rag_response.get("sources", []),
                "entities": no_rag_response.get("entities_mentioned", []),
                "response_time": no_rag_time
            },
            "differences": {
                "response_length_diff": len(rag_response["response"]) - len(no_rag_response["response"]),
                "has_sources_with_rag": len(rag_response.get("sources", [])) > 0,
                "responses_are_different": rag_response["response"] != no_rag_response["response"]
            }
        }
    
    async def detailed_rag_inspection(self, query: str) -> Dict[str, Any]:
        """
        Detailed inspection of what RAG retrieves and how it's used
        
        Args:
            query: Query to inspect
        
        Returns:
            Detailed breakdown of RAG process
        """
        print(f"🔬 Detailed RAG inspection for: '{query}'")
        
        # Step 1: Analyze the query
        query_analysis = await self.agent._analyze_query(query)
        print(f"  📝 Query analysis: {query_analysis}")
        
        # Step 2: Gather context manually
        context = await self.agent._gather_context(query, query_analysis)
        print(f"  📊 Retrieved {len(context.get('articles', []))} articles")
        print(f"  🔗 Retrieved {len(context.get('graph_results', []))} graph results")
        
        # Step 3: Build context prompt
        context_prompt = self.agent._build_context_prompt(context)
        print(f"  📄 Context prompt length: {len(context_prompt)} characters")
        
        # Step 4: Show what gets sent to the LLM
        system_prompt = self.agent._build_system_prompt(query_analysis)
        
        return {
            "query": query,
            "query_analysis": query_analysis,
            "retrieved_context": {
                "articles_count": len(context.get("articles", [])),
                "articles": [
                    {
                        "title": art.get("title", ""),
                        "source": art.get("source", ""),
                        "similarity_score": art.get("similarity_score"),
                        "snippet": art.get("content", "")[:100] + "..." if art.get("content") else ""
                    }
                    for art in context.get("articles", [])[:3]
                ],
                "entities": context.get("query_entities", []),
                "graph_results_count": len(context.get("graph_results", []))
            },
            "prompts": {
                "system_prompt_length": len(system_prompt),
                "context_prompt_length": len(context_prompt),
                "context_prompt_preview": context_prompt[:300] + "..." if len(context_prompt) > 300 else context_prompt
            }
        }
    
    async def test_specific_knowledge(self, queries: List[str]) -> Dict[str, Any]:
        """
        Test queries that should require RAG (specific/recent info not in model training)
        
        Args:
            queries: List of specific queries to test
        
        Returns:
            Results showing whether RAG provided specific information
        """
        results = {}
        
        for query in queries:
            print(f"🎯 Testing specific knowledge: '{query}'")
            
            # Get detailed inspection
            inspection = await self.detailed_rag_inspection(query)
            
            # Get response
            response = await self.agent.process_message(
                message=query,
                conversation_id=f"specific-test-{uuid.uuid4()}",
                use_hybrid_search=True
            )
            
            # Analyze if response seems to use retrieved info
            has_sources = len(response.get("sources", [])) > 0
            has_specific_entities = len(response.get("entities_mentioned", [])) > 0
            retrieved_articles = inspection["retrieved_context"]["articles_count"] > 0
            
            results[query] = {
                "response": response["response"],
                "sources_provided": has_sources,
                "entities_found": has_specific_entities,
                "articles_retrieved": retrieved_articles,
                "sources": response.get("sources", []),
                "rag_indicators": {
                    "mentions_sources": "according to" in response["response"].lower() or "based on" in response["response"].lower(),
                    "has_specific_details": retrieved_articles and has_sources,
                    "response_length": len(response["response"])
                }
            }
        
        return results
    
    async def inject_test_marker(self, query: str, marker: str = "🔍RAG_TEST_MARKER🔍") -> bool:
        """
        Inject a unique marker in retrieved context to verify it's being used
        
        Args:
            query: Query to test
            marker: Unique marker to inject
        
        Returns:
            True if marker appears in response, False otherwise
        """
        print(f"🏷️  Injecting test marker: {marker}")
        
        # Temporarily modify context building to include marker
        original_build_context = self.agent._build_context_prompt
        
        def modified_build_context(context):
            original_context = original_build_context(context)
            if original_context and "Context:" not in original_context:
                return f"{original_context}\n\n{marker} This information was retrieved from the knowledge base."
            return original_context
        
        # Temporarily replace the method
        self.agent._build_context_prompt = modified_build_context
        
        try:
            response = await self.agent.process_message(
                message=query,
                conversation_id=f"marker-test-{uuid.uuid4()}",
                use_hybrid_search=True
            )
            
            marker_in_response = marker in response["response"]
            print(f"  ✅ Marker found in response: {marker_in_response}")
            
            return marker_in_response
            
        finally:
            # Restore original method
            self.agent._build_context_prompt = original_build_context
    
    def create_rag_verification_report(
        self, 
        rag_vs_no_rag: Dict[str, Any],
        detailed_inspection: Dict[str, Any],
        marker_test: bool
    ) -> str:
        """
        Create a comprehensive RAG verification report
        """
        report = []
        report.append("📊 RAG VERIFICATION REPORT")
        report.append("=" * 50)
        report.append(f"Query: {rag_vs_no_rag['query']}")
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append("")
        
        # RAG vs No-RAG comparison
        report.append("🔍 RAG vs No-RAG Comparison:")
        report.append(f"  • With RAG sources: {rag_vs_no_rag['with_rag']['sources_count']}")
        report.append(f"  • Without RAG sources: {rag_vs_no_rag['without_rag']['sources_count']}")
        report.append(f"  • Responses are different: {rag_vs_no_rag['differences']['responses_are_different']}")
        report.append(f"  • RAG provides sources: {rag_vs_no_rag['differences']['has_sources_with_rag']}")
        report.append("")
        
        # Retrieved context details
        report.append("📚 Retrieved Context:")
        report.append(f"  • Articles retrieved: {detailed_inspection['retrieved_context']['articles_count']}")
        report.append(f"  • Entities identified: {len(detailed_inspection['retrieved_context']['entities'])}")
        report.append(f"  • Context prompt length: {detailed_inspection['prompts']['context_prompt_length']} chars")
        report.append("")
        
        # Sources
        if detailed_inspection['retrieved_context']['articles']:
            report.append("📄 Retrieved Articles:")
            for i, article in enumerate(detailed_inspection['retrieved_context']['articles'], 1):
                report.append(f"  {i}. {article['title']} (Source: {article['source']})")
                if article['similarity_score']:
                    report.append(f"     Similarity: {article['similarity_score']:.3f}")
        report.append("")
        
        # Marker test
        report.append("🏷️  Marker Test:")
        report.append(f"  • Injected marker found in response: {marker_test}")
        report.append(f"  • This proves context is being used: {'✅ YES' if marker_test else '❌ NO'}")
        report.append("")
        
        # Verdict
        report.append("🎯 VERDICT:")
        rag_working = (
            rag_vs_no_rag['differences']['has_sources_with_rag'] and
            rag_vs_no_rag['differences']['responses_are_different'] and
            detailed_inspection['retrieved_context']['articles_count'] > 0 and
            marker_test
        )
        
        if rag_working:
            report.append("  ✅ RAG IS WORKING CORRECTLY")
            report.append("  • Context is being retrieved")
            report.append("  • Context is being used in responses")
            report.append("  • Sources are being provided")
        else:
            report.append("  ❌ RAG MAY NOT BE WORKING PROPERLY")
            report.append("  • Check database connections")
            report.append("  • Verify context building")
            report.append("  • Check prompt construction")
        
        return "\n".join(report)


async def verify_rag_functionality(agent: LangGraphAgent, test_query: str = "What are the latest developments in AI technology?") -> str:
    """
    Convenient function to verify RAG is working
    
    Args:
        agent: LangGraph agent to test
        test_query: Query to use for testing
    
    Returns:
        Verification report as string
    """
    verifier = RAGVerifier(agent)
    
    print("🚀 Starting RAG verification...")
    
    # Run all tests
    rag_comparison = await verifier.test_rag_vs_no_rag(test_query)
    detailed_inspection = await verifier.detailed_rag_inspection(test_query)
    marker_test = await verifier.inject_test_marker(test_query)
    
    # Generate report
    report = verifier.create_rag_verification_report(
        rag_comparison, detailed_inspection, marker_test
    )
    
    return report
