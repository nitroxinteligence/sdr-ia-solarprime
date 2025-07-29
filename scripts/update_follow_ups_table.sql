-- =====================================================
-- Atualizar tabela follow_ups para sistema de follow-up automático
-- =====================================================

-- Remover a constraint antiga do tipo
ALTER TABLE follow_ups DROP CONSTRAINT IF EXISTS follow_ups_type_check;

-- Adicionar nova constraint com os tipos usados pelo sistema
ALTER TABLE follow_ups ADD CONSTRAINT follow_ups_type_check 
CHECK (type IN (
    'first_contact',    -- Primeiro follow-up após 30 minutos
    'reminder',         -- Segundo follow-up após 24 horas
    'reengagement',     -- Reengajamento após 48-72 horas
    'final',            -- Follow-up final
    'qualification',    -- Follow-up de qualificação
    'scheduling',       -- Follow-up para agendamento
    'check_in',         -- Check-in geral
    'nurture'          -- Nutrição de lead
));

-- Tornar o campo message opcional (será gerado automaticamente)
ALTER TABLE follow_ups ALTER COLUMN message DROP NOT NULL;

-- Adicionar campo metadata para armazenar contexto adicional
ALTER TABLE follow_ups ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Criar índice para buscar follow-ups pendentes eficientemente
CREATE INDEX IF NOT EXISTS idx_followups_pending_scheduled 
ON follow_ups(status, scheduled_at) 
WHERE status = 'pending';

-- Comentários para documentação
COMMENT ON COLUMN follow_ups.type IS 'Tipo de follow-up: first_contact (30min), reminder (24h), reengagement (48-72h), etc.';
COMMENT ON COLUMN follow_ups.metadata IS 'Metadados adicionais: phone, stage, last_message, etc.';
COMMENT ON COLUMN follow_ups.message IS 'Mensagem de follow-up (opcional - pode ser gerada automaticamente)';

-- Garantir que RLS está desabilitado para testes
ALTER TABLE follow_ups DISABLE ROW LEVEL SECURITY;