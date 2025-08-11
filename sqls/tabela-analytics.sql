create table public.analytics (
  id uuid not null default extensions.uuid_generate_v4 (),
  lead_id uuid null,
  event_type character varying(50) not null,
  event_data jsonb null default '{}'::jsonb,
  session_id character varying(100) null,
  user_agent character varying(255) null,
  ip_address character varying(45) null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  phone_number character varying(50) null,
  event_category character varying(50) null,
  constraint analytics_pkey primary key (id),
  constraint analytics_lead_id_fkey foreign KEY (lead_id) references leads (id) on delete CASCADE,
  constraint analytics_event_category_check check (
    (
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
  )
) TABLESPACE pg_default;

create index IF not exists idx_analytics_lead on public.analytics using btree (lead_id) TABLESPACE pg_default;

create index IF not exists idx_analytics_event on public.analytics using btree (event_type) TABLESPACE pg_default;

create index IF not exists idx_analytics_created on public.analytics using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists idx_analytics_session on public.analytics using btree (session_id) TABLESPACE pg_default;

create index IF not exists idx_analytics_created_brin on public.analytics using brin (created_at) TABLESPACE pg_default;

create index IF not exists idx_analytics_phone on public.analytics using btree (phone_number) TABLESPACE pg_default;

create index IF not exists idx_analytics_event_category on public.analytics using btree (event_category) TABLESPACE pg_default;