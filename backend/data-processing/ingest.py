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
from app.services.embedding_service import get_embedding_service
from langchain_text_splitters import RecursiveCharacterTextSplitter


class NewsDataProcessor:
    """
    Main data processing class for NewsNeuron
    Handles data ingestion, entity extraction, embedding generation, and database population
    """
    
    def __init__(self):
        self.supabase_client: Optional[SupabaseClient] = None
        self.neo4j_client: Optional[Neo4jClient] = None
        self.nlp: Optional[spacy.Language] = None
        self.embedding_service = None
        self._setup_components()
        
    def _setup_components(self):
        """Initialize Supabase, Neo4j, spaCy, and OpenAI clients"""
        try:
            self.supabase_client = get_supabase_client()
            self.neo4j_client = get_neo4j_client()
            
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_md")
            logging.info("SpaCy model loaded successfully")
            
            # Setup embedding service
            self.embedding_service = get_embedding_service()
            backend_info = self.embedding_service.get_backend_info()
            logging.info(f"Embedding service initialized: {backend_info['backend']} backend using {backend_info['model']} ({backend_info['cost']})")

        except Exception as e:
            logging.error(f"Error setting up components: {str(e)}")
            raise

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
                    processed_count = await self._process_batch_optimized(batch)
                    total_processed += processed_count
                    logger.info(f"Processed batch {i//batch_size + 1}, Total processed: {total_processed}/{len(articles)}")
                    await asyncio.sleep(0)
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
            
            # Ensure datetime objects are converted to ISO strings
            if 'published_date' in article and isinstance(article['published_date'], datetime):
                article['published_date'] = article['published_date'].isoformat()
            
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
                'published_date': datetime.now().isoformat(),
                'source': 'TechNews'
            },
            {
                'title': 'Climate Summit Reaches Historic Agreement',
                'content': 'World leaders at the international climate summit have reached a historic agreement on carbon reduction targets. The agreement includes commitments from major economies to achieve net-zero emissions by 2050.',
                'url': 'https://example.com/climate-agreement',
                'published_date': datetime.now().isoformat(),
                'source': 'GlobalNews'
            },
            {
                'title': 'Tesla Unveils New Electric Vehicle Technology',
                'content': 'Tesla has announced revolutionary battery technology that could extend electric vehicle range to over 500 miles. CEO Elon Musk demonstrated the new technology at the company\'s annual innovation day.',
                'url': 'https://example.com/tesla-battery',
                'published_date': datetime.now().isoformat(),
                'source': 'AutoNews'
            },
            {
                'title': 'OpenAI Releases Advanced AI Assistant',
                'content': 'OpenAI has released a new version of its AI assistant with enhanced reasoning capabilities. The update includes improved performance in coding, mathematics, and complex problem-solving tasks.',
                'url': 'https://example.com/openai-release',
                'published_date': datetime.now().isoformat(),
                'source': 'AIDaily'
            },
            {
                'title': 'Space Mission Discovers New Exoplanets',
                'content': 'NASA\'s latest space mission has discovered multiple exoplanets in the habitable zone of nearby star systems. Scientists believe these planets could potentially support liquid water and life.',
                'url': 'https://example.com/exoplanets',
                'published_date': datetime.now().isoformat(),
                'source': 'ScienceNews'
            },
            {
                'title': 'Microsoft Announces Quantum Computing Milestone',
                'content': 'Microsoft researchers have achieved a major milestone in quantum computing, demonstrating error correction in a 1000-qubit system. This breakthrough brings practical quantum computing applications closer to reality.',
                'url': 'https://example.com/microsoft-quantum',
                'published_date': datetime.now().isoformat(),
                'source': 'TechNews'
            },
            {
                'title': 'Global Trade War Impacts Tech Sector',
                'content': 'Rising tensions between major economies have led to new tariffs on technology products. Industry analysts predict significant impacts on smartphone and semiconductor markets.',
                'url': 'https://example.com/trade-war-tech',
                'published_date': datetime.now().isoformat(),
                'source': 'EconomicTimes'
            },
            {
                'title': 'Renewable Energy Surpasses Coal Production',
                'content': 'For the first time in history, renewable energy sources have produced more electricity than coal-fired power plants globally. Solar and wind energy led the historic achievement.',
                'url': 'https://example.com/renewable-milestone',
                'published_date': datetime.now().isoformat(),
                'source': 'EnergyWatch'
            },
            {
                'title': 'Meta Launches Virtual Reality Workspace Platform',
                'content': 'Meta has unveiled a new virtual reality platform designed for remote work collaboration. The platform includes 3D meeting spaces, shared virtual whiteboards, and real-time document editing.',
                'url': 'https://example.com/meta-vr-workspace',
                'published_date': datetime.now().isoformat(),
                'source': 'TechCrunch'
            },
            {
                'title': 'Breakthrough in Alzheimer\'s Disease Treatment',
                'content': 'Clinical trials of a new Alzheimer\'s treatment show promising results in slowing cognitive decline. The drug targets amyloid plaques in the brain and has shown 35% reduction in progression.',
                'url': 'https://example.com/alzheimers-treatment',
                'published_date': datetime.now().isoformat(),
                'source': 'MedicalNews'
            }
        ]
        
        # Create unique articles by modifying base articles
        articles = []
        for i in range(count):
            base_article = sample_articles[i % len(sample_articles)].copy()
            
            # Make each article unique
            if i >= len(sample_articles):
                update_num = i // len(sample_articles) + 1
                base_article['title'] = f"{base_article['title']} - Update {update_num}"
                base_article['url'] = f"{base_article['url']}-update-{update_num}"
                # Vary the published date slightly
                from datetime import timedelta
                base_date = datetime.now() - timedelta(days=i)
                base_article['published_date'] = base_date.isoformat()
            
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

    async def _process_batch_optimized(self, batch: List[Dict[str, Any]]) -> int:
        """Optimized batch processing with batched embeddings and bulk inserts"""
        processed = 0

        # 0. Filter out already existing articles by URL
        urls = [a.get('url') for a in batch if a.get('url')]
        url_to_skip = set()
        for url in urls:
            try:
                existing = self.supabase_client.client.table("articles").select("id").eq("url", url).limit(1).execute()
                if existing.data:
                    url_to_skip.add(url)
            except Exception:
                pass

        to_insert_articles = []
        embed_inputs = []
        embed_map_idx = []

        for idx, article in enumerate(batch):
            if article.get('url') and article['url'] in url_to_skip:
                continue
            to_insert = {
                'title': article['title'],
                'content': article['content'],
                'url': article.get('url'),
                'published_date': article.get('published_date'),
                'source': article.get('source')
            }
            to_insert_articles.append(to_insert)
            embed_inputs.append(f"{article.get('title','')}: {article.get('content','')}")
            embed_map_idx.append(idx)

        # 1. Batch embeddings for full articles
        full_embeddings = await self.embedding_service.generate_embeddings(embed_inputs) if embed_inputs else []
        for j, emb in enumerate(full_embeddings):
            if emb is not None:
                to_insert_articles[j]['embedding'] = emb

        # 2. Bulk insert articles
        inserted = await self.supabase_client.insert_articles_bulk(to_insert_articles)
        id_by_title = {row['title']: row['id'] for row in inserted}

        # 3. For each inserted article, process entities and chunks (with batching)
        chunk_rows: List[Dict[str, Any]] = []
        chunk_texts: List[str] = []
        chunk_row_indices: List[int] = []

        for article in batch:
            if article['title'] not in id_by_title:
                continue
            article_id = id_by_title[article['title']]

            # Entities (keep as current per-entity to avoid complex joins)
            try:
                entities = self._extract_entities(article)
                await self._process_entities_supabase(entities, article_id)
            except Exception as e:
                logger.error(f"Entity processing error for article {article_id}: {str(e)}")

            # Neo4j
            try:
                await self._process_neo4j_data(article, entities if 'entities' in locals() else [], article_id)
            except Exception as e:
                logger.error(f"Neo4j processing error for article {article_id}: {str(e)}")

            # Prepare chunks for batch embed + bulk insert
            title = article.get('title') or ''
            content = article.get('content') or ''
            base_text = f"{title}\n\n{content}".strip()
            if not base_text:
                continue
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ". ", " "])
            chunks = splitter.split_text(base_text)
            start_idx = len(chunk_texts)
            for ci, ct in enumerate(chunks):
                chunk_texts.append(ct)
                chunk_row_indices.append(len(chunk_rows))
                row = {"article_id": article_id, "chunk_index": ci, "content": ct}
                chunk_rows.append(row)

            processed += 1

        # 4. Batch embed chunks
        if chunk_texts:
            chunk_embeddings = await self.embedding_service.generate_embeddings(chunk_texts)
            for k, emb in enumerate(chunk_embeddings):
                if emb is not None:
                    chunk_rows[k]["embedding"] = f"[{','.join(map(str, emb))}]"

        # 5. Bulk insert chunks
        if chunk_rows:
            await self.supabase_client.insert_chunks_bulk(chunk_rows)

        return processed
    
    async def _check_existing_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Check if an article with the given URL already exists"""
        try:
            if not self.supabase_client or not self.supabase_client.client:
                return None
            
            response = self.supabase_client.client.table("articles").select("id, title").eq("url", url).limit(1).execute()
            
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error checking existing article: {str(e)}")
            return None

    async def _process_single_article(self, article: Dict[str, Any]) -> bool:
        """
        Process a single article through the complete pipeline
        
        Args:
            article: Article dictionary
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if article already exists
            article_url = article.get('url')
            if article_url:
                existing_article = await self._check_existing_article(article_url)
                if existing_article:
                    print(f"Article already exists: {existing_article.get('title', 'Unknown')[:50]}")
                    return True
            
            # 1. Generate embedding for full text
            embedding = await self._generate_embedding(article)
            
            # 2. Extract entities
            entities = self._extract_entities(article)
            
            # 3. Insert article into Supabase
            article_data = {
                'title': article['title'],
                'content': article['content'],
                'url': article.get('url'),
                'published_date': article.get('published_date'),
                'source': article.get('source')
            }
            
            # Only include embedding if it was generated
            if embedding is not None:
                article_data['embedding'] = embedding
                logging.debug(f"Including embedding with {len(embedding)} dimensions")
            else:
                logging.debug("No embedding generated - article will be stored without embedding")
            
            try:
                supabase_article = await self.supabase_client.insert_article(article_data)
                article_id = supabase_article['id']
            except Exception as insert_error:
                # Handle duplicate URL errors gracefully
                if "duplicate key" in str(insert_error).lower() and "url" in str(insert_error).lower():
                    print(f"Article with URL already exists: {article_data.get('url')}")
                    return True
                else:
                    print(f"Error inserting article: {str(insert_error)}")
                    return False
            
            # 4. Process entities in Supabase
            entity_ids = await self._process_entities_supabase(entities, article_id)
            
            # 5. Create nodes and relationships in Neo4j
            try:
                await self._process_neo4j_data(article, entities, article_id)
            except Exception as neo4j_error:
                print(f"Error processing Neo4j data: {str(neo4j_error)}")
                # Continue even if Neo4j fails - the article is already in Supabase

            # 6. Split into chunks and store chunk embeddings
            try:
                await self._process_article_chunks(article, article_id)
            except Exception as chunk_error:
                logger.error(f"Error processing chunks for article {article_id}: {str(chunk_error)}")
            
            logger.debug(f"Successfully processed article: {article['title'][:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error in single article processing: {str(e)}")
            return False
    
    async def _generate_embedding(self, article: Dict[str, Any]) -> Optional[List[float]]:
        """
        Generate embedding for article content using free local models
        
        Args:
            article: Article dictionary
        
        Returns:
            List of embedding values or None if no embedding service available
        """
        try:
            text_to_embed = f"{article.get('title', '')}: {article.get('content', '')}"
            
            # Generate embedding using free local service
            embedding = await self.embedding_service.generate_embedding(text_to_embed)
            
            if embedding:
                logging.debug(f"Generated embedding with {len(embedding)} dimensions")
            else:
                logging.info("No embedding generated - embedding service not available")
            
            return embedding
            
        except Exception as e:
            logging.error(f"Error generating embedding: {str(e)}")
            return None

    async def _generate_text_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for arbitrary text using local embedding service"""
        try:
            return await self.embedding_service.generate_embedding(text)
        except Exception as e:
            logger.error(f"Error generating text embedding: {str(e)}")
            return None

    async def _process_article_chunks(self, article: Dict[str, Any], article_id: int):
        """Split article into chunks and store chunk rows with embeddings"""
        title = article.get('title') or ''
        content = article.get('content') or ''
        base_text = f"{title}\n\n{content}".strip()

        if not base_text:
            return

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " "]
        )
        chunks = splitter.split_text(base_text)

        for idx, chunk_text in enumerate(chunks):
            chunk_embedding = await self._generate_text_embedding(chunk_text)
            await self.supabase_client.insert_chunk(
                article_id=article_id,
                chunk_index=idx,
                content=chunk_text,
                embedding=chunk_embedding
            )
    
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
                # Use exact match to avoid duplicates
                existing_entities = await self.supabase_client.search_entities(
                    query=f"={entity['name']}",
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
                    new_entity = await self.supabase_client.insert_entity(entity_data)
                    entity_id = new_entity['id']
                
                # Link article to entity (ignore duplicates)
                try:
                    await self.supabase_client.link_article_entity(article_id, entity_id)
                except Exception as link_error:
                    # Ignore duplicate key errors
                    if "duplicate key" not in str(link_error).lower():
                        print(f"Error linking article {article_id} to entity {entity_id}: {str(link_error)}")
                
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
            print(f"Processing Neo4j data for article: {article['title'][:50]}...")
            
            if not self.neo4j_client or not self.neo4j_client.driver:
                print("Warning: Neo4j client or driver not available")
                return
            # Create article node
            published_date = article.get('published_date')
            # Convert datetime to ISO string if it's a datetime object
            if hasattr(published_date, 'isoformat'):
                published_date = published_date.isoformat()
            elif isinstance(published_date, str):
                # It's already a string, keep it as is
                pass
            else:
                published_date = None
                
            print(f"Creating article node in Neo4j: ID={supabase_article_id}, Title={article['title'][:30]}")
            await self.neo4j_client.create_article_node(
                supabase_id=supabase_article_id,
                title=article['title'],
                published_date=published_date,
                source=article.get('source')
            )
            print(f"Article node created successfully")
            
            # Create entity nodes and relationships
            print(f"Processing {len(entities)} entities for Neo4j")
            for entity in entities:
                try:
                    # Create entity node
                    print(f"Creating entity node: {entity['name']} ({entity['type']})")
                    await self.neo4j_client.create_entity_node(
                        entity_name=entity['name'],
                        entity_type=entity['type']
                    )
                    
                    # Create MENTIONS relationship using the async method
                    print(f"Creating MENTIONS relationship: Article {supabase_article_id} -> Entity {entity['name']}")
                    await self.neo4j_client.create_relationship(
                        from_node_label="Article",
                        from_node_props={"supabase_id": supabase_article_id},
                        to_node_label="Entity",
                        to_node_props={"name": entity['name'], "type": entity['type']},
                        relationship_type="MENTIONS",
                        properties={
                            "context": entity.get('context', ''),
                            "confidence": entity.get('confidence', 0.9)
                        }
                    )
                    print(f"Relationship created successfully")
                
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
    
    await processor.process_dataset(dataset_path, limit=20)


if __name__ == "__main__":
    asyncio.run(main())
