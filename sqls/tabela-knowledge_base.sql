create table public.knowledge_base (
  id uuid not null default extensions.uuid_generate_v4 (),
  title character varying(200) not null,
  content text not null,
  category character varying(50) null,
  tags text[] null,
  source character varying(100) null,
  priority integer null default 1,
  is_active boolean null default true,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint knowledge_base_pkey primary key (id),
  constraint knowledge_base_priority_check check (
    (
      (priority >= 1)
      and (priority <= 10)
    )
  )
) TABLESPACE pg_default;

-- Índices para otimizar buscas
create index IF not exists idx_knowledge_base_category on public.knowledge_base using btree (category) TABLESPACE pg_default;

create index IF not exists idx_knowledge_base_active on public.knowledge_base using btree (is_active) TABLESPACE pg_default;

create index IF not exists idx_knowledge_base_priority on public.knowledge_base using btree (priority desc) TABLESPACE pg_default;

create index IF not exists idx_knowledge_base_created on public.knowledge_base using btree (created_at desc) TABLESPACE pg_default;

-- Índice para busca full-text no conteúdo
create index IF not exists idx_knowledge_base_content_search on public.knowledge_base using gin (to_tsvector('portuguese', content)) TABLESPACE pg_default;

-- Índice para busca full-text no título
create index IF not exists idx_knowledge_base_title_search on public.knowledge_base using gin (to_tsvector('portuguese', title)) TABLESPACE pg_default;

-- Índice para busca em tags
create index IF not exists idx_knowledge_base_tags on public.knowledge_base using gin (tags) TABLESPACE pg_default;

-- Trigger para atualizar updated_at automaticamente
create trigger update_knowledge_base_updated_at BEFORE
update on knowledge_base for EACH row
execute FUNCTION update_updated_at_column ();