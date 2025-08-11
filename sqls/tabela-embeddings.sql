-- Enable pgvector extension (run as superuser)
CREATE EXTENSION IF NOT EXISTS vector;

create table public.embeddings (
  id uuid not null default gen_random_uuid(),
  content text not null,
  content_type character varying(50) not null,
  embedding vector(768),  -- Gemini usa 768 dimensões por padrão
  metadata jsonb null,
  source character varying(200) null,
  chunk_index integer null,
  total_chunks integer null,
  parent_id uuid null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint embeddings_pkey primary key (id),
  constraint embeddings_content_type_check check (
    (content_type)::text = any (
      (
        array[
          'KNOWLEDGE_BASE'::character varying,
          'CONVERSATION'::character varying,
          'DOCUMENT'::character varying,
          'PRODUCT_INFO'::character varying,
          'FAQ'::character varying,
          'COMPANY_INFO'::character varying,
          'PRICING'::character varying,
          'TECHNICAL_SPEC'::character varying
        ]
      )::text[]
    )
  )
) TABLESPACE pg_default;

-- Índices para otimizar buscas
create index IF not exists idx_embeddings_content_type on public.embeddings using btree (content_type) TABLESPACE pg_default;

create index IF not exists idx_embeddings_source on public.embeddings using btree (source) TABLESPACE pg_default;

create index IF not exists idx_embeddings_parent on public.embeddings using btree (parent_id) TABLESPACE pg_default;

create index IF not exists idx_embeddings_created on public.embeddings using btree (created_at desc) TABLESPACE pg_default;

-- Índice para busca vetorial usando ivfflat
create index IF not exists idx_embeddings_vector on public.embeddings 
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Índice para busca full-text no conteúdo
create index IF not exists idx_embeddings_content_search on public.embeddings 
using gin (to_tsvector('portuguese', content)) TABLESPACE pg_default;

-- Trigger para atualizar updated_at automaticamente
create trigger update_embeddings_updated_at BEFORE
update on embeddings for EACH row
execute FUNCTION update_updated_at_column();

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