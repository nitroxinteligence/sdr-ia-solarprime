create table public.analytics (
  id uuid not null default gen_random_uuid(),
  lead_id uuid null,
  phone_number character varying(50) null,
  event_type character varying(50) not null,
  event_category character varying(50) null,
  event_data jsonb null,
  session_id character varying(255) null,
  conversation_id uuid null,
  timestamp timestamp with time zone null default CURRENT_TIMESTAMP,
  user_agent text null,
  ip_address inet null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint analytics_pkey primary key (id),
  constraint analytics_lead_id_fkey foreign key (lead_id) references leads (id) on delete CASCADE,
  constraint analytics_conversation_id_fkey foreign key (conversation_id) references conversations (id) on delete CASCADE,
  constraint analytics_event_type_check check (
    (event_type)::text = any (
      (
        array[
          'CONVERSATION_START'::character varying,
          'CONVERSATION_END'::character varying,
          'MESSAGE_SENT'::character varying,
          'MESSAGE_RECEIVED'::character varying,
          'LEAD_QUALIFIED'::character varying,
          'LEAD_DISQUALIFIED'::character varying,
          'MEETING_SCHEDULED'::character varying,
          'MEETING_CANCELLED'::character varying,
          'MEETING_RESCHEDULED'::character varying,
          'FOLLOW_UP_SENT'::character varying,
          'FOLLOW_UP_OPENED'::character varying,
          'MEDIA_RECEIVED'::character varying,
          'MEDIA_PROCESSED'::character varying,
          'ERROR_OCCURRED'::character varying,
          'STAGE_CHANGED'::character varying
        ]
      )::text[]
    )
  ),
  constraint analytics_event_category_check check (
    (event_category)::text = any (
      (
        array[
          'CONVERSATION'::character varying,
          'QUALIFICATION'::character varying,
          'MEETING'::character varying,
          'FOLLOW_UP'::character varying,
          'MEDIA'::character varying,
          'SYSTEM'::character varying,
          'USER_ACTION'::character varying
        ]
      )::text[]
    )
  )
) TABLESPACE pg_default;

-- Índices para otimizar consultas analíticas
create index IF not exists idx_analytics_lead_id on public.analytics using btree (lead_id) TABLESPACE pg_default;

create index IF not exists idx_analytics_phone on public.analytics using btree (phone_number) TABLESPACE pg_default;

create index IF not exists idx_analytics_event_type on public.analytics using btree (event_type) TABLESPACE pg_default;

create index IF not exists idx_analytics_event_category on public.analytics using btree (event_category) TABLESPACE pg_default;

create index IF not exists idx_analytics_session on public.analytics using btree (session_id) TABLESPACE pg_default;

create index IF not exists idx_analytics_conversation on public.analytics using btree (conversation_id) TABLESPACE pg_default;

create index IF not exists idx_analytics_timestamp on public.analytics using btree (timestamp desc) TABLESPACE pg_default;

create index IF not exists idx_analytics_created on public.analytics using btree (created_at desc) TABLESPACE pg_default;

-- Índice composto para queries de performance
create index IF not exists idx_analytics_daily on public.analytics using btree (
  date_trunc('day', timestamp),
  event_type,
  event_category
) TABLESPACE pg_default;

-- Índice para análise de eventos por lead
create index IF not exists idx_analytics_lead_events on public.analytics using btree (
  lead_id,
  event_type,
  timestamp desc
) TABLESPACE pg_default
where
  (lead_id IS NOT NULL);