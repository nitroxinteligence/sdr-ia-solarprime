create table public.follow_ups (
  id uuid not null default gen_random_uuid(),
  lead_id uuid null,
  phone_number character varying(50) not null,
  follow_up_type character varying(50) not null,
  scheduled_at timestamp with time zone not null,
  executed_at timestamp with time zone null,
  status character varying(20) null default 'PENDING'::character varying,
  message_template character varying(100) null,
  custom_message text null,
  priority character varying(20) null default 'MEDIUM'::character varying,
  attempts integer null default 0,
  max_attempts integer null default 3,
  last_attempt_at timestamp with time zone null,
  next_attempt_at timestamp with time zone null,
  metadata jsonb null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint follow_ups_pkey primary key (id),
  constraint follow_ups_lead_id_fkey foreign key (lead_id) references leads (id) on delete CASCADE,
  constraint follow_ups_status_check check (
    (status)::text = any (
      (
        array[
          'PENDING'::character varying,
          'EXECUTING'::character varying,
          'COMPLETED'::character varying,
          'FAILED'::character varying,
          'CANCELLED'::character varying
        ]
      )::text[]
    )
  ),
  constraint follow_ups_follow_up_type_check check (
    (follow_up_type)::text = any (
      (
        array[
          'IMMEDIATE_REENGAGEMENT'::character varying,
          'DAILY_NURTURING'::character varying,
          'MEETING_CONFIRMATION'::character varying,
          'MEETING_REMINDER'::character varying,
          'ABANDONMENT_CHECK'::character varying,
          'CUSTOM'::character varying
        ]
      )::text[]
    )
  ),
  constraint follow_ups_priority_check check (
    (priority)::text = any (
      (
        array[
          'LOW'::character varying,
          'MEDIUM'::character varying,
          'HIGH'::character varying,
          'URGENT'::character varying
        ]
      )::text[]
    )
  )
) TABLESPACE pg_default;

-- Índices para otimizar consultas
create index IF not exists idx_follow_ups_lead_id on public.follow_ups using btree (lead_id) TABLESPACE pg_default;

create index IF not exists idx_follow_ups_phone on public.follow_ups using btree (phone_number) TABLESPACE pg_default;

create index IF not exists idx_follow_ups_status on public.follow_ups using btree (status) TABLESPACE pg_default;

create index IF not exists idx_follow_ups_scheduled on public.follow_ups using btree (scheduled_at) TABLESPACE pg_default;

create index IF not exists idx_follow_ups_type on public.follow_ups using btree (follow_up_type) TABLESPACE pg_default;

create index IF not exists idx_follow_ups_priority on public.follow_ups using btree (priority) TABLESPACE pg_default;

-- Índice composto para consultas de follow-ups pendentes
create index IF not exists idx_follow_ups_pending on public.follow_ups using btree (
  status,
  scheduled_at,
  priority desc
) TABLESPACE pg_default
where
  ((status)::text = 'PENDING'::text);

-- Trigger para atualizar updated_at automaticamente
create trigger update_follow_ups_updated_at BEFORE
update on follow_ups for EACH row
execute FUNCTION update_updated_at_column();