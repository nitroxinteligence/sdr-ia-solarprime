-- Migration: Adicionar campos de qualificação na tabela leads
-- Date: 2025-07-30
-- Description: Adiciona campos necessários para verificação de qualificação antes do agendamento

-- Adicionar campo de status de qualificação
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS qualification_status VARCHAR(20) DEFAULT 'PENDING' 
CHECK (qualification_status IN ('PENDING', 'QUALIFIED', 'NOT_QUALIFIED'));

-- Adicionar campo para verificar se é decisor
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS is_decision_maker BOOLEAN DEFAULT NULL;

-- Adicionar campo para verificar se tem sistema solar
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS has_solar_system BOOLEAN DEFAULT NULL;

-- Adicionar campo para verificar se quer novo sistema solar
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS wants_new_solar_system BOOLEAN DEFAULT NULL;

-- Adicionar campo para verificar se tem contrato ativo
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS has_active_contract BOOLEAN DEFAULT NULL;

-- Adicionar campo para data de término do contrato
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS contract_end_date TIMESTAMP WITH TIME ZONE DEFAULT NULL;

-- Adicionar campo para tipo de solução de interesse (já pode existir)
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS solution_interest VARCHAR(100) DEFAULT NULL;

-- Criar índice para buscar leads por status de qualificação
CREATE INDEX IF NOT EXISTS idx_leads_qualification_status ON leads(qualification_status);

-- Criar índice composto para buscar leads qualificados
CREATE INDEX IF NOT EXISTS idx_leads_qualified 
ON leads(qualification_status, bill_value, is_decision_maker) 
WHERE qualification_status = 'QUALIFIED';

-- Comentários nas colunas
COMMENT ON COLUMN leads.qualification_status IS 'Status de qualificação do lead: PENDING, QUALIFIED, NOT_QUALIFIED';
COMMENT ON COLUMN leads.is_decision_maker IS 'Se o lead é o decisor principal sobre energia';
COMMENT ON COLUMN leads.has_solar_system IS 'Se o lead já possui sistema de energia solar';
COMMENT ON COLUMN leads.wants_new_solar_system IS 'Se o lead quer instalar um novo sistema solar';
COMMENT ON COLUMN leads.has_active_contract IS 'Se o lead tem contrato de energia vigente com outra empresa';
COMMENT ON COLUMN leads.contract_end_date IS 'Data de término do contrato atual de energia';
COMMENT ON COLUMN leads.solution_interest IS 'Tipo de solução solar de interesse do lead';