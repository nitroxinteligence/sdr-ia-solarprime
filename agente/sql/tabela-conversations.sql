create table public.conversations (
  id uuid not null default extensions.uuid_generate_v4 (),
  phone_number character varying(50) not null,
  lead_id uuid null,
  status character varying(20) null default 'ACTIVE'::character varying,
  total_messages integer null default 0,
  last_message_at timestamp with time zone null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint conversations_pkey primary key (id),
  constraint conversations_lead_id_fkey foreign KEY (lead_id) references leads (id) on delete CASCADE,
  constraint conversations_phone_number_key unique (phone_number),
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

-- Índices para otimizar consultas
create index IF not exists idx_conversations_phone on public.conversations using btree (phone_number) TABLESPACE pg_default;

create index IF not exists idx_conversations_lead_id on public.conversations using btree (lead_id) TABLESPACE pg_default;

create index IF not exists idx_conversations_status on public.conversations using btree (status) TABLESPACE pg_default;

create index IF not exists idx_conversations_created on public.conversations using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists idx_conversations_last_message on public.conversations using btree (last_message_at desc) TABLESPACE pg_default;

-- Índice composto para consultas ativas
create index IF not exists idx_conversations_active on public.conversations using btree (
  status,
  last_message_at desc
) TABLESPACE pg_default
where
  ((status)::text = 'ACTIVE'::text);

-- Trigger para atualizar updated_at automaticamente
create trigger update_conversations_updated_at BEFORE
update on conversations for EACH row
execute FUNCTION update_updated_at_column ();