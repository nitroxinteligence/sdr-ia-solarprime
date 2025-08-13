-- Adicionar coluna phone_number se não existir
ALTER TABLE public.follow_ups 
ADD COLUMN IF NOT EXISTS phone_number character varying(50) null;

-- Criar índice para phone_number
CREATE INDEX IF NOT EXISTS idx_followups_phone_number 
ON public.follow_ups USING btree (phone_number) TABLESPACE pg_default;