create table public.agent_sessions (
  id uuid not null default gen_random_uuid (),
  session_id character varying(255) not null,
  phone_number character varying(50) not null,
  state jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  last_interaction timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint agent_sessions_pkey primary key (id),
  constraint agent_sessions_session_id_key unique (session_id)
) TABLESPACE pg_default;

create index IF not exists idx_agent_sessions_session_id on public.agent_sessions using btree (session_id) TABLESPACE pg_default;

create index IF not exists idx_agent_sessions_phone_number on public.agent_sessions using btree (phone_number) TABLESPACE pg_default;

create index IF not exists idx_agent_sessions_last_interaction on public.agent_sessions using btree (last_interaction) TABLESPACE pg_default;

create trigger agent_sessions_updated_at_trigger BEFORE
update on agent_sessions for EACH row
execute FUNCTION update_agent_sessions_updated_at ();