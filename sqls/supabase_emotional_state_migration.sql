-- ================================================================================
-- MIGRAÇÃO SUPABASE: Adicionar coluna emotional_state na tabela conversations
-- ================================================================================
-- 
-- Contexto: O sistema SDR IA está tentando acessar uma coluna 'emotional_state'
-- que não existe na tabela 'conversations', causando erro SQL.
--
-- Esta migração resolve o erro:
-- "column conversations.emotional_state does not exist"
--

-- 1. Adicionar a coluna emotional_state com valores padrão
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS emotional_state TEXT DEFAULT 'ENTUSIASMADA';

-- 2. Criar índice para performance (opcional, mas recomendado)
CREATE INDEX IF NOT EXISTS idx_conversations_emotional_state 
ON conversations(emotional_state);

-- 3. Adicionar comentário explicativo na coluna
COMMENT ON COLUMN conversations.emotional_state IS 
'Estado emocional atual da conversa para humanização do agente (ENTUSIASMADA, CURIOSA, CONFIANTE, FOCADA, EMPOLGADA)';

-- 4. Atualizar todas as conversas existentes com o estado padrão (se necessário)
UPDATE conversations 
SET emotional_state = 'ENTUSIASMADA' 
WHERE emotional_state IS NULL;

-- ================================================================================
-- VALIDAÇÃO: Execute este SELECT para verificar se funcionou
-- ================================================================================
-- 
-- SELECT id, emotional_state 
-- FROM conversations 
-- LIMIT 5;
--
-- Resultado esperado: Deve mostrar as conversas com emotional_state = 'ENTUSIASMADA'
--

-- ================================================================================
-- ESTADOS VÁLIDOS: 
-- ================================================================================
-- Os valores válidos para emotional_state são definidos no enum EmotionalState:
-- - ENTUSIASMADA (padrão)
-- - CURIOSA
-- - CONFIANTE  
-- - FOCADA
-- - EMPOLGADA
--
-- O sistema pode ser expandido futuramente com constraint check:
-- 
-- ALTER TABLE conversations 
-- ADD CONSTRAINT check_emotional_state 
-- CHECK (emotional_state IN ('ENTUSIASMADA', 'CURIOSA', 'CONFIANTE', 'FOCADA', 'EMPOLGADA'));
--