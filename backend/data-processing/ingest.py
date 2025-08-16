"""
NewsNeuron Data Ingestion Pipeline
Processes news articles and populates both Supabase and Neo4j databases
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import spacy
import openai
from neo4j import GraphDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.database.supabase_client import get_supabase_client
from app.database.neo4j_client import get_neo4j_client


class NewsDataProcessor:
    """
    Main data processing class for NewsNeuron
    Handles data ingestion, entity extraction, embedding generation, and database population
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.neo4j = get_neo4j_client()
        self.nlp = None
        self._setup_components()
    
    def _setup_components(self):
        """Initialize NLP and AI components"""
        try:
            # Load spaCy model for NER
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("SpaCy model loaded successfully")
            except OSError:
                logger.warning("SpaCy model not found. Please install: python -m spacy download en_core_web_sm")
                self.nlp = None
            
            # Setup OpenAI
            if settings.openai_api_key:
                openai.api_key = settings.openai_api_key
                logger.info("OpenAI API configured")
            else:
                logger.warning("OpenAI API key not configured - using dummy embeddings")
                
        except Exception as e:
            logger.error(f"Error setting up components: {str(e)}")
    
    async def process_dataset(self, dataset_path: str, limit: Optional[int] = None):
        """
        Process a news dataset and populate databases
        
        Args:
            dataset_path: Path to the dataset file (CSV, JSON, or JSONL)
            limit: Optional limit on number of articles to process
        """
        try:
            logger.info(f"Starting data processing from {dataset_path}")
            
            # Load dataset
            articles = self._load_dataset(dataset_path, limit)
            logger.info(f"Loaded {len(articles)} articles")
            
            if not articles:
                logger.error("No articles found in dataset")
                return
            
            # Process articles in batches
            batch_size = 10
            total_processed = 0
            
            for i in range(0, len(articles), batch_size):
                batch = articles[i:i + batch_size]
                
                try:
                    processed_count = await self._process_batch(batch)
                    total_processed += processed_count
                    
                    logger.info(f"Processed batch {i//batch_size + 1}, "
                              f"Total processed: {total_processed}/{len(articles)}")
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as batch_error:
                    logger.error(f"Error processing batch {i//batch_size + 1}: {str(batch_error)}")
                    continue
            
            logger.info(f"Data processing completed. Total articles processed: {total_processed}")
            
        except Exception as e:
            logger.error(f"Error in dataset processing: {str(e)}")
    
    def _load_dataset(self, dataset_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load dataset from file
        
        Args:
            dataset_path: Path to dataset file
            limit: Optional limit on articles
        
        Returns:
            List of article dictionaries
        """
        try:
            file_path = Path(dataset_path)
            
            if not file_path.exists():
                # Create sample dataset if file doesn't exist
                logger.warning(f"Dataset file {dataset_path} not found. Creating sample data.")
                return self._create_sample_dataset(limit or 20)
            
            articles = []
            
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
                articles = df.to_dict('records')
                
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        articles = data
                    else:
                        articles = [data]
                        
            elif file_path.suffix.lower() == '.jsonl':
                with open(file_path, 'r', encoding='utf-8') as f:
                    articles = [json.loads(line) for line in f if line.strip()]
            
            # Apply limit if specified
            if limit:
                articles = articles[:limit]
            
            # Standardize article format
            standardized_articles = []
            for article in articles:
                standardized = self._standardize_article_format(article)
                if standardized:
                    standardized_articles.append(standardized)
            
            return standardized_articles
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            return self._create_sample_dataset(limit or 10)
    
    def _standardize_article_format(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Standardize article format across different datasets
        
        Args:
            article: Raw article dictionary
        
        Returns:
            Standardized article dictionary or None if invalid
        """
        try:
            # Map common field names
            title_fields = ['title', 'headline', 'Title', 'Headline']
            content_fields = ['content', 'text', 'body', 'article', 'Content', 'Text']
            url_fields = ['url', 'link', 'URL', 'Link']
            date_fields = ['published_date', 'date', 'published', 'publication_date', 'Date']
            source_fields = ['source', 'publication', 'publisher', 'Source', 'Publication']
            
            # Extract fields
            title = None
            for field in title_fields:
                if field in article and article[field]:
                    title = str(article[field]).strip()
                    break
            
            content = None
            for field in content_fields:
                if field in article and article[field]:
                    content = str(article[field]).strip()
                    break
            
            # Skip if missing essential fields
            if not title or not content:
                return None
            
            # Extract optional fields
            url = None
            for field in url_fields:
                if field in article and article[field]:
                    url = str(article[field]).strip()
                    break
            
            published_date = None
            for field in date_fields:
                if field in article and article[field]:
                    try:
                        if isinstance(article[field], str):
                            published_date = datetime.fromisoformat(article[field].replace('Z', '+00:00'))
                        elif hasattr(article[field], 'isoformat'):
                            published_date = article[field]
                    except:
                        continue
                    break
            
            source = None
            for field in source_fields:
                if field in article and article[field]:
                    source = str(article[field]).strip()
                    break
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'published_date': published_date,
                'source': source or 'Unknown'
            }
            
        except Exception as e:
            logger.error(f"Error standardizing article format: {str(e)}")
            return None
    
    def _create_sample_dataset(self, count: int) -> List[Dict[str, Any]]:
        """Create sample dataset for development"""
        sample_articles = [
            {
                'title': 'AI Breakthrough in Language Understanding',
                'content': 'Researchers at leading AI companies have announced significant breakthroughs in natural language understanding. The new models demonstrate improved comprehension and generation capabilities across multiple languages and domains.',
                'url': 'https://example.com/ai-breakthrough',
                'published_date': datetime.now(),
                'source': 'TechNews'
            },
            {
                'title': 'Climate Summit Reaches Historic Agreement',
                'content': 'World leaders at the international climate summit have reached a historic agreement on carbon reduction targets. The agreement includes commitments from major economies to achieve net-zero emissions by 2050.',
                'url': 'https://example.com/climate-agreement',
                'published_date': datetime.now(),
                'source': 'GlobalNews'
            },
            {
                'title': 'Tesla Unveils New Electric Vehicle Technology',
                'content': 'Tesla has announced revolutionary battery technology that could extend electric vehicle range to over 500 miles. CEO Elon Musk demonstrated the new technology at the company\'s annual innovation day.',
                'url': 'https://example.com/tesla-battery',
                'published_date': datetime.now(),
                'source': 'AutoNews'
            },
            {
                'title': 'OpenAI Releases Advanced AI Assistant',
                'content': 'OpenAI has released a new version of its AI assistant with enhanced reasoning capabilities. The update includes improved performance in coding, mathematics, and complex problem-solving tasks.',
                'url': 'https://example.com/openai-release',
                'published_date': datetime.now(),
                'source': 'AIDaily'
            },
            {
                'title': 'Space Mission Discovers New Exoplanets',
                'content': 'NASA\'s latest space mission has discovered multiple exoplanets in the habitable zone of nearby star systems. Scientists believe these planets could potentially support liquid water and life.',
                'url': 'https://example.com/exoplanets',
                'published_date': datetime.now(),
                'source': 'ScienceNews'
            }
        ]
        
        # Repeat and modify to reach desired count
        articles = []
        for i in range(count):
            base_article = sample_articles[i % len(sample_articles)].copy()
            if i >= len(sample_articles):
                base_article['title'] = f"{base_article['title']} - Update {i // len(sample_articles) + 1}"
            articles.append(base_article)
        
        logger.info(f"Created {len(articles)} sample articles")
        return articles
    
    async def _process_batch(self, batch: List[Dict[str, Any]]) -> int:
        """
        Process a batch of articles
        
        Args:
            batch: List of article dictionaries
        
        Returns:
            Number of successfully processed articles
        """
        processed_count = 0
        
        for article in batch:
            try:
                success = await self._process_single_article(article)
                if success:
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing article '{article.get('title', 'Unknown')}': {str(e)}")
                continue
        
        return processed_count
    
    async def _process_single_article(self, article: Dict[str, Any]) -> bool:
        """
        Process a single article through the complete pipeline
        
        Args:
            article: Article dictionary
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # 1. Generate embedding
            embedding = await self._generate_embedding(article)
            
            # 2. Extract entities
            entities = self._extract_entities(article)
            
            # 3. Insert article into Supabase
            article_data = {
                'title': article['title'],
                'content': article['content'],
                'url': article.get('url'),
                'published_date': article.get('published_date'),
                'source': article.get('source'),
                'embedding': embedding
            }
            
            supabase_article = await self.supabase.insert_article(article_data)
            article_id = supabase_article['id']
            
            # 4. Process entities in Supabase
            entity_ids = await self._process_entities_supabase(entities, article_id)
            
            # 5. Create nodes and relationships in Neo4j
            await self._process_neo4j_data(article, entities, article_id)
            
            logger.debug(f"Successfully processed article: {article['title'][:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error in single article processing: {str(e)}")
            return False
    
    async def _generate_embedding(self, article: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for article content
        
        Args:
            article: Article dictionary
        
        Returns:
            List of embedding values
        """
        try:
            if not settings.openai_api_key:
                # Return dummy embedding for development
                return [0.1] * settings.embedding_dimension
            
            # Combine title and content for embedding
            text = f"{article['title']} {article['content']}"
            
            # Truncate text if too long (OpenAI has token limits)
            max_chars = 8000  # Roughly equivalent to token limit
            if len(text) > max_chars:
                text = text[:max_chars]
            
            response = await openai.Embedding.acreate(
                model=settings.embedding_model,
                input=text
            )
            
            return response['data'][0]['embedding']
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return dummy embedding on error
            return [0.1] * settings.embedding_dimension
    
    def _extract_entities(self, article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract named entities from article content
        
        Args:
            article: Article dictionary
        
        Returns:
            List of entity dictionaries
        """
        try:
            if not self.nlp:
                # Return sample entities if spaCy not available
                return self._extract_sample_entities(article)
            
            # Combine title and content
            text = f"{article['title']} {article['content']}"
            
            # Process with spaCy
            doc = self.nlp(text)
            
            entities = []
            seen_entities = set()
            
            for ent in doc.ents:
                # Map spaCy labels to our entity types
                entity_type = self._map_spacy_label(ent.label_)
                
                if entity_type and ent.text.strip():
                    entity_name = ent.text.strip()
                    
                    # Avoid duplicates
                    entity_key = (entity_name.lower(), entity_type)
                    if entity_key not in seen_entities:
                        seen_entities.add(entity_key)
                        
                        entities.append({
                            'name': entity_name,
                            'type': entity_type,
                            'context': self._extract_context(text, ent.start_char, ent.end_char),
                            'confidence': 0.9  # spaCy doesn't provide confidence scores directly
                        })
            
            return entities[:20]  # Limit to 20 entities per article
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return self._extract_sample_entities(article)
    
    def _map_spacy_label(self, label: str) -> Optional[str]:
        """Map spaCy entity labels to our entity types"""
        mapping = {
            'PERSON': 'PERSON',
            'ORG': 'ORGANIZATION',
            'GPE': 'LOCATION',  # Geopolitical entity
            'LOC': 'LOCATION',
            'EVENT': 'EVENT',
            'FAC': 'LOCATION',  # Facility
            'NORP': 'ORGANIZATION',  # Nationalities, religious/political groups
        }
        return mapping.get(label)
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extract context around an entity mention"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _extract_sample_entities(self, article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sample entities when spaCy is not available"""
        # Simple keyword-based entity extraction for development
        text = f"{article['title']} {article['content']}".lower()
        
        sample_entities = []
        
        # Define some sample entities to look for
        known_entities = {
            'openai': 'ORGANIZATION',
            'tesla': 'ORGANIZATION',
            'nasa': 'ORGANIZATION',
            'google': 'ORGANIZATION',
            'microsoft': 'ORGANIZATION',
            'elon musk': 'PERSON',
            'san francisco': 'LOCATION',
            'california': 'LOCATION',
            'new york': 'LOCATION',
            'united states': 'LOCATION',
            'climate summit': 'EVENT',
            'ai conference': 'EVENT'
        }
        
        for entity_name, entity_type in known_entities.items():
            if entity_name in text:
                sample_entities.append({
                    'name': entity_name.title(),
                    'type': entity_type,
                    'context': f"Mentioned in context of {article['title']}",
                    'confidence': 0.8
                })
        
        return sample_entities[:10]
    
    async def _process_entities_supabase(
        self,
        entities: List[Dict[str, Any]],
        article_id: int
    ) -> List[int]:
        """
        Process entities in Supabase and create article-entity links
        
        Args:
            entities: List of entity dictionaries
            article_id: Supabase article ID
        
        Returns:
            List of entity IDs
        """
        entity_ids = []
        
        for entity in entities:
            try:
                # Check if entity already exists
                existing_entities = await self.supabase.search_entities(
                    query=entity['name'],
                    entity_type=entity['type'],
                    limit=1
                )
                
                if existing_entities:
                    entity_id = existing_entities[0]['id']
                else:
                    # Create new entity
                    entity_data = {
                        'name': entity['name'],
                        'type': entity['type']
                    }
                    new_entity = await self.supabase.insert_entity(entity_data)
                    entity_id = new_entity['id']
                
                # Link article to entity
                await self.supabase.link_article_entity(article_id, entity_id)
                entity_ids.append(entity_id)
                
            except Exception as e:
                logger.error(f"Error processing entity {entity['name']}: {str(e)}")
                continue
        
        return entity_ids
    
    async def _process_neo4j_data(
        self,
        article: Dict[str, Any],
        entities: List[Dict[str, Any]],
        supabase_article_id: int
    ):
        """
        Create nodes and relationships in Neo4j
        
        Args:
            article: Article dictionary
            entities: List of entities
            supabase_article_id: Article ID from Supabase
        """
        try:
            # Create article node
            await self.neo4j.create_article_node(
                supabase_id=supabase_article_id,
                title=article['title'],
                published_date=article.get('published_date').isoformat() if article.get('published_date') else None,
                source=article.get('source')
            )
            
            # Create entity nodes and relationships
            for entity in entities:
                try:
                    # Create entity node
                    await self.neo4j.create_entity_node(
                        entity_name=entity['name'],
                        entity_type=entity['type']
                    )
                    
                    # Create MENTIONS relationship
                    if self.neo4j.driver:
                        with self.neo4j.driver.session() as session:
                            session.run("""
                                MATCH (a:Article {supabase_id: $article_id})
                                MATCH (e:Entity {name: $entity_name, type: $entity_type})
                                MERGE (a)-[:MENTIONS {
                                    context: $context,
                                    confidence: $confidence
                                }]->(e)
                            """, 
                            article_id=supabase_article_id,
                            entity_name=entity['name'],
                            entity_type=entity['type'],
                            context=entity.get('context', ''),
                            confidence=entity.get('confidence', 0.9))
                
                except Exception as entity_error:
                    logger.error(f"Error processing Neo4j entity {entity['name']}: {str(entity_error)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing Neo4j data: {str(e)}")


async def main():
    """Main function to run the data ingestion pipeline"""
    processor = NewsDataProcessor()
    
    # Process sample dataset or specify your own dataset path
    dataset_path = "sample_news_dataset.json"  # This will create sample data
    
    # You can also specify a real dataset:
    # dataset_path = "/path/to/your/news_dataset.csv"
    
    await processor.process_dataset(dataset_path, limit=50)


if __name__ == "__main__":
    asyncio.run(main())
