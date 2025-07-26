-- =====================================================
-- Script para corrigir o campo phone_number
-- considerando as views dependentes
-- =====================================================

-- 1. Primeiro, remover a view que depende da coluna
DROP VIEW IF EXISTS v_leads_with_last_conversation CASCADE;

-- 2. Alterar o tipo da coluna phone_number
ALTER TABLE leads 
ALTER COLUMN phone_number TYPE VARCHAR(20);

-- 3. Recriar a view
CREATE OR REPLACE VIEW v_leads_with_last_conversation AS
SELECT 
    l.*,
    c.id as last_conversation_id,
    c.started_at as last_conversation_at,
    c.total_messages,
    c.sentiment
FROM leads l
LEFT JOIN LATERAL (
    SELECT * FROM conversations
    WHERE lead_id = l.id
    ORDER BY started_at DESC
    LIMIT 1
) c ON true;

-- 4. Verificar se funcionou
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'leads' 
AND column_name = 'phone_number';

-- Resultado esperado: phone_number | character varying | 20