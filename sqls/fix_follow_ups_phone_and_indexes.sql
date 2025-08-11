-- Correções URGENTES P0 para tabela follow_ups
-- Data: 08/08/2025
-- Objetivo: Adicionar coluna phone_number e corrigir índices conflitantes

-- 1. Adicionar coluna phone_number que o código espera
ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(50);

-- 2. Corrigir índices conflitantes
-- Primeiro, remover os índices problemáticos
DROP INDEX IF EXISTS idx_followups_pending;
DROP INDEX IF EXISTS idx_follow_ups_pending;

-- 3. Criar índice único e correto (usando minúsculas para corresponder ao check constraint)
CREATE INDEX idx_followups_pending 
ON follow_ups (scheduled_at, status) 
WHERE status = 'pending';

-- 4. Mensagem de conclusão
DO $$
BEGIN
    RAISE NOTICE '✅ Correções P0 aplicadas com sucesso!';
    RAISE NOTICE '📱 Coluna phone_number adicionada';
    RAISE NOTICE '🔍 Índices conflitantes corrigidos';
    RAISE NOTICE '✨ Tabela follow_ups pronta para produção';
END $$;