// NewsNeuron Neo4j Knowledge Graph Schema
// This file contains the graph schema and sample data for the NewsNeuron project

// Create constraints for better performance and data integrity

// Entity constraints
CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;
CREATE CONSTRAINT article_supabase_id_unique IF NOT EXISTS FOR (a:Article) REQUIRE a.supabase_id IS UNIQUE;

// Create indexes for better query performance
CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.type);
CREATE INDEX article_published_date_index IF NOT EXISTS FOR (a:Article) ON (a.published_date);
CREATE INDEX article_source_index IF NOT EXISTS FOR (a:Article) ON (a.source);

// Sample schema setup - Entity nodes
// These will be created by the data processing pipeline, but here's the structure:

/*
Node Types:
1. Entity - Represents all named entities
   Properties:
   - name: string (unique)
   - type: string (PERSON, ORGANIZATION, LOCATION, EVENT)
   - description: string (optional)
   - supabase_id: integer (link to Supabase entities table)
   - first_mentioned: datetime
   - last_mentioned: datetime
   - mention_count: integer

2. Article - Represents news articles
   Properties:
   - supabase_id: integer (unique, links to Supabase articles table)
   - title: string
   - published_date: datetime
   - source: string
   - url: string (optional)
*/

// Sample data creation (for development and testing)
// This demonstrates the graph structure

// Create sample entities
MERGE (openai:Entity {name: "OpenAI", type: "ORGANIZATION"})
SET openai.description = "AI research company",
    openai.first_mentioned = datetime("2023-01-01T00:00:00Z"),
    openai.last_mentioned = datetime(),
    openai.mention_count = 5;

MERGE (elon:Entity {name: "Elon Musk", type: "PERSON"})
SET elon.description = "CEO of Tesla and SpaceX",
    elon.first_mentioned = datetime("2023-01-01T00:00:00Z"),
    elon.last_mentioned = datetime(),
    elon.mention_count = 8;

MERGE (sf:Entity {name: "San Francisco", type: "LOCATION"})
SET sf.description = "City in California",
    sf.first_mentioned = datetime("2023-01-01T00:00:00Z"),
    sf.last_mentioned = datetime(),
    sf.mention_count = 3;

MERGE (tesla:Entity {name: "Tesla", type: "ORGANIZATION"})
SET tesla.description = "Electric vehicle company",
    tesla.first_mentioned = datetime("2023-01-01T00:00:00Z"),
    tesla.last_mentioned = datetime(),
    tesla.mention_count = 6;

MERGE (ai_summit:Entity {name: "AI Summit 2024", type: "EVENT"})
SET ai_summit.description = "Annual AI conference",
    ai_summit.first_mentioned = datetime("2024-01-01T00:00:00Z"),
    ai_summit.last_mentioned = datetime(),
    ai_summit.mention_count = 2;

// Create sample articles
MERGE (article1:Article {supabase_id: 1})
SET article1.title = "AI Breakthrough in Language Models",
    article1.published_date = datetime(),
    article1.source = "TechNews",
    article1.url = "https://example.com/ai-breakthrough";

MERGE (article2:Article {supabase_id: 2})
SET article2.title = "Tesla's New Factory Opens in Texas",
    article2.published_date = datetime(),
    article2.source = "AutoNews",
    article2.url = "https://example.com/tesla-factory";

MERGE (article3:Article {supabase_id: 3})
SET article3.title = "Elon Musk Speaks at AI Summit",
    article3.published_date = datetime(),
    article3.source = "TechConf",
    article3.url = "https://example.com/musk-ai-summit";

// Create relationships between articles and entities (MENTIONS)
MERGE (article1)-[:MENTIONS {context: "discusses latest AI developments", confidence: 0.95}]->(openai);
MERGE (article2)-[:MENTIONS {context: "new manufacturing facility", confidence: 0.98}]->(tesla);
MERGE (article2)-[:MENTIONS {context: "CEO announcement", confidence: 0.90}]->(elon);
MERGE (article3)-[:MENTIONS {context: "keynote speaker", confidence: 0.95}]->(elon);
MERGE (article3)-[:MENTIONS {context: "event location", confidence: 0.85}]->(ai_summit);
MERGE (article3)-[:MENTIONS {context: "AI technology discussion", confidence: 0.88}]->(openai);

// Create relationships between entities
MERGE (elon)-[:WORKS_FOR {role: "CEO", since: datetime("2008-01-01T00:00:00Z")}]->(tesla);
MERGE (elon)-[:PARTICIPATED_IN {role: "speaker", date: datetime()}]->(ai_summit);
MERGE (tesla)-[:LOCATED_IN {type: "headquarters"}]->(sf);
MERGE (ai_summit)-[:RELATED_TO {type: "topic"}]->(openai);

/*
Relationship Types:
1. MENTIONS - Article mentions an entity
   Properties:
   - context: string (context of the mention)
   - confidence: float (NER confidence score)
   - sentiment: string (optional: positive, negative, neutral)

2. WORKS_FOR - Person works for organization
   Properties:
   - role: string
   - since: datetime
   - until: datetime (optional)

3. LOCATED_IN - Entity is located in a location
   Properties:
   - type: string (headquarters, office, event_location, etc.)
   - since: datetime (optional)

4. PARTICIPATED_IN - Entity participated in an event
   Properties:
   - role: string
   - date: datetime

5. RELATED_TO - General relationship between entities
   Properties:
   - type: string (topic, partnership, competitor, etc.)
   - strength: float (relationship strength)

6. SIMILAR_TO - Entities are similar or related
   Properties:
   - similarity_score: float
   - reason: string
*/

// Useful queries for the application

// Query 1: Get timeline for an entity
// MATCH (a:Article)-[:MENTIONS]->(e:Entity)
// WHERE e.name = $entity_name
// RETURN a.title, a.published_date, a.supabase_id, a.source, a.url
// ORDER BY a.published_date DESC
// LIMIT $limit;

// Query 2: Get related entities
// MATCH (start:Entity {name: $entity_name})
// MATCH path = (start)-[*1..2]-(related:Entity)
// WHERE related.name <> start.name
// RETURN DISTINCT related.name, related.type, length(path) as distance
// ORDER BY distance, related.mention_count DESC
// LIMIT $limit;

// Query 3: Get entities mentioned together
// MATCH (a:Article)-[:MENTIONS]->(e1:Entity)
// MATCH (a)-[:MENTIONS]->(e2:Entity)
// WHERE e1.name = $entity_name AND e1 <> e2
// RETURN e2.name, e2.type, count(a) as co_mentions
// ORDER BY co_mentions DESC
// LIMIT $limit;

// Query 4: Get trending entities (most mentioned recently)
// MATCH (a:Article)-[:MENTIONS]->(e:Entity)
// WHERE a.published_date >= datetime() - duration('P30D')
// RETURN e.name, e.type, count(a) as recent_mentions
// ORDER BY recent_mentions DESC
// LIMIT $limit;

// Query 5: Get story evolution for an entity
// MATCH (a:Article)-[:MENTIONS]->(e:Entity)
// WHERE e.name = $entity_name
// WITH a, e, date(a.published_date) as mention_date
// RETURN mention_date, count(a) as daily_mentions, collect(a.title)[0..3] as sample_titles
// ORDER BY mention_date DESC
// LIMIT $limit;

// Query 6: Find influential entities (high centrality in the graph)
// MATCH (e:Entity)-[r]-(other:Entity)
// RETURN e.name, e.type, count(r) as connections, e.mention_count
// ORDER BY connections DESC, e.mention_count DESC
// LIMIT $limit;

// Functions for common operations

// Procedure to add a new article with entity mentions
// This would be called from the data processing pipeline
/*
CALL apoc.create.node(['Article'], {
    supabase_id: $supabase_id,
    title: $title,
    published_date: datetime($published_date),
    source: $source,
    url: $url
}) YIELD node as article
WITH article
UNWIND $entities as entity_data
MERGE (e:Entity {name: entity_data.name, type: entity_data.type})
ON CREATE SET e.first_mentioned = datetime($published_date),
              e.mention_count = 1
ON MATCH SET e.last_mentioned = datetime($published_date),
             e.mention_count = e.mention_count + 1
MERGE (article)-[:MENTIONS {
    context: entity_data.context,
    confidence: entity_data.confidence
}]->(e);
*/

// Maintenance queries

// Update mention counts
// MATCH (e:Entity)
// OPTIONAL MATCH (e)<-[:MENTIONS]-(a:Article)
// SET e.mention_count = count(a);

// Update first and last mentioned dates
// MATCH (e:Entity)
// OPTIONAL MATCH (e)<-[:MENTIONS]-(a:Article)
// WITH e, min(a.published_date) as first, max(a.published_date) as last
// SET e.first_mentioned = first, e.last_mentioned = last;

// Database statistics query
// MATCH (n) 
// RETURN labels(n) as NodeType, count(n) as Count
// UNION ALL
// MATCH ()-[r]->()
// RETURN type(r) as RelationshipType, count(r) as Count;

// Cleanup queries (for development)
// Remove all sample data:
// MATCH (n) WHERE n.name IN ["OpenAI", "Elon Musk", "Tesla", "San Francisco", "AI Summit 2024"] OR n.supabase_id IN [1, 2, 3] DETACH DELETE n;

// Performance optimization
// These indexes should be created after data ingestion for better performance:
// CREATE INDEX entity_mention_count IF NOT EXISTS FOR (e:Entity) ON (e.mention_count);
// CREATE INDEX entity_last_mentioned IF NOT EXISTS FOR (e:Entity) ON (e.last_mentioned);

RETURN "NewsNeuron Neo4j schema initialized successfully" as status;
