-- ============================================================
-- SQL DE CORREÇÃO PARA TABELAS DO SUPABASE
-- SDR IA SolarPrime v0.2
-- ============================================================

-- Função helper para atualizar updated_at (se não existir)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 1. CORRIGIR TABELA CONVERSATIONS
-- ============================================================

-- Verificar se a coluna phone_number existe, se não, adicionar
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'conversations' 
    AND column_name = 'phone_number'
  ) THEN
    ALTER TABLE conversations 
    ADD COLUMN phone_number VARCHAR(50);
    
    -- Criar índice para phone_number
    CREATE INDEX IF NOT EXISTS idx_conversations_phone 
    ON conversations(phone_number);
  END IF;
END $$;

-- Verificar se a coluna channel existe, se não, adicionar
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'conversations' 
    AND column_name = 'channel'
  ) THEN
    ALTER TABLE conversations 
    ADD COLUMN channel VARCHAR(50) DEFAULT 'whatsapp';
  END IF;
END $$;

-- Adicionar constraint para channel se não existir
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.constraint_column_usage 
    WHERE table_name = 'conversations' 
    AND constraint_name = 'conversations_channel_check'
  ) THEN
    ALTER TABLE conversations 
    ADD CONSTRAINT conversations_channel_check 
    CHECK (channel IN ('whatsapp', 'email', 'sms', 'webchat'));
  END IF;
END $$;

-- Adicionar metadata se não existir
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'conversations' 
    AND column_name = 'metadata'
  ) THEN
    ALTER TABLE conversations 
    ADD COLUMN metadata JSONB;
  END IF;
END $$;

-- Adicionar status se não existir
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'conversations' 
    AND column_name = 'status'
  ) THEN
    ALTER TABLE conversations 
    ADD COLUMN status VARCHAR(20) DEFAULT 'ACTIVE';
    
    -- Adicionar constraint para status
    ALTER TABLE conversations 
    ADD CONSTRAINT conversations_status_check 
    CHECK (status IN ('ACTIVE', 'PAUSED', 'COMPLETED', 'ARCHIVED'));
  END IF;
END $$;

-- ============================================================
-- 2. CORRIGIR TABELA FOLLOW_UPS
-- ============================================================

-- Verificar se follow_up_type existe, se não, adicionar
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'follow_ups' 
    AND column_name = 'follow_up_type'
  ) THEN
    ALTER TABLE follow_ups 
    ADD COLUMN follow_up_type VARCHAR(50) NOT NULL DEFAULT 'CUSTOM';
  END IF;
END $$;

-- Adicionar constraint para follow_up_type se não existir
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.constraint_column_usage 
    WHERE table_name = 'follow_ups' 
    AND constraint_name = 'follow_ups_follow_up_type_check'
  ) THEN
    ALTER TABLE follow_ups 
    ADD CONSTRAINT follow_ups_follow_up_type_check 
    CHECK (follow_up_type IN (
      'IMMEDIATE_REENGAGEMENT',
      'DAILY_NURTURING',
      'MEETING_CONFIRMATION',
      'MEETING_REMINDER',
      'ABANDONMENT_CHECK',
      'CUSTOM'
    ));
  END IF;
END $$;

-- Verificar se custom_message existe, se não, adicionar
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'follow_ups' 
    AND column_name = 'custom_message'
  ) THEN
    ALTER TABLE follow_ups 
    ADD COLUMN custom_message TEXT;
  END IF;
END $$;

-- Verificar se message_template existe, se não, adicionar
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'follow_ups' 
    AND column_name = 'message_template'
  ) THEN
    ALTER TABLE follow_ups 
    ADD COLUMN message_template VARCHAR(100);
  END IF;
END $$;

-- ============================================================
-- 3. CORRIGIR TABELA ANALYTICS
-- ============================================================

-- Verificar se phone_number existe, se não, adicionar
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'analytics' 
    AND column_name = 'phone_number'
  ) THEN
    ALTER TABLE analytics 
    ADD COLUMN phone_number VARCHAR(50);
    
    -- Criar índice para phone_number
    CREATE INDEX IF NOT EXISTS idx_analytics_phone 
    ON analytics(phone_number);
  END IF;
END $$;

-- Verificar se event_category existe, se não, adicionar
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'analytics' 
    AND column_name = 'event_category'
  ) THEN
    ALTER TABLE analytics 
    ADD COLUMN event_category VARCHAR(50);
    
    -- Criar índice para event_category
    CREATE INDEX IF NOT EXISTS idx_analytics_event_category 
    ON analytics(event_category);
  END IF;
END $$;

-- Adicionar constraint para event_category se não existir
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.constraint_column_usage 
    WHERE table_name = 'analytics' 
    AND constraint_name = 'analytics_event_category_check'
  ) THEN
    ALTER TABLE analytics 
    ADD CONSTRAINT analytics_event_category_check 
    CHECK (event_category IN (
      'CONVERSATION',
      'QUALIFICATION',
      'MEETING',
      'FOLLOW_UP',
      'MEDIA',
      'SYSTEM',
      'USER_ACTION'
    ));
  END IF;
END $$;

-- ============================================================
-- 4. CRIAR TABELA LEADS_QUALIFICATIONS (se não existir)
-- ============================================================

-- Criar tabela leads_qualifications se não existir
CREATE TABLE IF NOT EXISTS leads_qualifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  qualification_status VARCHAR(20) DEFAULT 'PENDING',
  score INTEGER CHECK (score >= 0 AND score <= 100),
  criteria JSONB,
  notes TEXT,
  qualified_by UUID,
  qualified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT leads_qualifications_status_check 
  CHECK (qualification_status IN ('PENDING', 'QUALIFIED', 'NOT_QUALIFIED', 'IN_REVIEW'))
);

-- Criar índices para leads_qualifications
CREATE INDEX IF NOT EXISTS idx_leads_qualifications_lead_id 
ON leads_qualifications(lead_id);

CREATE INDEX IF NOT EXISTS idx_leads_qualifications_status 
ON leads_qualifications(qualification_status);

CREATE INDEX IF NOT EXISTS idx_leads_qualifications_score 
ON leads_qualifications(score);

-- Trigger para updated_at (apenas se não existir)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger 
    WHERE tgname = 'update_leads_qualifications_updated_at'
  ) THEN
    CREATE TRIGGER update_leads_qualifications_updated_at
      BEFORE UPDATE ON leads_qualifications
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  END IF;
END $$;

-- ============================================================
-- 5. ADICIONAR COLUNAS FALTANTES EM MESSAGES (se necessário)
-- ============================================================

-- Adicionar message_type se não existir (para compatibilidade)
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'messages' 
    AND column_name = 'message_type'
  ) THEN
    ALTER TABLE messages 
    ADD COLUMN message_type VARCHAR(20) DEFAULT 'text';
  END IF;
END $$;

-- Adicionar sender se não existir (para compatibilidade)
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'messages' 
    AND column_name = 'sender'
  ) THEN
    ALTER TABLE messages 
    ADD COLUMN sender VARCHAR(20);
  END IF;
END $$;

-- Adicionar is_read se não existir
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'messages' 
    AND column_name = 'is_read'
  ) THEN
    ALTER TABLE messages 
    ADD COLUMN is_read BOOLEAN DEFAULT FALSE;
  END IF;
END $$;

-- ============================================================
-- 6. HABILITAR ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Habilitar RLS em todas as tabelas principais
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads_qualifications ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- 7. CRIAR POLÍTICAS RLS BÁSICAS (DESENVOLVIMENTO)
-- ============================================================

-- Para desenvolvimento, permitir acesso total via service key
-- NOTA: Em produção, criar políticas mais restritivas

-- Política para leads (criar apenas se não existir)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'leads' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON leads
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL; -- Ignorar se já existir
END $$;

-- Política para conversations
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'conversations' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON conversations
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Política para messages
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'messages' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON messages
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Política para follow_ups
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'follow_ups' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON follow_ups
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Política para analytics
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'analytics' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON analytics
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Política para agent_sessions
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'agent_sessions' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON agent_sessions
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Política para knowledge_base
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'knowledge_base' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON knowledge_base
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Política para embeddings
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'embeddings' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON embeddings
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Política para profiles
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'profiles' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON profiles
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Política para leads_qualifications
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'leads_qualifications' 
    AND policyname = 'Acesso total para service key'
  ) THEN
    CREATE POLICY "Acesso total para service key" ON leads_qualifications
      FOR ALL USING (true);
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- ============================================================
-- 8. OTIMIZAÇÕES DE PERFORMANCE
-- ============================================================

-- Criar índices BRIN para colunas de timestamp (mais eficientes)
CREATE INDEX IF NOT EXISTS idx_leads_created_brin 
ON leads USING BRIN (created_at);

CREATE INDEX IF NOT EXISTS idx_messages_created_brin 
ON messages USING BRIN (created_at);

CREATE INDEX IF NOT EXISTS idx_analytics_created_brin 
ON analytics USING BRIN (created_at);

CREATE INDEX IF NOT EXISTS idx_conversations_created_brin 
ON conversations USING BRIN (created_at);

-- Índices compostos para queries frequentes
CREATE INDEX IF NOT EXISTS idx_leads_status_qualified 
ON leads(qualification_status, qualification_score) 
WHERE qualification_status = 'QUALIFIED';

CREATE INDEX IF NOT EXISTS idx_followups_pending 
ON follow_ups(scheduled_at, status) 
WHERE status = 'PENDING';

-- Criar índice para conversações ativas (apenas se a coluna status existir)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'conversations' 
    AND column_name = 'status'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_conversations_active 
    ON conversations(lead_id, status) 
    WHERE status = 'ACTIVE';
  ELSE
    -- Se não existir status, criar índice apenas em lead_id
    CREATE INDEX IF NOT EXISTS idx_conversations_lead 
    ON conversations(lead_id);
  END IF;
END $$;

-- ============================================================
-- 9. FUNÇÕES AUXILIARES PARA O AGENTE SDR
-- ============================================================

-- Função para obter contexto completo de um lead
CREATE OR REPLACE FUNCTION get_lead_context(p_lead_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY INVOKER
AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'lead', row_to_json(l.*),
    'conversations', (
      SELECT json_agg(row_to_json(c.*))
      FROM conversations c
      WHERE c.lead_id = p_lead_id
    ),
    'recent_messages', (
      SELECT json_agg(row_to_json(m.*))
      FROM messages m
      JOIN conversations c ON m.conversation_id = c.id
      WHERE c.lead_id = p_lead_id
      ORDER BY m.created_at DESC
      LIMIT 10
    ),
    'follow_ups', (
      SELECT json_agg(row_to_json(f.*))
      FROM follow_ups f
      WHERE f.lead_id = p_lead_id
      AND f.status = 'PENDING'
    )
  ) INTO result
  FROM leads l
  WHERE l.id = p_lead_id;
  
  RETURN result;
END;
$$;

-- Função para calcular score de qualificação
CREATE OR REPLACE FUNCTION calculate_qualification_score(p_lead_id UUID)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY INVOKER
AS $$
DECLARE
  score INTEGER := 0;
  lead_data RECORD;
BEGIN
  SELECT * INTO lead_data FROM leads WHERE id = p_lead_id;
  
  -- Critérios de pontuação
  IF lead_data.bill_value > 300 THEN
    score := score + 20;
  END IF;
  
  IF lead_data.is_decision_maker = true THEN
    score := score + 30;
  END IF;
  
  IF lead_data.interested = true THEN
    score := score + 25;
  END IF;
  
  IF lead_data.property_type IN ('casa', 'comercial') THEN
    score := score + 15;
  END IF;
  
  IF lead_data.consumption_kwh > 250 THEN
    score := score + 10;
  END IF;
  
  RETURN LEAST(score, 100); -- Máximo 100
END;
$$;

-- ============================================================
-- 10. HABILITAR REALTIME PARA TABELAS CRÍTICAS
-- ============================================================

-- Habilitar realtime nas tabelas principais (apenas se não estiverem)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' 
    AND tablename = 'messages'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE messages;
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL; -- Ignorar se já existir
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' 
    AND tablename = 'conversations'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE conversations;
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' 
    AND tablename = 'follow_ups'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE follow_ups;
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' 
    AND tablename = 'analytics'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE analytics;
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Configurar replica identity para realtime
ALTER TABLE messages REPLICA IDENTITY FULL;
ALTER TABLE conversations REPLICA IDENTITY FULL;
ALTER TABLE follow_ups REPLICA IDENTITY FULL;
ALTER TABLE analytics REPLICA IDENTITY FULL;

-- ============================================================
-- VERIFICAÇÃO FINAL
-- ============================================================

-- Atualizar estatísticas para o query planner
ANALYZE leads;
ANALYZE conversations;
ANALYZE messages;
ANALYZE follow_ups;
ANALYZE analytics;
ANALYZE leads_qualifications;

-- Mensagem de conclusão
DO $$
BEGIN
  RAISE NOTICE 'Correções aplicadas com sucesso!';
  RAISE NOTICE 'Tabelas corrigidas: conversations, follow_ups, analytics';
  RAISE NOTICE 'Tabela criada: leads_qualifications';
  RAISE NOTICE 'RLS habilitado em todas as tabelas';
  RAISE NOTICE 'Índices otimizados criados';
  RAISE NOTICE 'Realtime habilitado para tabelas críticas';
END $$;