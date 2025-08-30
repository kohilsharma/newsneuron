"""
Flashcard Generator for NewsNeuron
Creates AI-summarized flashcards from news content
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.config import settings
from app.services.hybrid_retriever import HybridRetriever
from app.services.openrouter_client import get_openrouter_client
from app.schemas import Flashcard


class FlashcardGenerator:
    """
    Generates AI-powered news flashcards with key insights and summaries
    """

    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever
        # Use our custom OpenRouter client (no OpenAI dependency)
        self.openrouter_client = get_openrouter_client()

    async def generate_flashcards(
        self,
        topics: Optional[List[str]] = None,
        date_range: Optional[Dict[str, str]] = None,
        limit: int = 10,
    ) -> List[Flashcard]:
        """
        Generate flashcards from recent news
        
        Args:
            topics: Optional list of topics to focus on
            date_range: Optional date range for articles
            limit: Maximum number of flashcards to generate
        
        Returns:
            List of generated flashcards
        """
        try:
            # Gather source articles
            articles = await self._gather_source_articles(topics, date_range, limit * 2)

            if not articles:
                return self._create_sample_flashcards(limit)

            # Group articles by topic/theme
            article_groups = self._group_articles_by_theme(articles)

            # Generate flashcards from groups
            flashcards = []
            for theme, theme_articles in article_groups.items():
                if len(flashcards) >= limit:
                    break

                flashcard = await self._create_flashcard_from_articles(
                    theme=theme,
                    articles=theme_articles
                )

                if flashcard:
                    flashcards.append(flashcard)

            # Fill remaining slots with individual article flashcards if needed
            if len(flashcards) < limit:
                remaining_articles = [
                    article for article in articles
                    if not any(article in group for group in article_groups.values())
                ]

                for article in remaining_articles[:limit - len(flashcards)]:
                    flashcard = await self._create_flashcard_from_article(article)
                    if flashcard:
                        flashcards.append(flashcard)

            return flashcards[:limit]

        except Exception as e:
            print(f"Error generating flashcards: {str(e)}")
            return self._create_sample_flashcards(limit)

    async def _gather_source_articles(
        self,
        topics: Optional[List[str]],
        date_range: Optional[Dict[str, str]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Gather source articles for flashcard generation
        """
        try:
            articles = []

            if topics:
                # Search for articles on specific topics
                for topic in topics:
                    search_results = await self.retriever.hybrid_search(
                        query=topic,
                        search_type="vector",
                        limit=limit // len(topics) + 1,
                        include_entities=True
                    )
                    articles.extend(search_results.get("articles", []))
            else:
                # Get recent trending articles
                # For now, use a general search for recent news
                search_results = await self.retriever.hybrid_search(
                    query="latest news trends technology politics climate",
                    search_type="vector",
                    limit=limit,
                    include_entities=True
                )
                articles = search_results.get("articles", [])

            # Filter by date range if specified
            if date_range:
                articles = self._filter_articles_by_date(articles, date_range)

            return articles[:limit]

        except Exception as e:
            print(f"Error gathering source articles: {str(e)}")
            return []

    def _filter_articles_by_date(
        self,
        articles: List[Dict[str, Any]],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Filter articles by date range"""
        try:
            start_date = datetime.fromisoformat(date_range.get("start_date", ""))
            end_date = datetime.fromisoformat(date_range.get("end_date", ""))

            filtered_articles = []
            for article in articles:
                pub_date_str = article.get("published_date")
                if pub_date_str:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    if start_date <= pub_date <= end_date:
                        filtered_articles.append(article)

            return filtered_articles

        except Exception as e:
            print(f"Error filtering articles by date: {str(e)}")
            return articles

    def _group_articles_by_theme(
        self,
        articles: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group articles by common themes/topics
        TODO: Implement proper topic clustering
        """
        # Simple keyword-based grouping for now
        themes = {
            "Technology & AI": [],
            "Politics & Government": [],
            "Climate & Environment": [],
            "Economy & Business": [],
            "Health & Science": [],
            "General News": []
        }

        tech_keywords = ["technology", "ai", "artificial intelligence", "tech", "software", "digital"]
        politics_keywords = ["politics", "government", "election", "policy", "congress", "senate"]
        climate_keywords = ["climate", "environment", "green", "sustainability", "carbon"]
        economy_keywords = ["economy", "business", "market", "trade", "financial", "economic"]
        health_keywords = ["health", "medical", "medicine", "research", "study", "science"]

        for article in articles:
            title = article.get("title", "").lower()
            content = article.get("content", "").lower()
            text = f"{title} {content}"

            categorized = False

            if any(keyword in text for keyword in tech_keywords):
                themes["Technology & AI"].append(article)
                categorized = True
            elif any(keyword in text for keyword in politics_keywords):
                themes["Politics & Government"].append(article)
                categorized = True
            elif any(keyword in text for keyword in climate_keywords):
                themes["Climate & Environment"].append(article)
                categorized = True
            elif any(keyword in text for keyword in economy_keywords):
                themes["Economy & Business"].append(article)
                categorized = True
            elif any(keyword in text for keyword in health_keywords):
                themes["Health & Science"].append(article)
                categorized = True

            if not categorized:
                themes["General News"].append(article)

        # Remove empty themes and limit articles per theme
        filtered_themes = {
            theme: articles[:3] for theme, articles in themes.items() 
            if articles
        }

        return filtered_themes

    async def _create_flashcard_from_articles(
        self,
        theme: str,
        articles: List[Dict[str, Any]]
    ) -> Optional[Flashcard]:
        """
        Create a flashcard from multiple related articles
        """
        try:
            if not self.openrouter_client.is_available():
                return self._create_sample_flashcard(theme, articles)

            # Combine article content
            combined_content = ""
            source_articles = []

            for article in articles[:3]:  # Limit to 3 articles
                title = article.get("title", "")
                content = article.get("content", "")[:500]  # Truncate content
                combined_content += f"Title: {title}\nContent: {content}\n\n"

                source_articles.append({
                    "id": article.get("id"),
                    "title": title,
                    "url": article.get("url"),
                    "source": article.get("source")
                })

            # Generate flashcard using OpenRouter
            prompt = f"""Create a news flashcard for the theme "{theme}" based on the following articles:

{combined_content}

Generate a flashcard with:
1. A compelling title (max 60 characters)
2. A brief summary (2-3 sentences)
3. 3-5 key points (bullet points)
4. Extract mentioned entities (people, organizations, locations)

Format as JSON:
{{
    "title": "...",
    "summary": "...",
    "key_points": ["...", "...", "..."],
    "entities": [{{"name": "...", "type": "..."}}, ...]
}}"""

            response = await self.openrouter_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a news analyst creating concise, informative flashcards."},
                    {"role": "user", "content": prompt}
                ],
                model=settings.default_llm_model,
                max_tokens=800,
                temperature=0.7
            )

            # Parse response
            response_content = self.openrouter_client.extract_message_content(response)
            try:
                flashcard_data = eval(response_content)  # Use json.loads in production
            except:
                # Fallback to manual creation
                return self._create_sample_flashcard(theme, articles)

            # Create flashcard object
            flashcard = Flashcard(
                id=str(uuid.uuid4()),
                title=flashcard_data.get("title", theme),
                summary=flashcard_data.get("summary", "Summary not available"),
                key_points=flashcard_data.get("key_points", []),
                entities=flashcard_data.get("entities", []),
                source_articles=source_articles,
                created_at=datetime.now(),
                category=theme
            )

            return flashcard

        except Exception as e:
            print(f"Error creating flashcard from articles: {str(e)}")
            return self._create_sample_flashcard(theme, articles)

    async def _create_flashcard_from_article(
        self,
        article: Dict[str, Any]
    ) -> Optional[Flashcard]:
        """
        Create a flashcard from a single article
        """
        try:
            title = article.get("title", "News Update")
            content = article.get("content", "")

            # Create simple flashcard
            flashcard = Flashcard(
                id=str(uuid.uuid4()),
                title=title[:60] + "..." if len(title) > 60 else title,
                summary=content[:200] + "..." if len(content) > 200 else content,
                key_points=[
                    "Key information from article",
                    "Additional details available",
                    "Related topics to explore"
                ],
                entities=[],
                source_articles=[{
                    "id": article.get("id"),
                    "title": title,
                    "url": article.get("url"),
                    "source": article.get("source")
                }],
                created_at=datetime.now(),
                category="General"
            )

            return flashcard

        except Exception as e:
            print(f"Error creating flashcard from article: {str(e)}")
            return None

    def _create_sample_flashcard(
        self,
        theme: str,
        articles: List[Dict[str, Any]]
    ) -> Flashcard:
        """Create a sample flashcard when AI generation fails"""
        return Flashcard(
            id=str(uuid.uuid4()),
            title=f"{theme} Update",
            summary=f"Recent developments in {theme.lower()} with key insights and analysis.",
            key_points=[
                f"Latest trends in {theme.lower()}",
                "Key stakeholders and their positions",
                "Potential impact and implications",
                "Areas to watch for future developments"
            ],
            entities=[
                {"name": "Sample Entity", "type": "ORGANIZATION"}
            ],
            source_articles=[
                {
                    "id": article.get("id", 1),
                    "title": article.get("title", "Sample Article"),
                    "url": article.get("url"),
                    "source": article.get("source", "NewsNeuron")
                } for article in articles[:2]
            ],
            created_at=datetime.now(),
            category=theme
        )

    def _create_sample_flashcards(self, limit: int) -> List[Flashcard]:
        """Create sample flashcards for development/fallback"""
        themes = [
            "Technology & AI",
            "Climate Change",
            "Global Politics",
            "Economic Trends",
            "Health & Science"
        ]

        flashcards = []
        for i in range(min(limit, len(themes))):
            theme = themes[i]
            flashcard = self._create_sample_flashcard(theme, [])
            flashcards.append(flashcard)

        return flashcards
