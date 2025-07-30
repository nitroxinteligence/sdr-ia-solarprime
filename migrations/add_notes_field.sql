-- Migration: Adicionar campo notes na tabela leads
-- Date: 2025-07-30
-- Description: Adiciona campo para armazenar observações gerais sobre o lead

-- Adicionar campo notes
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT NULL;

-- Adicionar comentário na coluna
COMMENT ON COLUMN leads.notes IS 'Observações gerais sobre o lead, incluindo histórico de interações e anotações importantes';

-- Criar índice para busca em texto (opcional, útil se for fazer buscas por conteúdo)
CREATE INDEX IF NOT EXISTS idx_leads_notes_search 
ON leads USING gin(to_tsvector('portuguese', notes))
WHERE notes IS NOT NULL;