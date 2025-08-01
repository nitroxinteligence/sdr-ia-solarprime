-- Criar tabela agent_sessions para armazenar estado do agente AGnO
CREATE TABLE IF NOT EXISTS agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    state JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_agent_sessions_session_id ON agent_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_phone_number ON agent_sessions(phone_number);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_last_interaction ON agent_sessions(last_interaction);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_agent_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.last_interaction = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER agent_sessions_updated_at_trigger
    BEFORE UPDATE ON agent_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_sessions_updated_at();

-- Comentários para documentação
COMMENT ON TABLE agent_sessions IS 'Armazena o estado das sessões do agente AGnO por telefone';
COMMENT ON COLUMN agent_sessions.session_id IS 'ID único da sessão do agente';
COMMENT ON COLUMN agent_sessions.phone_number IS 'Número de telefone do WhatsApp associado à sessão';
COMMENT ON COLUMN agent_sessions.state IS 'Estado atual da conversa em formato JSON';
COMMENT ON COLUMN agent_sessions.last_interaction IS 'Timestamp da última interação com o agente';