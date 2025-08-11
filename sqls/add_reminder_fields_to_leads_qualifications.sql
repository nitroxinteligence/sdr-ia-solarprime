-- Adicionar campos de controle de lembretes na tabela leads_qualifications
-- Estes campos serão usados para rastrear se os lembretes já foram enviados

ALTER TABLE leads_qualifications 
ADD COLUMN IF NOT EXISTS reminder_24h_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS reminder_24h_sent_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS reminder_2h_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS reminder_2h_sent_at TIMESTAMP;

-- Comentários explicativos
COMMENT ON COLUMN leads_qualifications.reminder_24h_sent IS 'Indica se o lembrete de 24h antes da reunião foi enviado';
COMMENT ON COLUMN leads_qualifications.reminder_24h_sent_at IS 'Data/hora em que o lembrete de 24h foi enviado';
COMMENT ON COLUMN leads_qualifications.reminder_2h_sent IS 'Indica se o lembrete de 2h antes da reunião foi enviado';
COMMENT ON COLUMN leads_qualifications.reminder_2h_sent_at IS 'Data/hora em que o lembrete de 2h foi enviado';