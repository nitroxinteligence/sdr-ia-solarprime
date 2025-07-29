-- Adicionar campos do Google Calendar na tabela leads
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS google_event_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS meeting_scheduled_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS meeting_type VARCHAR(50) DEFAULT 'initial_meeting',
ADD COLUMN IF NOT EXISTS meeting_status VARCHAR(50) DEFAULT 'scheduled';

-- Criar índice para busca rápida por event_id
CREATE INDEX IF NOT EXISTS idx_leads_google_event_id ON leads(google_event_id);

-- Criar índice para buscar reuniões por data
CREATE INDEX IF NOT EXISTS idx_leads_meeting_scheduled_at ON leads(meeting_scheduled_at);

-- Comentário nos campos
COMMENT ON COLUMN leads.google_event_id IS 'ID do evento no Google Calendar';
COMMENT ON COLUMN leads.meeting_scheduled_at IS 'Data/hora da reunião agendada';
COMMENT ON COLUMN leads.meeting_type IS 'Tipo de reunião: initial_meeting, follow_up_meeting, contract_signing';
COMMENT ON COLUMN leads.meeting_status IS 'Status da reunião: scheduled, completed, cancelled, no_show';