-- Script para popular a tabela knowledge_base no Supabase
-- Execute este script no SQL Editor do Supabase

-- Limpar dados existentes (opcional)
-- DELETE FROM knowledge_base;

-- Inserir informações da Solar Prime
INSERT INTO knowledge_base (title, content, category, tags, created_at, updated_at)
VALUES 
(
    'Informações da Empresa Solar Prime',
    'A Solar Prime é líder em soluções de energia solar fotovoltaica em Pernambuco, com mais de 5 anos de experiência no mercado. Nossa missão é democratizar o acesso à energia solar, proporcionando economia e sustentabilidade para residências e empresas. Oferecemos economia garantida de até 95% na conta de luz, instalação em até 30 dias, 25 anos de garantia nos painéis solares, 10 anos de garantia no inversor, monitoramento 24/7 via aplicativo, equipe técnica certificada, mais de 2000 clientes satisfeitos, nota 4.9 no Google e parceria com as melhores marcas do mercado.',
    'empresa',
    ARRAY['solar prime', 'empresa', 'sobre', 'informações', 'missão'],
    NOW(),
    NOW()
),
(
    'Processo de Instalação Solar',
    'Nosso processo de instalação é simples e eficiente: 1) Análise da conta de luz para dimensionamento correto, 2) Projeto personalizado de acordo com suas necessidades, 3) Aprovação na concessionária local (cuidamos de toda burocracia), 4) Instalação profissional em até 2 dias, 5) Ativação e monitoramento do sistema. Todo o processo leva em média 30 dias do contrato até a geração de energia.',
    'instalacao',
    ARRAY['instalação', 'processo', 'etapas', 'prazo'],
    NOW(),
    NOW()
),
(
    'Formas de Pagamento',
    'Oferecemos diversas formas de pagamento para facilitar seu investimento em energia solar: À vista com 10% de desconto especial, Parcelamento em até 84x sem entrada, Financiamento bancário com carência de 6 meses, Modelo de assinatura mensal (você paga apenas pela energia gerada). Temos sempre uma opção que cabe no seu bolso!',
    'financeiro',
    ARRAY['pagamento', 'financiamento', 'parcelamento', 'valores'],
    NOW(),
    NOW()
),
(
    'Kit Residencial Básico',
    'Para contas de R$ 200 a R$ 400: Sistema de 2-3 kWp com 4 a 6 painéis de 550W, inversor de 3kW, produção média de 350 kWh/mês. Investimento a partir de R$ 8.990 com payback de 4 anos. Ideal para casas pequenas e médias.',
    'produtos',
    ARRAY['kit', 'residencial', 'básico', 'produto', '3kwp'],
    NOW(),
    NOW()
),
(
    'Kit Residencial Intermediário',
    'Para contas de R$ 400 a R$ 700: Sistema de 4-5 kWp com 8 a 10 painéis de 550W, inversor de 5kW, produção média de 600 kWh/mês. Investimento a partir de R$ 14.990 com excelente custo-benefício. Perfeito para famílias de 3-4 pessoas.',
    'produtos',
    ARRAY['kit', 'residencial', 'intermediário', 'produto', '5kwp'],
    NOW(),
    NOW()
),
(
    'Kit Residencial Premium',
    'Para contas de R$ 700 a R$ 1.200: Sistema de 6-8 kWp com 12 a 16 painéis de 550W, inversor de 8kW, produção média de 1000 kWh/mês. Investimento a partir de R$ 22.990. Solução completa para grandes residências.',
    'produtos',
    ARRAY['kit', 'residencial', 'premium', 'produto', '8kwp'],
    NOW(),
    NOW()
),
(
    'Painéis Solares Canadian',
    'Utilizamos painéis Canadian Solar 550W Mono PERC com eficiência de 21,3%, certificação Tier 1, 25 anos de garantia de produção. Resistentes a granizo e ventos fortes, são os melhores do mercado mundial.',
    'componentes',
    ARRAY['painel', 'canadian', 'componente', 'equipamento'],
    NOW(),
    NOW()
),
(
    'Inversores de Qualidade',
    'Trabalhamos com as melhores marcas: Growatt para residencial, Fronius para comercial, Huawei para industrial. Todos com 10 anos de garantia, monitoramento via WiFi e eficiência superior a 98%.',
    'componentes',
    ARRAY['inversor', 'growatt', 'fronius', 'huawei', 'componente'],
    NOW(),
    NOW()
),
(
    'Objeção: É muito caro',
    'Entendo sua preocupação! Mas veja só: não é um gasto, é um investimento. Você para de pagar conta de luz e em 4 anos o sistema se paga. Depois disso, são mais 21 anos de energia grátis! Além disso, temos parcelamento em até 84x, que fica menor que sua conta atual.',
    'objecoes',
    ARRAY['objeção', 'caro', 'preço', 'valor', 'investimento'],
    NOW(),
    NOW()
),
(
    'Objeção: Não tenho dinheiro agora',
    'Totalmente compreensível! Por isso criamos o financiamento com 6 meses de carência. Você só começa a pagar depois que já está economizando. E a parcela fica menor que sua conta de luz atual!',
    'objecoes',
    ARRAY['objeção', 'dinheiro', 'financeiro', 'pagamento'],
    NOW(),
    NOW()
),
(
    'Objeção: Preciso pensar',
    'Claro, é uma decisão importante! Enquanto você pensa, está perdendo dinheiro todo mês com a conta de luz. Que tal agendarmos uma visita sem compromisso para você tirar todas as dúvidas? Assim você pode decidir com mais segurança.',
    'objecoes',
    ARRAY['objeção', 'pensar', 'decidir', 'dúvida'],
    NOW(),
    NOW()
),
(
    'Objeção: E se eu me mudar?',
    'Excelente pergunta! O sistema solar valoriza seu imóvel em até 10%. Se vender, você recupera o investimento. Se alugar, pode cobrar mais pelo aluguel. E se quiser, podemos até transferir o sistema para sua nova casa!',
    'objecoes',
    ARRAY['objeção', 'mudar', 'mudança', 'imóvel'],
    NOW(),
    NOW()
),
(
    'Objeção: E em dias nublados?',
    'Boa pergunta! Os painéis funcionam com luminosidade, não só com sol direto. Em dias nublados produzem 20-30% da capacidade. E você acumula créditos nos dias de sol para usar quando precisar! O sistema é dimensionado considerando a média anual.',
    'objecoes',
    ARRAY['objeção', 'nublado', 'chuva', 'tempo', 'sol'],
    NOW(),
    NOW()
),
(
    'Benefícios da Energia Solar',
    'Economia de até 95% na conta de luz, proteção contra aumentos tarifários (que sobem 10% ao ano), valorização do imóvel em até 10%, contribuição para o meio ambiente, independência energética, retorno garantido do investimento, incentivos fiscais e créditos de carbono.',
    'beneficios',
    ARRAY['benefícios', 'vantagens', 'economia', 'sustentabilidade'],
    NOW(),
    NOW()
),
(
    'Garantias Solar Prime',
    '25 anos de garantia de produção nos painéis (80% da capacidade), 10 anos de garantia no inversor, 5 anos de garantia na instalação, 15 anos de garantia nas estruturas de fixação, 1 ano de manutenção preventiva gratuita, suporte técnico vitalício.',
    'garantias',
    ARRAY['garantia', 'suporte', 'manutenção', 'assistência'],
    NOW(),
    NOW()
),
(
    'Áreas de Atuação',
    'Atendemos toda a região: Grande Recife, Região Metropolitana de Pernambuco, Interior de Pernambuco, João Pessoa e região (PB), Maceió e região (AL). Instalação e suporte técnico local.',
    'atendimento',
    ARRAY['área', 'região', 'atendimento', 'localização', 'cidades'],
    NOW(),
    NOW()
),
(
    'Certificações e Parcerias',
    'Certificação INMETRO, Selo Procel de Eficiência Energética, ISO 9001:2015, Parceiro oficial Canadian Solar, Parceiro oficial Growatt, Parceiro oficial Fronius. Trabalhamos apenas com produtos certificados e de primeira linha.',
    'certificacoes',
    ARRAY['certificação', 'parceria', 'qualidade', 'selo'],
    NOW(),
    NOW()
),
(
    'Como Funciona o Sistema Solar',
    'Os painéis solares captam a luz do sol e geram energia elétrica em corrente contínua (CC). O inversor converte essa energia para corrente alternada (CA), compatível com sua casa. A energia gerada é consumida instantaneamente e o excesso vai para a rede, gerando créditos. À noite ou em dias de baixa produção, você usa os créditos acumulados.',
    'tecnologia',
    ARRAY['funcionamento', 'tecnologia', 'como funciona', 'sistema'],
    NOW(),
    NOW()
),
(
    'Manutenção do Sistema',
    'O sistema solar requer manutenção mínima: limpeza semestral dos painéis (incluída no primeiro ano), inspeção visual periódica, monitoramento remoto 24/7 via aplicativo. Os equipamentos são projetados para durar mais de 25 anos com manutenção adequada.',
    'manutencao',
    ARRAY['manutenção', 'limpeza', 'cuidados', 'durabilidade'],
    NOW(),
    NOW()
),
(
    'Lei 14.300 e Marco Legal',
    'A lei 14.300/2022 garantiu segurança jurídica para energia solar. Quem instalar até 2025 tem direito adquirido por 25 anos com isenção de taxas. Após 2025, haverá cobrança gradual sobre a energia injetada na rede. Por isso, quanto antes instalar, melhor!',
    'legislacao',
    ARRAY['lei', 'legislação', 'marco legal', 'regulamentação', 'taxação'],
    NOW(),
    NOW()
);

-- Verificar se os dados foram inseridos
SELECT COUNT(*) as total_documentos FROM knowledge_base;
SELECT category, COUNT(*) as quantidade FROM knowledge_base GROUP BY category ORDER BY category;