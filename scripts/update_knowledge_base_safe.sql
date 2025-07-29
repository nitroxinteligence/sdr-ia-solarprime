-- Script SEGURO para atualizar tabelas de Knowledge Base
-- Este script pode ser executado múltiplas vezes sem erros

-- Habilitar extensões (se ainda não existirem)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Adicionar IF NOT EXISTS em todos os índices
DO $$ 
BEGIN
    -- Índices da knowledge_base
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_knowledge_category') THEN
        CREATE INDEX idx_knowledge_category ON knowledge_base(category);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_knowledge_keywords') THEN
        CREATE INDEX idx_knowledge_keywords ON knowledge_base USING GIN(keywords);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_knowledge_embedding') THEN
        CREATE INDEX idx_knowledge_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
    END IF;
    
    -- Índices da agent_sessions
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agent_sessions_session_id') THEN
        CREATE INDEX idx_agent_sessions_session_id ON agent_sessions(session_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agent_sessions_phone') THEN
        CREATE INDEX idx_agent_sessions_phone ON agent_sessions(phone_number);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_agent_sessions_updated') THEN
        CREATE INDEX idx_agent_sessions_updated ON agent_sessions(updated_at);
    END IF;
    
    -- Índice da embeddings
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'embeddings_embedding_idx') THEN
        CREATE INDEX embeddings_embedding_idx ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    END IF;
END $$;

-- Verificar e inserir dados apenas se não existirem
DO $$
BEGIN
    -- Verificar se a tabela knowledge_base está vazia
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

-- Mostrar estatísticas
SELECT 
    'Tabelas criadas:' as info,
    COUNT(DISTINCT tablename) as total
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('knowledge_base', 'agent_sessions', 'embeddings');

SELECT 
    'Registros na knowledge_base:' as info,
    COUNT(*) as total
FROM knowledge_base;

SELECT 
    'Distribuição por categoria:' as info,
    category, 
    COUNT(*) as total
FROM knowledge_base
GROUP BY category
ORDER BY category;