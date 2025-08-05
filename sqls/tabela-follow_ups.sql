create table public.follow_ups (
  id uuid not null default extensions.uuid_generate_v4 (),
  lead_id uuid null,
  scheduled_at timestamp with time zone not null,
  type character varying(50) not null,
  message text not null,
  status character varying(20) null default 'pending'::character varying,
  executed_at timestamp with time zone null,
  result jsonb null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  metadata jsonb null,
  follow_up_type character varying(50) not null default 'CUSTOM'::character varying,
  custom_message text null,
  message_template character varying(100) null,
  priority text null default 'medium'::text,
  attempt integer null default 0,
  last_attempt_at timestamp with time zone null,
  next_retry_at timestamp with time zone null,
  error_reason text null,
  response jsonb null,
  constraint follow_ups_pkey primary key (id),
  constraint follow_ups_lead_id_fkey foreign KEY (lead_id) references leads (id) on delete CASCADE,
  constraint follow_ups_follow_up_type_check check (
    (
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
    )
  ),
  constraint follow_ups_status_check check (
    (
      (status)::text = any (
        (
          array[
            'pending'::character varying,
            'executed'::character varying,
            'failed'::character varying,
            'cancelled'::character varying
          ]
        )::text[]
      )
    )
  ),
  constraint follow_ups_type_check check (
    (
      (type)::text = any (
        (
          array[
            'reminder'::character varying,
            'check_in'::character varying,
            'reengagement'::character varying,
            'nurture'::character varying
          ]
        )::text[]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_followups_lead on public.follow_ups using btree (lead_id) TABLESPACE pg_default;

create index IF not exists idx_followups_scheduled on public.follow_ups using btree (scheduled_at) TABLESPACE pg_default;

create index IF not exists idx_followups_status on public.follow_ups using btree (status) TABLESPACE pg_default;

create index IF not exists idx_followups_type on public.follow_ups using btree (type) TABLESPACE pg_default;

create index IF not exists idx_followups_pending on public.follow_ups using btree (scheduled_at, status) TABLESPACE pg_default
where
  ((status)::text = 'PENDING'::text);

create index IF not exists idx_follow_ups_pending on public.follow_ups using btree (status, scheduled_at) TABLESPACE pg_default
where
  ((status)::text = 'pending'::text);

create index IF not exists idx_follow_ups_lead on public.follow_ups using btree (lead_id, status) TABLESPACE pg_default;

create trigger update_followups_updated_at BEFORE
update on follow_ups for EACH row
execute FUNCTION update_updated_at_column ();