-- Migration: Adicionar coluna chosen_flow na tabela leads
-- Data: 2025-08-12
-- Descrição: Campo para armazenar o fluxo de solução escolhido pelo lead

-- 1. Adicionar a coluna chosen_flow
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS chosen_flow VARCHAR(100) NULL;

-- 2. Adicionar comentário explicativo
COMMENT ON COLUMN public.leads.chosen_flow IS 'Fluxo de solução escolhido pelo lead: Instalação Usina Própria, Aluguel de Lote, Compra com Desconto, Usina Investimento';

-- 3. Criar índice para busca rápida por fluxo escolhido
CREATE INDEX IF NOT EXISTS idx_leads_chosen_flow 
ON public.leads(chosen_flow) 
WHERE chosen_flow IS NOT NULL;

-- 4. Adicionar constraint check para valores válidos (opcional mas recomendado)
ALTER TABLE public.leads
ADD CONSTRAINT leads_chosen_flow_check CHECK (
    chosen_flow IS NULL OR 
    chosen_flow IN (
        'Instalação Usina Própria',
        'Aluguel de Lote', 
        'Compra com Desconto',
        'Usina Investimento'
    )
);

-- 5. Adicionar coluna google_event_link se não existir
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS google_event_link TEXT NULL;

-- 6. Adicionar comentário para google_event_link
COMMENT ON COLUMN public.leads.google_event_link IS 'Link do evento no Google Calendar para reunião agendada';

-- 7. Criar índice para google_event_link
CREATE INDEX IF NOT EXISTS idx_leads_google_event_link 
ON public.leads(google_event_link) 
WHERE google_event_link IS NOT NULL;

-- 8. Atualizar timestamp de modificação
UPDATE public.leads 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

-- Verificar se a migration foi aplicada com sucesso
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'leads' 
        AND column_name = 'chosen_flow'
    ) THEN
        RAISE NOTICE '✅ Coluna chosen_flow adicionada com sucesso!';
    ELSE
        RAISE EXCEPTION '❌ Erro ao adicionar coluna chosen_flow';
    END IF;
    
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'leads' 
        AND column_name = 'google_event_link'
    ) THEN
        RAISE NOTICE '✅ Coluna google_event_link adicionada com sucesso!';
    ELSE
        RAISE EXCEPTION '❌ Erro ao adicionar coluna google_event_link';
    END IF;
END $$;