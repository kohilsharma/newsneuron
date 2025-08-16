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
    embedding VECTOR(1536), -- OpenAI embedding dimension
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

-- Conversations table - stores chat conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT, -- Can be extended to proper user system later
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
    user_id TEXT,
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

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_flashcards_user_id ON flashcards(user_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_category ON flashcards(category);
CREATE INDEX IF NOT EXISTS idx_flashcards_created_at ON flashcards(created_at DESC);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_articles(
    query_embedding vector(1536),
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

-- Row Level Security (RLS) policies
-- Enable RLS on user-specific tables
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE flashcards ENABLE ROW LEVEL SECURITY;

-- Policies for conversations (basic - can be enhanced with proper auth)
CREATE POLICY "Users can view their own conversations" ON conversations
    FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert their own conversations" ON conversations
    FOR INSERT WITH CHECK (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can update their own conversations" ON conversations
    FOR UPDATE USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can delete their own conversations" ON conversations
    FOR DELETE USING (auth.uid()::text = user_id OR user_id IS NULL);

-- Policies for messages
CREATE POLICY "Users can view messages from their conversations" ON messages
    FOR SELECT USING (
        conversation_id IN (
            SELECT id FROM conversations 
            WHERE auth.uid()::text = user_id OR user_id IS NULL
        )
    );

CREATE POLICY "Users can insert messages to their conversations" ON messages
    FOR INSERT WITH CHECK (
        conversation_id IN (
            SELECT id FROM conversations 
            WHERE auth.uid()::text = user_id OR user_id IS NULL
        )
    );

-- Policies for flashcards
CREATE POLICY "Users can view their own flashcards" ON flashcards
    FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert their own flashcards" ON flashcards
    FOR INSERT WITH CHECK (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can update their own flashcards" ON flashcards
    FOR UPDATE USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can delete their own flashcards" ON flashcards
    FOR DELETE USING (auth.uid()::text = user_id OR user_id IS NULL);

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
