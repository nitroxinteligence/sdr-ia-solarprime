create table public.messages (
  id uuid not null default extensions.uuid_generate_v4 (),
  conversation_id uuid null,
  whatsapp_message_id character varying(100) null,
  role character varying(20) not null,
  content text not null,
  media_type character varying(20) null,
  media_url text null,
  media_data jsonb null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  message_type character varying(20) null default 'text'::character varying,
  sender character varying(20) null,
  is_read boolean null default false,
  constraint messages_pkey primary key (id),
  constraint messages_conversation_id_fkey foreign KEY (conversation_id) references conversations (id) on delete CASCADE,
  constraint messages_media_type_check check (
    (
      (media_type)::text = any (
        (
          array[
            'image'::character varying,
            'audio'::character varying,
            'video'::character varying,
            'document'::character varying,
            'buffered'::character varying,
            'text'::character varying
          ]
        )::text[]
      )
    )
  ),
  constraint messages_role_check check (
    (
      (role)::text = any (
        (
          array[
            'user'::character varying,
            'assistant'::character varying,
            'system'::character varying
          ]
        )::text[]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_messages_conversation on public.messages using btree (conversation_id) TABLESPACE pg_default;

create index IF not exists idx_messages_role on public.messages using btree (role) TABLESPACE pg_default;

create index IF not exists idx_messages_created on public.messages using btree (created_at) TABLESPACE pg_default;

create index IF not exists idx_messages_whatsapp_id on public.messages using btree (whatsapp_message_id) TABLESPACE pg_default;

create index IF not exists idx_messages_created_brin on public.messages using brin (created_at) TABLESPACE pg_default;