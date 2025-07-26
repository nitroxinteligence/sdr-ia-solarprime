-- =====================================================
-- Script para corrigir o tamanho do campo phone_number
-- =====================================================

BEGIN;

-- IMPORTANTE: Este script remove views que dependem da coluna phone_number
-- Você precisará recriá-las depois no Supabase Dashboard

-- 1. Forçar remoção de TODAS as views que possam depender da tabela leads
DROP VIEW IF EXISTS v_leads_with_last_conversation CASCADE;
DROP VIEW IF EXISTS v_lead_statistics CASCADE;
DROP VIEW IF EXISTS v_leads CASCADE;
DROP VIEW IF EXISTS v_lead_details CASCADE;

-- 2. Alterar a coluna para acomodar IDs do WhatsApp (ex: 5511999999999@s.whatsapp.net)
ALTER TABLE leads 
ALTER COLUMN phone_number TYPE VARCHAR(50);

-- 3. Verificar alteração
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'leads' 
AND column_name = 'phone_number';

COMMIT;

-- NOTA: Após executar este script, recrie as views removidas no Supabase Dashboard