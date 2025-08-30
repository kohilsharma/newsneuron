-- NewsNeuron Supabase Database Schema
-- This file contains the complete database schema for the NewsNeuron project

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Articles table - stores news articles with vector embeddings
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT UNIQUE,
    published_date TIMESTAMP WITH TIME ZONE,
    source VARCHAR(100),
    embedding VECTOR(384), -- sentence-transformers/all-MiniLM-L6-v2 dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Entities table - stores extracted entities
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL, -- PERSON, ORGANIZATION, LOCATION, EVENT
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Junction table for many-to-many relationship between articles and entities
CREATE TABLE IF NOT EXISTS article_entities (
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    confidence FLOAT DEFAULT 1.0, -- NER confidence score
    context TEXT, -- Context where entity was mentioned
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (article_id, entity_id)
);

-- Chunks table - stores article chunks with embeddings for improved retrieval
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table - stores chat conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table - stores chat messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    metadata JSONB, -- For storing sources, entities, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Flashcards table - stores generated flashcards
CREATE TABLE IF NOT EXISTS flashcards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_points JSONB NOT NULL, -- Array of key points
    entities JSONB, -- Array of entity objects
    source_articles JSONB, -- Array of source article references
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_published_date ON articles(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_title_trgm ON articles USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_articles_content_trgm ON articles USING gin(content gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_name_trgm ON entities USING gin(name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_article_entities_article_id ON article_entities(article_id);
CREATE INDEX IF NOT EXISTS idx_article_entities_entity_id ON article_entities(entity_id);

CREATE INDEX IF NOT EXISTS idx_chunks_article_id ON chunks(article_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index ON chunks(chunk_index);

CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_flashcards_category ON flashcards(category);
CREATE INDEX IF NOT EXISTS idx_flashcards_created_at ON flashcards(created_at DESC);

-- Vector similarity search function for chunks
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.78,
    match_count int DEFAULT 20
)
RETURNS TABLE (
    id int,
    article_id int,
    chunk_index int,
    content text,
    similarity float
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        chunks.id,
        chunks.article_id,
        chunks.chunk_index,
        chunks.content,
        1 - (chunks.embedding <=> query_embedding) AS similarity
    FROM chunks
    WHERE chunks.embedding IS NOT NULL
      AND 1 - (chunks.embedding <=> query_embedding) > match_threshold
    ORDER BY chunks.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_articles(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.78,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id int,
    title text,
    content text,
    url text,
    published_date timestamptz,
    source varchar(100),
    similarity float
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        articles.id,
        articles.title,
        articles.content,
        articles.url,
        articles.published_date,
        articles.source,
        1 - (articles.embedding <=> query_embedding) AS similarity
    FROM articles
    WHERE 1 - (articles.embedding <=> query_embedding) > match_threshold
    ORDER BY articles.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_articles_updated_at 
    BEFORE UPDATE ON articles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entities_updated_at 
    BEFORE UPDATE ON entities 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_flashcards_updated_at 
    BEFORE UPDATE ON flashcards 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW recent_articles AS
SELECT 
    id,
    title,
    content,
    url,
    published_date,
    source,
    created_at
FROM articles
WHERE published_date >= NOW() - INTERVAL '30 days'
ORDER BY published_date DESC;

ALTER VIEW recent_articles SET (security_invoker = on);

CREATE OR REPLACE VIEW entity_mention_counts AS
SELECT 
    e.id,
    e.name,
    e.type,
    COUNT(ae.article_id) as mention_count,
    MAX(a.published_date) as last_mentioned
FROM entities e
LEFT JOIN article_entities ae ON e.id = ae.entity_id
LEFT JOIN articles a ON ae.article_id = a.id
GROUP BY e.id, e.name, e.type
ORDER BY mention_count DESC;

ALTER VIEW entity_mention_counts SET (security_invoker = on);

-- Row Level Security (RLS) policies
-- Enable RLS on user-specific tables
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE flashcards ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE article_entities ENABLE ROW LEVEL SECURITY;

-- Policies for articles
CREATE POLICY "Enable read access for all users" ON articles
    FOR SELECT USING (TRUE);
CREATE POLICY "Enable write access for all users" ON articles
    FOR INSERT WITH CHECK (TRUE);
CREATE POLICY "Enable update access for all users" ON articles
    FOR UPDATE USING (TRUE);
CREATE POLICY "Enable delete access for all users" ON articles
    FOR DELETE USING (TRUE);

-- Policies for entities
CREATE POLICY "Enable read access for all users" ON entities
    FOR SELECT USING (TRUE);
CREATE POLICY "Enable write access for all users" ON entities
    FOR INSERT WITH CHECK (TRUE);
CREATE POLICY "Enable update access for all users" ON entities
    FOR UPDATE USING (TRUE);
CREATE POLICY "Enable delete access for all users" ON entities
    FOR DELETE USING (TRUE);

-- Policies for article_entities
CREATE POLICY "Enable read access for all users" ON article_entities
    FOR SELECT USING (TRUE);
CREATE POLICY "Enable write access for all users" ON article_entities
    FOR INSERT WITH CHECK (TRUE);
CREATE POLICY "Enable update access for all users" ON article_entities
    FOR UPDATE USING (TRUE);
CREATE POLICY "Enable delete access for all users" ON article_entities
    FOR DELETE USING (TRUE);

-- Policies for conversations (basic - can be enhanced with proper auth)
CREATE POLICY "Enable read access for all users" ON conversations
    FOR SELECT USING (TRUE);

CREATE POLICY "Enable insert access for all users" ON conversations
    FOR INSERT WITH CHECK (TRUE);

CREATE POLICY "Enable update access for all users" ON conversations
    FOR UPDATE USING (TRUE);

CREATE POLICY "Enable delete access for all users" ON conversations
    FOR DELETE USING (TRUE);

-- Policies for messages
CREATE POLICY "Enable read access for all users" ON messages
    FOR SELECT USING (TRUE);

CREATE POLICY "Enable insert access for all users" ON messages
    FOR INSERT WITH CHECK (TRUE);

-- Policies for flashcards
CREATE POLICY "Enable read access for all users" ON flashcards
    FOR SELECT USING (TRUE);

CREATE POLICY "Enable insert access for all users" ON flashcards
    FOR INSERT WITH CHECK (TRUE);

CREATE POLICY "Enable update access for all users" ON flashcards
    FOR UPDATE USING (TRUE);

CREATE POLICY "Enable delete access for all users" ON flashcards
    FOR DELETE USING (TRUE);

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO service_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- Sample data insertion function (for development)
CREATE OR REPLACE FUNCTION insert_sample_data()
RETURNS void AS $$
BEGIN
    -- Insert sample entities
    INSERT INTO entities (name, type, description) VALUES
    ('OpenAI', 'ORGANIZATION', 'AI research company'),
    ('Elon Musk', 'PERSON', 'CEO of Tesla and SpaceX'),
    ('San Francisco', 'LOCATION', 'City in California'),
    ('Climate Summit 2024', 'EVENT', 'International climate conference')
    ON CONFLICT (name) DO NOTHING;
    
    -- Insert sample articles (without embeddings for now)
    INSERT INTO articles (title, content, url, published_date, source) VALUES
    (
        'AI Breakthrough in Language Models',
        'Recent developments in artificial intelligence have shown remarkable progress in language understanding and generation capabilities.',
        'https://example.com/ai-breakthrough',
        NOW() - INTERVAL '1 day',
        'TechNews'
    ),
    (
        'Climate Change Summit Begins',
        'World leaders gather to discuss urgent climate action and sustainable development goals for the next decade.',
        'https://example.com/climate-summit',
        NOW() - INTERVAL '2 days',
        'GlobalNews'
    )
    ON CONFLICT (url) DO NOTHING;
    
    RAISE NOTICE 'Sample data inserted successfully';
END;
$$ LANGUAGE plpgsql;

-- Comment for usage
COMMENT ON FUNCTION insert_sample_data() IS 'Inserts sample data for development and testing purposes';
COMMENT ON FUNCTION match_articles(vector, float, int) IS 'Performs vector similarity search on articles using pgvector';
COMMENT ON TABLE articles IS 'Stores news articles with vector embeddings for semantic search';
COMMENT ON TABLE entities IS 'Stores named entities extracted from articles';
COMMENT ON TABLE article_entities IS 'Many-to-many relationship between articles and entities';
COMMENT ON TABLE conversations IS 'Stores chat conversation metadata';
COMMENT ON TABLE messages IS 'Stores individual chat messages within conversations';
COMMENT ON TABLE flashcards IS 'Stores AI-generated news flashcards';
