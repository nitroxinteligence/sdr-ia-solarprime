create table public.leads_qualifications (
  id uuid not null default gen_random_uuid (),
  lead_id uuid null,
  qualification_status character varying(20) null default 'PENDING'::character varying,
  score integer null,
  criteria jsonb null,
  notes text null,
  qualified_by uuid null,
  qualified_at timestamp with time zone null,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  google_event_id character varying(255) null,
  reminder_24h_sent boolean null default false,
  reminder_24h_sent_at timestamp without time zone null,
  reminder_2h_sent boolean null default false,
  reminder_2h_sent_at timestamp without time zone null,
  constraint leads_qualifications_pkey primary key (id),
  constraint leads_qualifications_lead_id_fkey foreign KEY (lead_id) references leads (id) on delete CASCADE,
  constraint leads_qualifications_score_check check (
    (
      (score >= 0)
      and (score <= 100)
    )
  ),
  constraint leads_qualifications_status_check check (
    (
      (qualification_status)::text = any (
        (
          array[
            'PENDING'::character varying,
            'QUALIFIED'::character varying,
            'NOT_QUALIFIED'::character varying,
            'IN_REVIEW'::character varying
          ]
        )::text[]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_leads_qualifications_google_event_id on public.leads_qualifications using btree (google_event_id) TABLESPACE pg_default;

create index IF not exists idx_leads_qualifications_lead_id on public.leads_qualifications using btree (lead_id) TABLESPACE pg_default;

create index IF not exists idx_leads_qualifications_status on public.leads_qualifications using btree (qualification_status) TABLESPACE pg_default;

create index IF not exists idx_leads_qualifications_score on public.leads_qualifications using btree (score) TABLESPACE pg_default;

create trigger update_leads_qualifications_updated_at BEFORE
update on leads_qualifications for EACH row
execute FUNCTION update_updated_at_column ();