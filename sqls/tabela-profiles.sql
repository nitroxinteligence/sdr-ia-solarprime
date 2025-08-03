create table public.profiles (
  id uuid not null default extensions.uuid_generate_v4 (),
  phone_number character varying(50) not null,
  name character varying(100) null,
  email character varying(100) null,
  document character varying(20) null,
  profile_picture_url text null,
  preferences jsonb null,
  total_messages integer null default 0,
  last_interaction_at timestamp with time zone null,
  interaction_count integer null default 0,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint profiles_pkey primary key (id),
  constraint profiles_phone_number_key unique (phone_number)
) TABLESPACE pg_default;

-- Índices para otimizar consultas
create index IF not exists idx_profiles_phone on public.profiles using btree (phone_number) TABLESPACE pg_default;

create index IF not exists idx_profiles_name on public.profiles using btree (name) TABLESPACE pg_default;

create index IF not exists idx_profiles_email on public.profiles using btree (email) TABLESPACE pg_default;

create index IF not exists idx_profiles_last_interaction on public.profiles using btree (last_interaction_at desc) TABLESPACE pg_default;

create index IF not exists idx_profiles_created on public.profiles using btree (created_at desc) TABLESPACE pg_default;

-- Índice para busca full-text no nome
create index IF not exists idx_profiles_name_search on public.profiles using gin (to_tsvector('portuguese', name)) TABLESPACE pg_default;

-- Trigger para atualizar updated_at automaticamente
create trigger update_profiles_updated_at BEFORE
update on profiles for EACH row
execute FUNCTION update_updated_at_column ();