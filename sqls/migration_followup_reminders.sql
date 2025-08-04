-- Migration: Adicionar campos para lembretes de reunião (24h e 2h)
-- Data: 04/08/2025

-- 1. Adicionar campos na tabela calendar_events para rastrear lembretes
ALTER TABLE calendar_events 
ADD COLUMN IF NOT EXISTS reminder_24h_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS reminder_24h_sent_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS reminder_2h_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS reminder_2h_sent_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS reminder_30min_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS reminder_30min_sent_at TIMESTAMP WITH TIME ZONE;

-- 2. Adicionar índices para performance
CREATE INDEX IF NOT EXISTS idx_calendar_events_reminders 
ON calendar_events (status, reminder_24h_sent, reminder_2h_sent, reminder_30min_sent);

CREATE INDEX IF NOT EXISTS idx_calendar_events_start_time 
ON calendar_events (start_time);

-- 3. Adicionar campo attempt na tabela follow_ups para rastrear tentativas
ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS attempt INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMP WITH TIME ZONE;

-- 4. Adicionar índices para follow_ups
CREATE INDEX IF NOT EXISTS idx_follow_ups_pending 
ON follow_ups (status, scheduled_at) 
WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_follow_ups_lead 
ON follow_ups (lead_id, status);

-- 5. Criar função para buscar eventos que precisam de lembrete 24h
CREATE OR REPLACE FUNCTION get_events_needing_24h_reminder()
RETURNS TABLE (
    id UUID,
    lead_id UUID,
    title TEXT,
    start_time TIMESTAMP WITH TIME ZONE,
    location TEXT,
    meeting_link TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id,
        ce.lead_id,
        ce.title,
        ce.start_time,
        ce.location,
        ce.meeting_link
    FROM calendar_events ce
    WHERE 
        ce.status = 'confirmed'
        AND ce.reminder_24h_sent = FALSE
        AND ce.start_time BETWEEN 
            NOW() + INTERVAL '23 hours 30 minutes' 
            AND NOW() + INTERVAL '24 hours 30 minutes';
END;
$$ LANGUAGE plpgsql;

-- 6. Criar função para buscar eventos que precisam de lembrete 2h
CREATE OR REPLACE FUNCTION get_events_needing_2h_reminder()
RETURNS TABLE (
    id UUID,
    lead_id UUID,
    title TEXT,
    start_time TIMESTAMP WITH TIME ZONE,
    location TEXT,
    meeting_link TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id,
        ce.lead_id,
        ce.title,
        ce.start_time,
        ce.location,
        ce.meeting_link
    FROM calendar_events ce
    WHERE 
        ce.status = 'confirmed'
        AND ce.reminder_2h_sent = FALSE
        AND ce.start_time BETWEEN 
            NOW() + INTERVAL '1 hour 30 minutes' 
            AND NOW() + INTERVAL '2 hours 30 minutes';
END;
$$ LANGUAGE plpgsql;

-- 7. Criar função para buscar follow-ups pendentes
CREATE OR REPLACE FUNCTION get_pending_followups()
RETURNS TABLE (
    id UUID,
    lead_id UUID,
    type follow_up_type,
    message TEXT,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    priority TEXT,
    attempt INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.lead_id,
        f.type,
        f.message,
        f.scheduled_at,
        f.priority,
        f.attempt
    FROM follow_ups f
    WHERE 
        f.status = 'pending'
        AND f.scheduled_at <= NOW()
    ORDER BY 
        f.priority DESC,
        f.scheduled_at ASC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- 8. Criar trigger para auto-agendar follow-ups
CREATE OR REPLACE FUNCTION auto_schedule_followup()
RETURNS TRIGGER AS $$
BEGIN
    -- Se lead não respondeu após 30 minutos, agendar reengajamento
    IF NEW.last_interaction_at < NOW() - INTERVAL '30 minutes' 
       AND NEW.qualification_stage != 'QUALIFIED'
       AND NOT EXISTS (
           SELECT 1 FROM follow_ups 
           WHERE lead_id = NEW.id 
           AND status = 'pending'
           AND type = 'IMMEDIATE_REENGAGEMENT'
       ) THEN
        
        INSERT INTO follow_ups (
            lead_id, 
            type, 
            scheduled_at, 
            status, 
            priority
        ) VALUES (
            NEW.id,
            'IMMEDIATE_REENGAGEMENT',
            NOW() + INTERVAL '30 minutes',
            'pending',
            'high'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 9. Aplicar trigger na tabela leads
DROP TRIGGER IF EXISTS trigger_auto_schedule_followup ON leads;
CREATE TRIGGER trigger_auto_schedule_followup
    AFTER UPDATE OF last_interaction_at ON leads
    FOR EACH ROW
    EXECUTE FUNCTION auto_schedule_followup();

-- 10. Adicionar comentários para documentação
COMMENT ON COLUMN calendar_events.reminder_24h_sent IS 'Indica se o lembrete de 24h foi enviado';
COMMENT ON COLUMN calendar_events.reminder_2h_sent IS 'Indica se o lembrete de 2h foi enviado';
COMMENT ON COLUMN calendar_events.reminder_30min_sent IS 'Indica se o lembrete de 30min foi enviado';
COMMENT ON COLUMN follow_ups.attempt IS 'Número de tentativas de envio deste follow-up';
COMMENT ON FUNCTION get_events_needing_24h_reminder() IS 'Retorna eventos que precisam de lembrete de 24h';
COMMENT ON FUNCTION get_events_needing_2h_reminder() IS 'Retorna eventos que precisam de lembrete de 2h';
COMMENT ON FUNCTION get_pending_followups() IS 'Retorna follow-ups pendentes ordenados por prioridade';