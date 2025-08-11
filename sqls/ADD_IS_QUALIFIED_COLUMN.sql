-- Migration: Adicionar coluna is_qualified à tabela leads
-- Data: 04/08/2025
-- Motivo: Código espera essa coluna mas ela não existe

-- Adicionar coluna is_qualified como computed column baseada em qualification_status
ALTER TABLE public.leads 
ADD COLUMN IF NOT EXISTS is_qualified BOOLEAN 
GENERATED ALWAYS AS (
    CASE 
        WHEN qualification_status = 'QUALIFIED' THEN TRUE
        ELSE FALSE
    END
) STORED;

-- Criar índice para melhor performance
CREATE INDEX IF NOT EXISTS idx_leads_is_qualified 
ON public.leads (is_qualified) 
WHERE is_qualified = TRUE;

-- Comentário explicativo
COMMENT ON COLUMN public.leads.is_qualified IS 
'Coluna computada: TRUE quando qualification_status = QUALIFIED. Criada para compatibilidade com o código legado.';