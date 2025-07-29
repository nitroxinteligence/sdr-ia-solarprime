-- ============================================
-- SCRIPT COMPLETO PARA SUPABASE - SDR IA SOLARPRIME V2
-- ============================================
-- Este script configura todo o banco de dados necessário para o sistema V2
-- Execute no Supabase SQL Editor (https://supabase.com/dashboard/project/rcjcpwqezmlhenmhrski/sql/new)

-- ============================================
-- 1. HABILITAR EXTENSÕES
-- ============================================
-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 2. CRIAR TABELAS PRINCIPAIS
-- ============================================

-- Tabela: knowledge_base (Base de conhecimento)
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT[],
    metadata JSONB DEFAULT '{}',
    embedding vector(1536), -- OpenAI text-embedding-3-small
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: agent_sessions (Sessões do agente)
CREATE TABLE IF NOT EXISTS agent_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    state JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: embeddings (Para AGnO PgVector)
-- Apenas criar se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'embeddings') THEN
        CREATE TABLE embeddings (
            id TEXT PRIMARY KEY,
            content TEXT,
            meta_data JSONB,
            embedding vector(1536),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
END $$;

-- ============================================
-- 3. CRIAR ÍNDICES COM VERIFICAÇÃO
-- ============================================

-- Função auxiliar para criar índices apenas se não existirem
CREATE OR REPLACE FUNCTION create_index_if_not_exists(
    index_name text,
    table_name text,
    index_definition text
) RETURNS void AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND indexname = index_name
    ) THEN
        EXECUTE format('CREATE INDEX %I ON %I %s', index_name, table_name, index_definition);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Criar índices da knowledge_base
SELECT create_index_if_not_exists('idx_knowledge_category', 'knowledge_base', '(category)');
SELECT create_index_if_not_exists('idx_knowledge_keywords', 'knowledge_base', 'USING GIN(keywords)');

-- Criar índice vetorial apenas se a coluna embedding existir e tiver dados
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'knowledge_base' 
        AND column_name = 'embedding'
    ) THEN
        -- Usar HNSW que é mais eficiente para busca de similaridade
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname = 'idx_knowledge_embedding'
        ) THEN
            CREATE INDEX idx_knowledge_embedding ON knowledge_base 
            USING hnsw (embedding vector_cosine_ops);
        END IF;
    END IF;
END $$;

-- Criar índices da agent_sessions
SELECT create_index_if_not_exists('idx_agent_sessions_session_id', 'agent_sessions', '(session_id)');
SELECT create_index_if_not_exists('idx_agent_sessions_phone', 'agent_sessions', '(phone_number)');
SELECT create_index_if_not_exists('idx_agent_sessions_updated', 'agent_sessions', '(updated_at DESC)');

-- Criar índice vetorial da embeddings se a tabela existir
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'embeddings'
    ) THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname = 'embeddings_embedding_idx'
        ) THEN
            CREATE INDEX embeddings_embedding_idx ON embeddings 
            USING hnsw (embedding vector_cosine_ops);
        END IF;
    END IF;
END $$;

-- Limpar função temporária
DROP FUNCTION IF EXISTS create_index_if_not_exists(text, text, text);

-- ============================================
-- 4. CRIAR TRIGGERS
-- ============================================

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar triggers com verificação
DO $$
BEGIN
    -- Trigger para knowledge_base
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'update_knowledge_base_updated_at'
    ) THEN
        CREATE TRIGGER update_knowledge_base_updated_at 
        BEFORE UPDATE ON knowledge_base
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- Trigger para agent_sessions
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'update_agent_sessions_updated_at'
    ) THEN
        CREATE TRIGGER update_agent_sessions_updated_at 
        BEFORE UPDATE ON agent_sessions
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- ============================================
-- 5. CONFIGURAR ROW LEVEL SECURITY (RLS)
-- ============================================

-- Habilitar RLS
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_sessions ENABLE ROW LEVEL SECURITY;

-- Limpar políticas antigas se existirem
DROP POLICY IF EXISTS "Public read access to knowledge" ON knowledge_base;
DROP POLICY IF EXISTS "Service role full access to knowledge" ON knowledge_base;
DROP POLICY IF EXISTS "Service role full access to sessions" ON agent_sessions;

-- Criar políticas
-- Knowledge base: leitura pública, escrita apenas service role
CREATE POLICY "Public read access to knowledge" ON knowledge_base
    FOR SELECT USING (true);

CREATE POLICY "Service role full access to knowledge" ON knowledge_base
    FOR ALL USING (auth.role() = 'service_role');

-- Agent sessions: apenas service role
CREATE POLICY "Service role full access to sessions" ON agent_sessions
    FOR ALL USING (auth.role() = 'service_role');

-- RLS para embeddings se existir
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'embeddings'
    ) THEN
        ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
        
        DROP POLICY IF EXISTS "Service role full access to embeddings" ON embeddings;
        CREATE POLICY "Service role full access to embeddings" ON embeddings
            FOR ALL USING (auth.role() = 'service_role');
    END IF;
END $$;

-- ============================================
-- 6. CRIAR FUNÇÕES DE BUSCA
-- ============================================

-- Função para busca semântica na knowledge_base
CREATE OR REPLACE FUNCTION search_knowledge(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 3
)
RETURNS TABLE (
    id uuid,
    category varchar,
    question text,
    answer text,
    keywords text[],
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        id,
        category,
        question,
        answer,
        keywords,
        1 - (embedding <=> query_embedding) as similarity
    FROM knowledge_base
    WHERE embedding IS NOT NULL
    AND 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Função para busca por keywords
CREATE OR REPLACE FUNCTION search_knowledge_by_keywords(
    search_keywords text[]
)
RETURNS TABLE (
    id uuid,
    category varchar,
    question text,
    answer text,
    keywords text[],
    match_count integer
)
LANGUAGE plpgsql STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.category,
        kb.question,
        kb.answer,
        kb.keywords,
        (
            SELECT COUNT(*)::integer
            FROM unnest(kb.keywords) AS k
            WHERE k = ANY(search_keywords)
        ) AS match_count
    FROM knowledge_base kb
    WHERE kb.keywords && search_keywords
    ORDER BY match_count DESC;
END;
$$;

-- Função para match de documentos (compatível com AGnO PgVector)
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    filter JSONB DEFAULT '{}'::JSONB
)
RETURNS TABLE (
    id TEXT,
    content TEXT,
    meta_data JSONB,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Verificar se a tabela embeddings existe
    IF EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'embeddings'
    ) THEN
        RETURN QUERY
        SELECT 
            e.id,
            e.content,
            e.meta_data,
            1 - (e.embedding <=> query_embedding) as similarity
        FROM embeddings e
        WHERE 
            e.embedding IS NOT NULL
            AND CASE 
                WHEN filter = '{}'::JSONB THEN true
                ELSE e.meta_data @> filter
            END
        ORDER BY e.embedding <=> query_embedding
        LIMIT match_count;
    END IF;
END;
$$;

-- ============================================
-- 7. INSERIR DADOS INICIAIS (SE NÃO EXISTIREM)
-- ============================================

-- Verificar e inserir dados apenas se a tabela estiver vazia
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM knowledge_base LIMIT 1) THEN
        RAISE NOTICE 'Inserindo dados iniciais na knowledge_base...';
        
        -- Categoria: Preços e Custos
        INSERT INTO knowledge_base (category, question, answer, keywords) VALUES
        ('preco', 'Quanto custa instalar energia solar?', 'O investimento em energia solar residencial na SolarPrime começa a partir de R$ 12.000, variando conforme o tamanho do sistema necessário. Oferecemos financiamento em até 84x com taxas especiais. O payback médio é de 3 a 4 anos.', ARRAY['preço', 'custo', 'valor', 'investimento', 'instalação', 'quanto custa']),
        ('preco', 'Vocês fazem financiamento?', 'Sim! A SolarPrime oferece financiamento em até 84 meses com as melhores taxas do mercado. Trabalhamos com os principais bancos e também temos parcerias especiais. A aprovação é rápida e pode ser feita durante a visita técnica.', ARRAY['financiamento', 'parcelamento', 'pagamento', 'banco', 'crédito']),
        ('preco', 'Qual o valor da manutenção?', 'A manutenção do sistema solar é mínima e muito barata. Recomendamos apenas a limpeza dos painéis a cada 6 meses, que pode ser feita com água. Se preferir, oferecemos plano de manutenção por R$ 150 por visita.', ARRAY['manutenção', 'limpeza', 'custo manutenção', 'valor manutenção']);

        -- Categoria: Economia
        INSERT INTO knowledge_base (category, question, answer, keywords) VALUES
        ('economia', 'Quanto vou economizar na conta de luz?', 'Com energia solar você pode economizar até 95% na sua conta de luz! A economia exata depende do seu consumo e do sistema instalado. Na consulta gratuita, fazemos uma simulação personalizada mostrando sua economia mensal e anual.', ARRAY['economia', 'economizar', 'desconto', 'conta de luz', 'redução']),
        ('economia', 'Em quanto tempo o sistema se paga?', 'O payback (retorno do investimento) geralmente ocorre entre 3 a 4 anos. Após esse período, você terá energia praticamente gratuita por mais de 20 anos! É um dos melhores investimentos disponíveis hoje.', ARRAY['payback', 'retorno', 'investimento', 'tempo', 'se paga']),
        ('economia', 'Vale a pena mesmo?', 'Absolutamente! Além da economia de até 95% na conta de luz, você fica protegido dos aumentos tarifários, valoriza seu imóvel em até 10% e contribui com o meio ambiente. É um investimento com retorno garantido.', ARRAY['vale a pena', 'vantagem', 'benefício', 'retorno']);

        -- Categoria: Técnica
        INSERT INTO knowledge_base (category, question, answer, keywords) VALUES
        ('tecnica', 'Como funciona a energia solar?', 'Os painéis solares captam a luz do sol e a transformam em energia elétrica através do efeito fotovoltaico. O inversor converte essa energia para o padrão da sua casa. O excesso é enviado para a rede e vira créditos na sua conta.', ARRAY['como funciona', 'funcionamento', 'sistema solar', 'painel solar']),
        ('tecnica', 'Funciona em dias nublados?', 'Sim! Os painéis solares funcionam mesmo em dias nublados, apenas com eficiência reduzida. O sistema é dimensionado considerando a média anual de radiação solar, garantindo economia mesmo com variações climáticas.', ARRAY['nublado', 'chuva', 'tempo', 'clima', 'funciona']),
        ('tecnica', 'Quantos painéis preciso?', 'A quantidade de painéis depende do seu consumo mensal de energia. Em média, residências precisam de 8 a 16 painéis. Na visita técnica gratuita, calculamos exatamente quantos painéis você precisa.', ARRAY['quantos painéis', 'quantidade', 'número de painéis']),
        ('tecnica', 'Qual a durabilidade do sistema?', 'Os painéis solares têm garantia de 25 anos de performance e podem durar mais de 30 anos! O inversor tem garantia de 5 a 10 anos. A SolarPrime oferece garantia total de instalação por 5 anos.', ARRAY['durabilidade', 'garantia', 'vida útil', 'duração', 'anos']);

        -- Categoria: Instalação
        INSERT INTO knowledge_base (category, question, answer, keywords) VALUES
        ('instalacao', 'Como é feita a instalação?', 'A instalação é rápida e profissional! Nossa equipe técnica instala todo o sistema em 1 a 2 dias. Cuidamos de toda a parte elétrica, fixação dos painéis e configuração do sistema. Tudo com segurança e garantia.', ARRAY['instalação', 'instalar', 'como instala', 'processo']),
        ('instalacao', 'Preciso fazer obra?', 'Não! A instalação de energia solar não requer obras civis. Os painéis são fixados na estrutura existente do telhado com sistemas de fixação apropriados. É um processo limpo e sem quebra-quebra.', ARRAY['obra', 'reforma', 'bagunça', 'quebrar']),
        ('instalacao', 'Precisa de autorização?', 'A SolarPrime cuida de todo o processo burocrático para você! Fazemos o projeto, solicitamos aprovação na distribuidora de energia e cuidamos de toda documentação necessária. Você não precisa se preocupar com nada.', ARRAY['autorização', 'documentação', 'burocracia', 'aprovação']);

        -- Categoria: Empresa
        INSERT INTO knowledge_base (category, question, answer, keywords) VALUES
        ('empresa', 'Quem é a SolarPrime?', 'A SolarPrime Boa Viagem é líder em energia solar em Pernambuco, com mais de 500 sistemas instalados. Somos uma empresa sólida, com equipe própria de engenheiros e técnicos certificados. Nosso compromisso é com sua economia e satisfação.', ARRAY['solarprime', 'empresa', 'quem é', 'sobre']),
        ('empresa', 'Vocês têm referências?', 'Sim! Temos centenas de clientes satisfeitos em Boa Viagem e região. Podemos mostrar casos de sucesso próximos a você. Nossos clientes economizam em média R$ 400 por mês e estão extremamente satisfeitos.', ARRAY['referências', 'clientes', 'casos', 'exemplos']),
        ('empresa', 'Qual o diferencial de vocês?', 'Nosso diferencial é o compromisso com resultado: garantimos a economia prometida, usamos apenas equipamentos premium com certificação internacional, temos equipe própria (não terceirizamos) e oferecemos 5 anos de garantia total.', ARRAY['diferencial', 'vantagem', 'por que vocês', 'melhor']);

        -- Categoria: Processo
        INSERT INTO knowledge_base (category, question, answer, keywords) VALUES
        ('processo', 'Como faço para contratar?', 'É muito simples! 1) Agende uma consulta gratuita, 2) Receba nosso consultor para análise, 3) Aprovando a proposta, cuidamos de toda instalação e documentação. Em 30 dias você já está economizando!', ARRAY['contratar', 'processo', 'como fazer', 'passo a passo']),
        ('processo', 'Demora quanto tempo?', 'Do contrato à energia solar funcionando são aproximadamente 30 dias. Isso inclui: projeto (5 dias), aprovação na distribuidora (15 dias), instalação (2 dias) e ativação do sistema (7 dias).', ARRAY['tempo', 'prazo', 'demora', 'quanto tempo']),
        ('processo', 'Posso acompanhar o processo?', 'Claro! Você recebe atualizações em cada etapa do processo via WhatsApp. Temos um portal do cliente onde pode acompanhar tudo online. Transparência total do início ao fim.', ARRAY['acompanhar', 'status', 'andamento', 'processo']);
        
        RAISE NOTICE 'Dados iniciais inseridos com sucesso!';
    ELSE
        RAISE NOTICE 'Tabela knowledge_base já contém dados. Pulando inserção.';
    END IF;
END $$;

-- ============================================
-- 8. ESTATÍSTICAS E VERIFICAÇÃO
-- ============================================

-- Mostrar resultado da configuração
DO $$
DECLARE
    kb_count INTEGER;
    session_count INTEGER;
    embed_exists BOOLEAN;
BEGIN
    -- Contar registros
    SELECT COUNT(*) INTO kb_count FROM knowledge_base;
    SELECT COUNT(*) INTO session_count FROM agent_sessions;
    SELECT EXISTS(SELECT 1 FROM pg_tables WHERE tablename = 'embeddings') INTO embed_exists;
    
    RAISE NOTICE '=== CONFIGURAÇÃO CONCLUÍDA ===';
    RAISE NOTICE '✅ Tabela knowledge_base: % registros', kb_count;
    RAISE NOTICE '✅ Tabela agent_sessions: % registros', session_count;
    RAISE NOTICE '✅ Tabela embeddings: %', CASE WHEN embed_exists THEN 'criada' ELSE 'não criada' END;
    RAISE NOTICE '✅ Extensões habilitadas: uuid-ossp, vector';
    RAISE NOTICE '✅ RLS configurado com políticas de segurança';
    RAISE NOTICE '✅ Funções de busca criadas';
    RAISE NOTICE '';
    RAISE NOTICE '🎉 Sistema pronto para uso!';
END $$;

-- Comentários nas tabelas
COMMENT ON TABLE knowledge_base IS 'Base de conhecimento da SolarPrime para o agente de IA';
COMMENT ON TABLE agent_sessions IS 'Estado das sessões do agente AGnO Framework';
COMMENT ON TABLE embeddings IS 'Tabela de embeddings para busca vetorial com AGnO PgVector';