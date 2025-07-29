-- Script para criar tabelas de Knowledge Base e Agent Sessions no Supabase
-- Execute este script no Supabase SQL Editor

-- Habilitar extensão para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Habilitar extensão para vetores (embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- ==============================================
-- TABELA: knowledge_base
-- ==============================================
-- Armazena a base de conhecimento da SolarPrime
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT[],
    metadata JSONB DEFAULT '{}',
    embedding vector(1536), -- Para busca semântica com OpenAI embeddings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance (IF NOT EXISTS para evitar erros)
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_keywords ON knowledge_base USING GIN(keywords);
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_knowledge_base_updated_at ON knowledge_base;
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- TABELA: agent_sessions
-- ==============================================
-- Armazena o estado das sessões do agente AGnO
CREATE TABLE IF NOT EXISTS agent_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    state JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance (IF NOT EXISTS para evitar erros)
CREATE INDEX IF NOT EXISTS idx_agent_sessions_session_id ON agent_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_phone ON agent_sessions(phone_number);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_updated ON agent_sessions(updated_at);

-- Trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_agent_sessions_updated_at ON agent_sessions;
CREATE TRIGGER update_agent_sessions_updated_at BEFORE UPDATE ON agent_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- DADOS INICIAIS: Knowledge Base
-- ==============================================

-- Limpar dados existentes antes de inserir (opcional - descomente se quiser recriar)
-- TRUNCATE TABLE knowledge_base CASCADE;

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

-- Adicionar mais FAQs conforme necessário...

-- ==============================================
-- POLÍTICAS DE SEGURANÇA (RLS)
-- ==============================================

-- Habilitar RLS
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_sessions ENABLE ROW LEVEL SECURITY;

-- Política para knowledge_base (leitura pública, escrita apenas service role)
DROP POLICY IF EXISTS "Public read access to knowledge" ON knowledge_base;
CREATE POLICY "Public read access to knowledge" ON knowledge_base
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Service role full access to knowledge" ON knowledge_base;
CREATE POLICY "Service role full access to knowledge" ON knowledge_base
    FOR ALL USING (auth.role() = 'service_role');

-- Política para agent_sessions (apenas service role)
DROP POLICY IF EXISTS "Service role full access to sessions" ON agent_sessions;
CREATE POLICY "Service role full access to sessions" ON agent_sessions
    FOR ALL USING (auth.role() = 'service_role');

-- ==============================================
-- FUNCTIONS: Busca semântica
-- ==============================================

-- Função para buscar conhecimento por similaridade
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
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Função para buscar conhecimento por keywords
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

-- ==============================================
-- FUNCTIONS: Integração com PgVector do AGnO
-- ==============================================

-- Função para criar tabela de embeddings do PgVector se não existir
-- O AGnO vai criar automaticamente, mas podemos pré-criar
CREATE TABLE IF NOT EXISTS embeddings (
    id TEXT PRIMARY KEY,
    content TEXT,
    meta_data JSONB,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca vetorial eficiente
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Função para match de documentos (usada pelo PgVector)
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
    RETURN QUERY
    SELECT 
        e.id,
        e.content,
        e.meta_data,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM embeddings e
    WHERE 
        CASE 
            WHEN filter = '{}'::JSONB THEN true
            ELSE e.meta_data @> filter
        END
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

COMMENT ON TABLE knowledge_base IS 'Base de conhecimento da SolarPrime para o agente de IA';
COMMENT ON TABLE agent_sessions IS 'Estado das sessões do agente AGnO Framework';
COMMENT ON TABLE embeddings IS 'Tabela de embeddings para busca vetorial com AGnO PgVector';