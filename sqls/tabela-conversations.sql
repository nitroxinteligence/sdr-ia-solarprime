create table public.conversations (
  id uuid not null default extensions.uuid_generate_v4 (),
  lead_id uuid null,
  session_id character varying(100) not null,
  started_at timestamp with time zone null default CURRENT_TIMESTAMP,
  ended_at timestamp with time zone null,
  total_messages integer null default 0,
  current_stage character varying(50) null,
  sentiment character varying(20) null default 'neutro'::character varying,
  is_active boolean null default true,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  phone_number character varying(50) null,
  channel character varying(50) null default 'whatsapp'::character varying,
  metadata jsonb null,
  status character varying(20) null default 'ACTIVE'::character varying,
  emotional_state text null default 'ENTUSIASMADA'::text,
  constraint conversations_pkey primary key (id),
  constraint conversations_session_id_key unique (session_id),
  constraint conversations_lead_id_fkey foreign KEY (lead_id) references leads (id) on delete CASCADE,
  constraint conversations_channel_check check (
    (
      (channel)::text = any (
        (
          array[
            'whatsapp'::character varying,
            'email'::character varying,
            'sms'::character varying,
            'webchat'::character varying
          ]
        )::text[]
      )
    )
  ),
  constraint conversations_sentiment_check check (
    (
      (sentiment)::text = any (
        (
          array[
            'positivo'::character varying,
            'neutro'::character varying,
            'negativo'::character varying
          ]
        )::text[]
      )
    )
  ),
  constraint conversations_status_check check (
    (
      (status)::text = any (
        (
          array[
            'ACTIVE'::character varying,
            'PAUSED'::character varying,
            'COMPLETED'::character varying,
            'ARCHIVED'::character varying
          ]
        )::text[]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_conversations_emotional_state on public.conversations using btree (emotional_state) TABLESPACE pg_default;

create index IF not exists idx_conversations_lead on public.conversations using btree (lead_id) TABLESPACE pg_default;

create index IF not exists idx_conversations_session on public.conversations using btree (session_id) TABLESPACE pg_default;

create index IF not exists idx_conversations_active on public.conversations using btree (is_active) TABLESPACE pg_default;

create index IF not exists idx_conversations_created on public.conversations using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists idx_conversations_created_brin on public.conversations using brin (created_at) TABLESPACE pg_default;

create index IF not exists idx_conversations_phone on public.conversations using btree (phone_number) TABLESPACE pg_default;

create trigger update_conversations_updated_at BEFORE
update on conversations for EACH row
execute FUNCTION update_updated_at_column ();