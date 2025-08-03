-- Tabela para armazenar eventos do calendário
-- Sincronizada com Google Calendar

CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Relacionamento com lead
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    
    -- Informações do evento
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Datas e horários
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    
    -- Localização
    location TEXT,
    meeting_link TEXT, -- Link do Google Meet ou similar
    
    -- IDs de sincronização
    google_event_id VARCHAR(255) UNIQUE, -- ID do evento no Google Calendar
    google_calendar_id VARCHAR(255), -- ID do calendário usado
    
    -- Status e tipo
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, confirmed, cancelled, completed
    event_type VARCHAR(50) DEFAULT 'meeting', -- meeting, follow_up, reminder
    
    -- Dados de participantes
    attendees JSONB DEFAULT '[]'::jsonb, -- Lista de participantes
    organizer_email VARCHAR(255),
    
    -- Configurações de lembrete
    reminder_minutes INTEGER DEFAULT 30, -- Minutos antes para lembrete
    reminder_sent BOOLEAN DEFAULT FALSE,
    
    -- Metadados
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    cancelled_at TIMESTAMPTZ,
    
    -- Índices para performance
    INDEX idx_calendar_events_lead_id (lead_id),
    INDEX idx_calendar_events_start_time (start_time),
    INDEX idx_calendar_events_status (status),
    INDEX idx_calendar_events_google_event_id (google_event_id)
);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_calendar_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calendar_events_updated_at
    BEFORE UPDATE ON calendar_events
    FOR EACH ROW
    EXECUTE FUNCTION update_calendar_events_updated_at();

-- Comentários para documentação
COMMENT ON TABLE calendar_events IS 'Eventos de calendário sincronizados com Google Calendar';
COMMENT ON COLUMN calendar_events.lead_id IS 'ID do lead associado ao evento';
COMMENT ON COLUMN calendar_events.google_event_id IS 'ID único do evento no Google Calendar';
COMMENT ON COLUMN calendar_events.status IS 'Status do evento: scheduled, confirmed, cancelled, completed';
COMMENT ON COLUMN calendar_events.attendees IS 'Array JSON com informações dos participantes';
COMMENT ON COLUMN calendar_events.metadata IS 'Dados adicionais do evento em formato JSON';

-- Função para buscar próximos eventos
CREATE OR REPLACE FUNCTION get_upcoming_events(
    p_lead_id UUID DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    lead_id UUID,
    title VARCHAR,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    status VARCHAR,
    meeting_link TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id,
        ce.lead_id,
        ce.title,
        ce.start_time,
        ce.end_time,
        ce.status,
        ce.meeting_link
    FROM calendar_events ce
    WHERE 
        ce.start_time > NOW()
        AND ce.status IN ('scheduled', 'confirmed')
        AND (p_lead_id IS NULL OR ce.lead_id = p_lead_id)
    ORDER BY ce.start_time ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Função para buscar eventos que precisam de lembrete
CREATE OR REPLACE FUNCTION get_events_needing_reminder()
RETURNS TABLE (
    id UUID,
    lead_id UUID,
    title VARCHAR,
    start_time TIMESTAMPTZ,
    reminder_minutes INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id,
        ce.lead_id,
        ce.title,
        ce.start_time,
        ce.reminder_minutes
    FROM calendar_events ce
    WHERE 
        ce.status IN ('scheduled', 'confirmed')
        AND ce.reminder_sent = FALSE
        AND ce.start_time - INTERVAL '1 minute' * ce.reminder_minutes <= NOW()
        AND ce.start_time > NOW();
END;
$$ LANGUAGE plpgsql;