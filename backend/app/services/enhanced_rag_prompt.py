"""
Enhanced RAG Prompt Generator for NewsNeuron
Implements strict source grounding and citation requirements
"""
import json
from typing import Dict, Any, List
from datetime import datetime


def get_enhanced_rag_prompt(context: str, question: str, user_intent: str = "general") -> str:
    """
    Generates an exhaustive RAG prompt for the NewsNeuron agent with strict citation requirements.
    
    Args:
        context: A string containing the retrieved document chunks and their metadata.
        question: The user's original question.
        user_intent: The classified intent (timeline, summary, search, etc.)
        
    Returns:
        A formatted string ready to be sent to the LLM.
    """
    
    # Add intent-specific instructions
    intent_instructions = ""
    if user_intent == "timeline":
        intent_instructions = """
**TIMELINE FOCUS**: The user is asking for chronological information. Focus on dates, sequence of events, and story evolution. Present information in temporal order when possible."""
    
    elif user_intent == "summary":
        intent_instructions = """
**SUMMARY FOCUS**: The user wants a concise overview. Provide structured key points while maintaining citation requirements. Use bullet points or numbered lists for clarity."""
    
    elif user_intent == "relationship":
        intent_instructions = """
**RELATIONSHIP FOCUS**: The user is interested in connections between entities, events, or topics. Highlight relationships and connections found in the sources."""

    prompt = f"""# NewsNeuron RAG System Prompt

## 1. Identity and Role
You are **NewsNeuron**, an expert AI news analyst specializing in factual, source-grounded journalism. You operate like a senior researcher at a prestigious news organization (Reuters, AP, BBC), providing objective analysis based exclusively on verified sources.

## 2. Core Mission
Analyze the provided news articles to answer the user's question with complete accuracy and full source attribution. Every claim must be traceable to specific sources.

## 3. MANDATORY Citation Rules
**CRITICAL**: You MUST cite every single fact, claim, or piece of information using this exact format:
- **Format**: `[Source: {{source_name}}]` at the end of each sentence containing sourced information
- **Multiple Sources**: If synthesizing from multiple sources: `[Sources: {{source1}}, {{source2}}]`
- **Example**: "The policy was announced Tuesday [Source: Reuters Report] and affects 50,000 workers [Source: Bloomberg Analysis]."

## 4. Absolute Requirements

### 4.1 Source Grounding (CRITICAL)
- **100% Grounding**: Your response MUST be entirely based on the provided context
- **No External Knowledge**: Do NOT add information from your training data, even if factually correct
- **Attribution Required**: Every factual statement requires a source citation

### 4.2 Handling Insufficient Information
If the provided articles don't contain enough information to answer the question:
- State clearly: "Based on the provided articles, there is insufficient information to answer this question."
- Do NOT apologize or add explanatory text
- Do NOT attempt to answer with partial information

### 4.3 Conflicting Information
When sources disagree:
- Present both viewpoints with proper citations
- Example: "Company A reports revenue of $5M [Source: TechNews], while Company B claims $7M [Source: BusinessDaily]."
- Do NOT choose sides or make judgments about which source is correct

### 4.4 Synthesis Over Summary
- Create a coherent narrative that directly answers the question
- Do NOT simply list what each source says
- Weave information together logically while maintaining citations

{intent_instructions}

## 5. Response Structure
1. **Direct Answer**: Start with a clear, direct response to the question
2. **Supporting Details**: Provide comprehensive details with citations
3. **Context**: Include relevant background information when available
4. **Source List**: End with a brief list of sources used (optional)

## 6. Quality Standards
- **Accuracy**: Only include information explicitly stated in sources
- **Completeness**: Address all aspects of the question that sources cover
- **Clarity**: Use clear, professional journalism language
- **Balance**: Present multiple perspectives when they exist

---

**RETRIEVED CONTEXT:**
{context}

---

**USER QUESTION:**
{question}

---

**ANALYSIS INSTRUCTIONS:**
1. Carefully read all provided sources
2. Identify information directly relevant to the user's question
3. Synthesize a comprehensive answer using ONLY the provided information
4. Ensure every factual claim includes proper source citation
5. If information is insufficient, state this clearly

**YOUR RESPONSE:**"""

    return prompt


def format_context_for_enhanced_rag(articles: List[Dict[str, Any]]) -> str:
    """
    Format retrieved articles into the context string expected by the enhanced RAG prompt.
    
    Args:
        articles: List of article dictionaries from retrieval
        
    Returns:
        Formatted context string with proper metadata
    """
    if not articles:
        return "No relevant articles found in the knowledge base."
    
    formatted_context = ""
    
    for i, article in enumerate(articles, 1):
        # Extract article information
        title = article.get("title", f"Article {i}")
        content = article.get("content", "")
        source = article.get("source", "Unknown Source")
        published_date = article.get("published_date", "")
        similarity_score = article.get("similarity_score")
        
        # Create source name for citation
        source_name = f"{title}" if title != f"Article {i}" else f"{source} Article {i}"
        
        # Format the context entry
        formatted_context += f"**Article {i}:**\n"
        formatted_context += f"Content: {content}\n"
        formatted_context += f"Metadata: {{\n"
        formatted_context += f"  'source_name': '{source_name}',\n"
        formatted_context += f"  'publication_source': '{source}',\n"
        if published_date:
            formatted_context += f"  'published_date': '{published_date}',\n"
        if similarity_score:
            formatted_context += f"  'relevance_score': {similarity_score:.3f}\n"
        formatted_context += f"}}\n\n"
    
    return formatted_context


def extract_citations_from_response(response: str) -> List[str]:
    """
    Extract all citations from a response to verify source attribution.
    
    Args:
        response: The AI response text
        
    Returns:
        List of cited sources
    """
    import re
    
    # Pattern to match [Source: source_name] or [Sources: source1, source2]
    citation_pattern = r'\[Sources?:\s*([^\]]+)\]'
    matches = re.findall(citation_pattern, response)
    
    citations = []
    for match in matches:
        # Handle multiple sources separated by commas
        sources = [source.strip() for source in match.split(',')]
        citations.extend(sources)
    
    return citations


def validate_rag_response(response: str, provided_sources: List[str]) -> Dict[str, Any]:
    """
    Validate that a RAG response properly cites sources and follows guidelines.
    
    Args:
        response: The AI response text
        provided_sources: List of source names that were provided in context
        
    Returns:
        Validation results dictionary
    """
    citations = extract_citations_from_response(response)
    
    # Check for citation coverage
    has_citations = len(citations) > 0
    citation_coverage = len(citations) / max(len(response.split('.')), 1)  # Citations per sentence
    
    # Check for proper source usage
    valid_citations = [cite for cite in citations if any(source in cite for source in provided_sources)]
    invalid_citations = [cite for cite in citations if cite not in valid_citations]
    
    # Check for insufficient information handling
    insufficient_info_handled = "insufficient information" in response.lower() and len(response) < 200
    
    return {
        "has_citations": has_citations,
        "citation_count": len(citations),
        "citation_coverage": citation_coverage,
        "valid_citations": len(valid_citations),
        "invalid_citations": len(invalid_citations),
        "insufficient_info_handled": insufficient_info_handled,
        "follows_format": has_citations and len(invalid_citations) == 0,
        "quality_score": min(1.0, (len(valid_citations) / max(len(citations), 1)) * citation_coverage)
    }


class EnhancedRAGFormatter:
    """
    Helper class to format and validate enhanced RAG interactions
    """
    
    @staticmethod
    def format_articles_for_prompt(articles: List[Dict[str, Any]], max_articles: int = 5) -> str:
        """Format articles for the enhanced RAG prompt"""
        return format_context_for_enhanced_rag(articles[:max_articles])
    
    @staticmethod
    def generate_prompt(articles: List[Dict[str, Any]], question: str, intent: str = "general") -> str:
        """Generate the complete enhanced RAG prompt"""
        context = EnhancedRAGFormatter.format_articles_for_prompt(articles)
        return get_enhanced_rag_prompt(context, question, intent)
    
    @staticmethod
    def validate_response(response: str, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the response against provided sources"""
        source_names = [
            article.get("title", f"{article.get('source', 'Unknown')} Article")
            for article in articles
        ]
        return validate_rag_response(response, source_names)
    
    @staticmethod
    def create_source_summary(articles: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Create a summary of sources for transparency"""
        return [
            {
                "source_name": article.get("title", "Unknown Title"),
                "publication": article.get("source", "Unknown Source"),
                "published_date": article.get("published_date", "Unknown Date"),
                "relevance_score": f"{article.get('similarity_score', 0):.3f}" if article.get('similarity_score') else "N/A"
            }
            for article in articles
        ]
