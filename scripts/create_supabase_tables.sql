-- =====================================================
-- SDR IA SolarPrime - Schema do Banco de Dados
-- =====================================================
-- Execute este script no Supabase SQL Editor
-- =====================================================

-- Habilitar UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABELA: leads
-- =====================================================
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    document VARCHAR(20), -- CPF/CNPJ
    property_type VARCHAR(20) CHECK (property_type IN ('casa', 'apartamento', 'comercial', 'rural')),
    address TEXT,
    bill_value DECIMAL(10,2),
    consumption_kwh INTEGER,
    current_stage VARCHAR(50) DEFAULT 'INITIAL_CONTACT',
    qualification_score INTEGER CHECK (qualification_score >= 0 AND qualification_score <= 100),
    interested BOOLEAN DEFAULT true,
    kommo_lead_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para leads
CREATE INDEX idx_leads_phone ON leads(phone_number);
CREATE INDEX idx_leads_stage ON leads(current_stage);
CREATE INDEX idx_leads_interested ON leads(interested);
CREATE INDEX idx_leads_created ON leads(created_at DESC);

-- =====================================================
-- TABELA: conversations
-- =====================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    total_messages INTEGER DEFAULT 0,
    current_stage VARCHAR(50),
    sentiment VARCHAR(20) DEFAULT 'neutro' CHECK (sentiment IN ('positivo', 'neutro', 'negativo')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para conversations
CREATE INDEX idx_conversations_lead ON conversations(lead_id);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_active ON conversations(is_active);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);

-- =====================================================
-- TABELA: messages
-- =====================================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    whatsapp_message_id VARCHAR(100),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    media_type VARCHAR(20) CHECK (media_type IN ('image', 'audio', 'video', 'document')),
    media_url TEXT,
    media_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para messages
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_messages_whatsapp_id ON messages(whatsapp_message_id);

-- =====================================================
-- TABELA: lead_qualifications
-- =====================================================
CREATE TABLE IF NOT EXISTS lead_qualifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    has_own_property BOOLEAN,
    decision_maker BOOLEAN,
    urgency_level VARCHAR(20) CHECK (urgency_level IN ('alta', 'media', 'baixa')),
    objections JSONB DEFAULT '[]'::jsonb,
    solutions_presented JSONB DEFAULT '[]'::jsonb,
    extracted_data JSONB DEFAULT '{}'::jsonb,
    qualification_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para lead_qualifications
CREATE INDEX idx_qualifications_lead ON lead_qualifications(lead_id);
CREATE INDEX idx_qualifications_date ON lead_qualifications(qualification_date DESC);

-- =====================================================
-- TABELA: follow_ups
-- =====================================================
CREATE TABLE IF NOT EXISTS follow_ups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('reminder', 'check_in', 'reengagement', 'nurture')),
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'executed', 'failed', 'cancelled')),
    executed_at TIMESTAMP WITH TIME ZONE,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para follow_ups
CREATE INDEX idx_followups_lead ON follow_ups(lead_id);
CREATE INDEX idx_followups_scheduled ON follow_ups(scheduled_at);
CREATE INDEX idx_followups_status ON follow_ups(status);
CREATE INDEX idx_followups_type ON follow_ups(type);

-- =====================================================
-- TABELA: analytics
-- =====================================================
CREATE TABLE IF NOT EXISTS analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,
    session_id VARCHAR(100),
    user_agent VARCHAR(255),
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para analytics
CREATE INDEX idx_analytics_lead ON analytics(lead_id);
CREATE INDEX idx_analytics_event ON analytics(event_type);
CREATE INDEX idx_analytics_created ON analytics(created_at DESC);
CREATE INDEX idx_analytics_session ON analytics(session_id);

-- =====================================================
-- FUNÇÕES E TRIGGERS
-- =====================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qualifications_updated_at BEFORE UPDATE ON lead_qualifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_followups_updated_at BEFORE UPDATE ON follow_ups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS ÚTEIS
-- =====================================================

-- View de leads com última conversa
CREATE OR REPLACE VIEW v_leads_with_last_conversation AS
SELECT 
    l.*,
    c.id as last_conversation_id,
    c.started_at as last_conversation_date,
    c.total_messages,
    c.sentiment as last_sentiment
FROM leads l
LEFT JOIN LATERAL (
    SELECT * FROM conversations 
    WHERE lead_id = l.id 
    ORDER BY created_at DESC 
    LIMIT 1
) c ON true;

-- View de estatísticas por lead
CREATE OR REPLACE VIEW v_lead_statistics AS
SELECT 
    l.id,
    l.phone_number,
    l.name,
    l.current_stage,
    l.qualification_score,
    COUNT(DISTINCT c.id) as total_conversations,
    COUNT(DISTINCT m.id) as total_messages,
    MAX(c.created_at) as last_contact
FROM leads l
LEFT JOIN conversations c ON c.lead_id = l.id
LEFT JOIN messages m ON m.conversation_id = c.id
GROUP BY l.id;

-- =====================================================
-- POLÍTICAS DE SEGURANÇA (RLS)
-- =====================================================

-- Habilitar RLS nas tabelas
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_qualifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- Política para service role (acesso total)
CREATE POLICY "Service role has full access to leads" ON leads
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to conversations" ON conversations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to messages" ON messages
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to qualifications" ON lead_qualifications
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to followups" ON follow_ups
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to analytics" ON analytics
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- DADOS INICIAIS (OPCIONAL)
-- =====================================================

-- Inserir lead de teste
/*
INSERT INTO leads (phone_number, name, current_stage) 
VALUES ('5511999999999', 'Lead Teste', 'INITIAL_CONTACT')
ON CONFLICT (phone_number) DO NOTHING;
*/

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================
-- Agora você pode usar o Supabase com todas as tabelas criadas!
-- Lembre-se de configurar as variáveis de ambiente:
-- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY