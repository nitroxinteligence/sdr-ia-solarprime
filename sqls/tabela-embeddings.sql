create table public.embeddings (
  id uuid not null default gen_random_uuid (),
  content text not null,
  content_type character varying(50) not null,
  embedding public.vector null,
  metadata jsonb null,
  source character varying(200) null,
  chunk_index integer null,
  total_chunks integer null,
  parent_id uuid null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint embeddings_pkey primary key (id),
  constraint embeddings_content_type_check check (
    (
      (content_type)::text = any (
        array[
          ('KNOWLEDGE_BASE'::character varying)::text,
          ('CONVERSATION'::character varying)::text,
          ('DOCUMENT'::character varying)::text,
          ('PRODUCT_INFO'::character varying)::text,
          ('FAQ'::character varying)::text,
          ('COMPANY_INFO'::character varying)::text,
          ('PRICING'::character varying)::text,
          ('TECHNICAL_SPEC'::character varying)::text
        ]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_embeddings_content_type on public.embeddings using btree (content_type) TABLESPACE pg_default;

create index IF not exists idx_embeddings_source on public.embeddings using btree (source) TABLESPACE pg_default;

create index IF not exists idx_embeddings_parent on public.embeddings using btree (parent_id) TABLESPACE pg_default;

create index IF not exists idx_embeddings_created on public.embeddings using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists idx_embeddings_vector on public.embeddings using ivfflat (embedding vector_cosine_ops)
with
  (lists = '100') TABLESPACE pg_default;

create index IF not exists idx_embeddings_content_search on public.embeddings using gin (to_tsvector('portuguese'::regconfig, content)) TABLESPACE pg_default;

create trigger update_embeddings_updated_at BEFORE
update on embeddings for EACH row
execute FUNCTION update_updated_at_column ();