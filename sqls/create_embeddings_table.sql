-- Script para criar a tabela embeddings no Supabase
-- Execute este script no SQL Editor do Supabase

-- Enable pgvector extension (run as superuser)
CREATE EXTENSION IF NOT EXISTS vector;

-- Criar tabela embeddings se não existir
CREATE TABLE IF NOT EXISTS public.embeddings (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  content text NOT NULL,
  content_type character varying(50) NOT NULL,
  embedding vector(768),  -- Gemini usa 768 dimensões
  metadata jsonb NULL,
  source character varying(200) NULL,
  chunk_index integer NULL,
  total_chunks integer NULL,
  parent_id uuid NULL,
  created_at timestamp with time zone NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT embeddings_pkey PRIMARY KEY (id),
  CONSTRAINT embeddings_content_type_check CHECK (
    (content_type)::text = ANY (
      ARRAY[
        'KNOWLEDGE_BASE'::character varying,
        'CONVERSATION'::character varying,
        'DOCUMENT'::character varying,
        'PRODUCT_INFO'::character varying,
        'FAQ'::character varying,
        'COMPANY_INFO'::character varying,
        'PRICING'::character varying,
        'TECHNICAL_SPEC'::character varying
      ]::text[]
    )
  )
);

-- Índices para otimizar buscas
CREATE INDEX IF NOT EXISTS idx_embeddings_content_type ON public.embeddings USING btree (content_type);
CREATE INDEX IF NOT EXISTS idx_embeddings_source ON public.embeddings USING btree (source);
CREATE INDEX IF NOT EXISTS idx_embeddings_parent ON public.embeddings USING btree (parent_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_created ON public.embeddings USING btree (created_at DESC);

-- Índice para busca vetorial usando ivfflat
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON public.embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Índice para busca full-text no conteúdo
CREATE INDEX IF NOT EXISTS idx_embeddings_content_search ON public.embeddings 
USING gin (to_tsvector('portuguese', content));

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at automaticamente
CREATE TRIGGER update_embeddings_updated_at BEFORE UPDATE ON embeddings 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Função para busca semântica (similarity search)
CREATE OR REPLACE FUNCTION search_embeddings(
  query_embedding vector(768),
  match_count int DEFAULT 5,
  filter_type text DEFAULT NULL
)
RETURNS TABLE(
  id uuid,
  content text,
  content_type character varying,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    e.id,
    e.content,
    e.content_type,
    e.metadata,
    1 - (e.embedding <=> query_embedding) as similarity
  FROM embeddings e
  WHERE (filter_type IS NULL OR e.content_type = filter_type)
    AND e.embedding IS NOT NULL
  ORDER BY e.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Função para busca híbrida (vetorial + full-text)
CREATE OR REPLACE FUNCTION hybrid_search_embeddings(
  query_embedding vector(768),
  query_text text,
  match_count int DEFAULT 5,
  filter_type text DEFAULT NULL,
  vector_weight float DEFAULT 0.5
)
RETURNS TABLE(
  id uuid,
  content text,
  content_type character varying,
  metadata jsonb,
  combined_score float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH vector_search AS (
    SELECT
      e.id,
      1 - (e.embedding <=> query_embedding) as vector_score
    FROM embeddings e
    WHERE (filter_type IS NULL OR e.content_type = filter_type)
      AND e.embedding IS NOT NULL
  ),
  text_search AS (
    SELECT
      e.id,
      ts_rank(to_tsvector('portuguese', e.content), plainto_tsquery('portuguese', query_text)) as text_score
    FROM embeddings e
    WHERE to_tsvector('portuguese', e.content) @@ plainto_tsquery('portuguese', query_text)
      AND (filter_type IS NULL OR e.content_type = filter_type)
  )
  SELECT
    e.id,
    e.content,
    e.content_type,
    e.metadata,
    (COALESCE(v.vector_score, 0) * vector_weight + 
     COALESCE(t.text_score, 0) * (1 - vector_weight)) as combined_score
  FROM embeddings e
  LEFT JOIN vector_search v ON e.id = v.id
  LEFT JOIN text_search t ON e.id = t.id
  WHERE v.id IS NOT NULL OR t.id IS NOT NULL
  ORDER BY combined_score DESC
  LIMIT match_count;
END;
$$;

-- Verificar se a tabela foi criada corretamente
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'embeddings'
ORDER BY ordinal_position;