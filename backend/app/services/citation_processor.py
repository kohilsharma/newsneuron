"""
Citation Processor for NewsNeuron
Handles citation extraction, linking, and verification for interactive chat
"""
import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from app.schemas import CitationInfo
from app.services.enhanced_rag_prompt import extract_citations_from_response


class CitationProcessor:
    """
    Advanced citation processor for interactive chat with linking capabilities
    """
    
    def __init__(self):
        self.citation_pattern = r'\[Sources?:\s*([^\]]+)\]'
        self.inline_citation_pattern = r'\[Source:\s*([^\]]+)\]'
    
    def process_response_citations(
        self, 
        response_text: str, 
        source_articles: List[Dict[str, Any]]
    ) -> Tuple[str, List[CitationInfo]]:
        """
        Process citations in response text and create interactive citation objects
        
        Args:
            response_text: The AI response with citations
            source_articles: List of source articles used
            
        Returns:
            Tuple of (processed_text, citation_info_list)
        """
        citations = []
        processed_text = response_text
        article_map = self._create_article_map(source_articles)
        
        # Find all citation matches with positions
        citation_matches = list(re.finditer(self.citation_pattern, response_text))
        
        # Process citations from end to start to preserve positions
        for match in reversed(citation_matches):
            citation_text = match.group(1)
            start_pos = match.start()
            end_pos = match.end()
            
            # Extract individual sources from citation
            source_names = [name.strip() for name in citation_text.split(',')]
            
            for source_name in source_names:
                # Find matching article
                article_info = self._find_matching_article(source_name, article_map)
                
                if article_info:
                    citation_id = f"cite_{uuid.uuid4().hex[:8]}"
                    
                    # Create citation info
                    citation_info = CitationInfo(
                        id=citation_id,
                        source_name=source_name,
                        title=article_info.get("title", source_name),
                        url=article_info.get("url"),
                        publication=article_info.get("source", "Unknown"),
                        published_date=article_info.get("published_date"),
                        snippet=article_info.get("content", "")[:200] + "..." if article_info.get("content") else None,
                        similarity_score=article_info.get("similarity_score"),
                        position_in_text={"start": start_pos, "end": end_pos},
                        verification_url=self._generate_verification_url(article_info)
                    )
                    
                    citations.append(citation_info)
            
            # Replace citation with interactive link
            interactive_citation = self._create_interactive_citation_html(
                citation_text, [c for c in citations if c.position_in_text["start"] == start_pos]
            )
            
            processed_text = (
                processed_text[:start_pos] + 
                interactive_citation + 
                processed_text[end_pos:]
            )
        
        return processed_text, citations
    
    def _create_article_map(self, articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Create a mapping of article titles to article data"""
        article_map = {}
        
        for article in articles:
            title = article.get("title", "")
            # Add variations for matching
            article_map[title] = article
            article_map[title.lower()] = article
            
            # Add short versions
            if len(title) > 30:
                short_title = title[:30] + "..."
                article_map[short_title] = article
        
        return article_map
    
    def _find_matching_article(self, source_name: str, article_map: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the best matching article for a source name"""
        # Direct match
        if source_name in article_map:
            return article_map[source_name]
        
        # Case insensitive match
        if source_name.lower() in article_map:
            return article_map[source_name.lower()]
        
        # Partial match
        for title, article in article_map.items():
            if source_name.lower() in title.lower() or title.lower() in source_name.lower():
                return article
        
        return None
    
    def _generate_verification_url(self, article_info: Dict[str, Any]) -> str:
        """Generate a verification URL for the article"""
        article_id = article_info.get("id")
        if article_id:
            return f"/api/v1/articles/{article_id}/verify"
        return None
    
    def _create_interactive_citation_html(
        self, 
        citation_text: str, 
        citation_infos: List[CitationInfo]
    ) -> str:
        """Create interactive HTML for citations"""
        citation_ids = [c.id for c in citation_infos]
        
        # Create a clickable citation with data attributes
        return f'<span class="citation-link" data-citation-ids="{",".join(citation_ids)}" data-original="{citation_text}">[Sources: {citation_text}]</span>'
    
    def generate_suggested_questions(
        self, 
        response_text: str, 
        entities: List[str], 
        source_articles: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate suggested follow-up questions based on response"""
        suggestions = []
        
        # Entity-based suggestions
        for entity in entities[:3]:
            suggestions.append(f"Tell me more about {entity}")
            suggestions.append(f"What's the latest news on {entity}?")
        
        # Source-based suggestions
        if source_articles:
            suggestions.append("Can you elaborate on these sources?")
            suggestions.append("What other related articles are available?")
        
        # Content-based suggestions
        if "announced" in response_text.lower():
            suggestions.append("What are the implications of this announcement?")
        
        if "study" in response_text.lower() or "research" in response_text.lower():
            suggestions.append("What were the key findings?")
        
        if any(word in response_text.lower() for word in ["increase", "decrease", "change"]):
            suggestions.append("What caused this change?")
        
        # Add some randomized suggestions to avoid AI-generated feel
        random_suggestions = [
            "How does this compare to previous years?",
            "What are the potential future developments?",
            "Who are the key players involved?",
            "What's the broader context here?",
            "Are there any opposing viewpoints?",
            "What questions should I be asking about this?"
        ]
        
        # Add 2-3 random suggestions
        import random
        suggestions.extend(random.sample(random_suggestions, min(3, len(random_suggestions))))
        
        return suggestions[:6]  # Limit to 6 suggestions
    
    def create_interactive_elements(
        self, 
        response_text: str, 
        entities: List[str], 
        rag_quality: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create interactive UI elements for the response"""
        elements = []
        
        # Quality indicator
        quality_score = rag_quality.get("quality_score", 0)
        if quality_score > 0:
            elements.append({
                "type": "quality_indicator",
                "score": quality_score,
                "label": self._get_quality_label(quality_score),
                "color": self._get_quality_color(quality_score)
            })
        
        # Entity chips
        if entities:
            elements.append({
                "type": "entity_chips",
                "entities": [{"name": entity, "searchable": True} for entity in entities[:5]]
            })
        
        # Citation summary
        citation_count = rag_quality.get("citation_count", 0)
        if citation_count > 0:
            elements.append({
                "type": "citation_summary",
                "count": citation_count,
                "expandable": True
            })
        
        # Reading time estimate
        word_count = len(response_text.split())
        reading_time = max(1, word_count // 200)  # Assuming 200 WPM
        elements.append({
            "type": "reading_time",
            "minutes": reading_time,
            "words": word_count
        })
        
        return elements
    
    def _get_quality_label(self, score: float) -> str:
        """Get quality label based on score"""
        if score >= 0.9:
            return "Excellent Sources"
        elif score >= 0.7:
            return "Good Sources"
        elif score >= 0.5:
            return "Moderate Sources"
        else:
            return "Limited Sources"
    
    def _get_quality_color(self, score: float) -> str:
        """Get quality color based on score"""
        if score >= 0.9:
            return "green"
        elif score >= 0.7:
            return "blue"
        elif score >= 0.5:
            return "yellow"
        else:
            return "orange"
    
    def extract_conversation_insights(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract insights from conversation for summary"""
        topics = set()
        entities = set()
        total_sources = 0
        
        for message in messages:
            if message.get("role") == "assistant":
                # Extract entities
                message_entities = message.get("entities_mentioned", [])
                entities.update(message_entities)
                
                # Count sources
                sources = message.get("sources", [])
                total_sources += len(sources)
                
                # Simple topic extraction (in production, use more sophisticated NLP)
                content = message.get("content", "").lower()
                if "ai" in content or "artificial intelligence" in content:
                    topics.add("Artificial Intelligence")
                if "climate" in content or "environment" in content:
                    topics.add("Climate & Environment")
                if "politics" in content or "government" in content:
                    topics.add("Politics & Government")
                if "technology" in content or "tech" in content:
                    topics.add("Technology")
                if "business" in content or "economy" in content:
                    topics.add("Business & Economy")
        
        return {
            "topics_discussed": list(topics),
            "entities_mentioned": list(entities)[:10],  # Top 10
            "total_sources_used": total_sources,
            "message_count": len([m for m in messages if m.get("role") == "user"])
        }
    
    def generate_conversation_title(self, messages: List[Dict[str, Any]]) -> str:
        """Generate a title for the conversation"""
        if not messages:
            return "New Conversation"
        
        # Get first user message
        first_user_message = None
        for message in messages:
            if message.get("role") == "user":
                first_user_message = message.get("content", "")
                break
        
        if not first_user_message:
            return "New Conversation"
        
        # Simple title generation (in production, use LLM to generate better titles)
        content = first_user_message.lower()
        
        if "ai" in content or "artificial intelligence" in content:
            return "AI Discussion"
        elif "climate" in content or "environment" in content:
            return "Climate & Environment"
        elif "politics" in content or "government" in content:
            return "Political Discussion"
        elif "technology" in content or "tech" in content:
            return "Technology News"
        elif "business" in content or "economy" in content:
            return "Business & Economy"
        else:
            # Use first few words
            words = first_user_message.split()[:4]
            return " ".join(words).title()
    
    def create_citation_verification_data(self, citation: CitationInfo) -> Dict[str, Any]:
        """Create data for citation verification modal"""
        return {
            "citation_id": citation.id,
            "source_details": {
                "title": citation.title,
                "publication": citation.publication,
                "published_date": citation.published_date,
                "url": citation.url,
                "snippet": citation.snippet,
                "similarity_score": citation.similarity_score
            },
            "verification_methods": [
                {
                    "type": "source_check",
                    "label": "View Original Source",
                    "url": citation.url,
                    "available": bool(citation.url)
                },
                {
                    "type": "similarity_check", 
                    "label": "Relevance Score",
                    "score": citation.similarity_score,
                    "available": citation.similarity_score is not None
                },
                {
                    "type": "context_check",
                    "label": "View Context",
                    "snippet": citation.snippet,
                    "available": bool(citation.snippet)
                }
            ],
            "trust_indicators": {
                "has_url": bool(citation.url),
                "has_date": bool(citation.published_date),
                "high_relevance": (citation.similarity_score or 0) > 0.7,
                "known_publication": citation.publication not in ["Unknown", ""]
            }
        }


# Global citation processor instance
_citation_processor = None


def get_citation_processor() -> CitationProcessor:
    """Get singleton citation processor instance"""
    global _citation_processor
    if _citation_processor is None:
        _citation_processor = CitationProcessor()
    return _citation_processor
