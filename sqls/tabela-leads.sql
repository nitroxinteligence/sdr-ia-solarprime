create table public.leads (
  id uuid not null default extensions.uuid_generate_v4 (),
  phone_number character varying(50) not null,
  name character varying(100) null,
  email character varying(100) null,
  document character varying(20) null,
  property_type character varying(20) null,
  address text null,
  bill_value numeric(10, 2) null,
  consumption_kwh integer null,
  current_stage character varying(50) null default 'INITIAL_CONTACT'::character varying,
  qualification_score integer null,
  interested boolean null default true,
  kommo_lead_id character varying(50) null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  google_event_id character varying(255) null,
  meeting_scheduled_at timestamp with time zone null,
  meeting_type character varying(50) null default 'initial_meeting'::character varying,
  meeting_status character varying(50) null default 'scheduled'::character varying,
  qualification_status character varying(20) null default 'PENDING'::character varying,
  is_decision_maker boolean null,
  has_solar_system boolean null,
  wants_new_solar_system boolean null,
  has_active_contract boolean null,
  contract_end_date timestamp with time zone null,
  solution_interest character varying(100) null default null::character varying,
  is_qualified boolean GENERATED ALWAYS as (
    case
      when ((qualification_status)::text = 'QUALIFIED'::text) then true
      else false
    end
  ) STORED null,
  last_interaction timestamp with time zone null default now(),
  constraint leads_pkey primary key (id),
  constraint leads_phone_number_key unique (phone_number),
  constraint leads_property_type_check check (
    (
      (property_type)::text = any (
        (
          array[
            'casa'::character varying,
            'apartamento'::character varying,
            'comercial'::character varying,
            'rural'::character varying
          ]
        )::text[]
      )
    )
  ),
  constraint leads_qualification_score_check check (
    (
      (qualification_score >= 0)
      and (qualification_score <= 100)
    )
  ),
  constraint leads_qualification_status_check check (
    (
      (qualification_status)::text = any (
        (
          array[
            'PENDING'::character varying,
            'QUALIFIED'::character varying,
            'NOT_QUALIFIED'::character varying
          ]
        )::text[]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_leads_stage on public.leads using btree (current_stage) TABLESPACE pg_default;

create index IF not exists idx_leads_interested on public.leads using btree (interested) TABLESPACE pg_default;

create index IF not exists idx_leads_created on public.leads using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists idx_leads_phone on public.leads using btree (phone_number) TABLESPACE pg_default;

create index IF not exists idx_leads_google_event_id on public.leads using btree (google_event_id) TABLESPACE pg_default;

create index IF not exists idx_leads_meeting_scheduled_at on public.leads using btree (meeting_scheduled_at) TABLESPACE pg_default;

create index IF not exists idx_leads_qualification_status on public.leads using btree (qualification_status) TABLESPACE pg_default;

create index IF not exists idx_leads_qualified on public.leads using btree (
  qualification_status,
  bill_value,
  is_decision_maker
) TABLESPACE pg_default
where
  ((qualification_status)::text = 'QUALIFIED'::text);

create index IF not exists idx_leads_created_brin on public.leads using brin (created_at) TABLESPACE pg_default;

create index IF not exists idx_leads_status_qualified on public.leads using btree (qualification_status, qualification_score) TABLESPACE pg_default
where
  ((qualification_status)::text = 'QUALIFIED'::text);

create index IF not exists idx_leads_is_qualified on public.leads using btree (is_qualified) TABLESPACE pg_default
where
  (is_qualified = true);

create trigger update_leads_updated_at BEFORE
update on leads for EACH row
execute FUNCTION update_updated_at_column ();