-- Adicionar coluna google_event_id na tabela leads_qualifications
-- Esta coluna será usada para associar o evento do Google Calendar com o lead qualificado

ALTER TABLE leads_qualifications 
ADD COLUMN IF NOT EXISTS google_event_id VARCHAR(255);

-- Criar índice para melhorar performance das buscas
CREATE INDEX IF NOT EXISTS idx_leads_qualifications_google_event_id 
ON leads_qualifications(google_event_id);

-- Comentário explicativo
COMMENT ON COLUMN leads_qualifications.google_event_id IS 'ID do evento no Google Calendar associado a este lead qualificado';