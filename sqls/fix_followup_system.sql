-- Script de Correção para Sistema de Follow-up e Lembretes
-- Data: 04/08/2025

-- 1. Criar tabela calendar_events se não existir
CREATE TABLE IF NOT EXISTS public.calendar_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    google_event_id TEXT UNIQUE,
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location TEXT,
    meeting_link TEXT,
    status TEXT DEFAULT 'confirmed',
    attendees JSONB,
    metadata JSONB,
    
    -- Campos de lembretes
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_24h_sent BOOLEAN DEFAULT FALSE,
    reminder_24h_sent_at TIMESTAMP WITH TIME ZONE,
    reminder_2h_sent BOOLEAN DEFAULT FALSE,
    reminder_2h_sent_at TIMESTAMP WITH TIME ZONE,
    reminder_30min_sent BOOLEAN DEFAULT FALSE,
    reminder_30min_sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cancelled_at TIMESTAMP WITH TIME ZONE
);

-- 2. Adicionar índices para calendar_events
CREATE INDEX IF NOT EXISTS idx_calendar_events_lead ON calendar_events(lead_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_status ON calendar_events(status);
CREATE INDEX IF NOT EXISTS idx_calendar_events_start_time ON calendar_events(start_time);
CREATE INDEX IF NOT EXISTS idx_calendar_events_reminders ON calendar_events(reminder_24h_sent, reminder_2h_sent, reminder_30min_sent);

-- 3. Adicionar coluna priority em follow_ups se não existir
ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'medium';

-- 4. Adicionar outras colunas necessárias em follow_ups
ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS attempt INTEGER DEFAULT 0;

ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS error_reason TEXT;

ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS response JSONB;

-- 5. Criar índices para follow_ups
CREATE INDEX IF NOT EXISTS idx_follow_ups_pending 
ON follow_ups(status, scheduled_at) 
WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_follow_ups_lead 
ON follow_ups(lead_id, status);

-- 6. Adicionar permissões RLS (Row Level Security)
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;

-- 7. Criar políticas para service role
CREATE POLICY "Service role can do everything with calendar_events" 
ON calendar_events 
FOR ALL 
USING (true) 
WITH CHECK (true);

CREATE POLICY "Service role can do everything with follow_ups" 
ON follow_ups 
FOR ALL 
USING (true) 
WITH CHECK (true);

-- 8. Atualizar valores de enum se necessário
DO $$ 
BEGIN
    -- Adicionar novos tipos de follow-up se não existirem
    IF NOT EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'follow_up_type'
    ) THEN
        CREATE TYPE follow_up_type AS ENUM (
            'IMMEDIATE_REENGAGEMENT',
            'DAILY_NURTURING',
            'MEETING_CONFIRMATION',
            'MEETING_REMINDER',
            'ABANDONMENT_CHECK',
            'CUSTOM'
        );
    END IF;
END $$;

-- 9. Criar função helper para buscar eventos que precisam de lembrete
CREATE OR REPLACE FUNCTION get_events_needing_reminder(hours_before INTEGER)
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
        AND ce.start_time BETWEEN 
            NOW() + (hours_before || ' hours')::INTERVAL - INTERVAL '30 minutes'
            AND NOW() + (hours_before || ' hours')::INTERVAL + INTERVAL '30 minutes'
        AND (
            CASE hours_before
                WHEN 24 THEN ce.reminder_24h_sent = FALSE
                WHEN 2 THEN ce.reminder_2h_sent = FALSE
                ELSE ce.reminder_30min_sent = FALSE
            END
        );
END;
$$ LANGUAGE plpgsql;

-- 10. Mensagem de conclusão
DO $$
BEGIN
    RAISE NOTICE '✅ Script de correção executado com sucesso!';
    RAISE NOTICE '📊 Tabelas criadas/atualizadas: calendar_events, follow_ups';
    RAISE NOTICE '🔍 Índices criados para melhor performance';
    RAISE NOTICE '🔒 RLS habilitado com políticas para service role';
END $$;