-- ===============================================
-- Script de Inserção de Dados - Knowledge Base SolarPrime
-- ===============================================
-- Este script insere toda a base de conhecimento Q&A da SolarPrime
-- Baseado no arquivo docs/KNOWLEDGE-RAG.md
-- ===============================================

-- Limpar dados existentes (opcional - remova se quiser preservar dados anteriores)
-- TRUNCATE TABLE knowledge_base CASCADE;

-- Inserir dados da Knowledge Base
INSERT INTO knowledge_base (category, question, answer, keywords, metadata) VALUES

-- 1. Vantagens e Diferenciais
('vantagens', 
'Que vantagens a Solarprime oferece em relação aos concorrentes?',
'A Solarprime oferece vantagens únicas que nos diferenciam no mercado. Primeiro, garantimos **mínimo de 20% de desconto sobre toda a conta** não apenas sobre o consumo como fazem os concorrentes. Segundo, **no final do contrato, a usina é sua**, o que aumenta ainda mais sua economia a longo prazo. Terceiro, oferecemos **energia limpa e barata** sem investimentos e sem obras montamos a usina ideal para o seu negócio. Quarto, você tem **previsibilidade financeira** sem surpresas no final do mês, protegido dos aumentos de bandeiras tarifárias. Diferente da Origo, que promete 35% mas entrega apenas 15% real, ou da Setta, que exige mudança de titularidade, nós oferecemos transparência total e você mantém sua conta no seu nome.',
ARRAY['vantagens', 'diferenciais', 'concorrentes', 'desconto', 'usina própria', 'economia'],
'{"similar_questions": ["Por que escolher a Solarprime ao invés de outras empresas de energia solar?", "Quais os diferenciais da Solarprime no mercado?", "Como a Solarprime se destaca da concorrência?"], "tags": ["Mínimo de 20% de desconto sobre toda a conta: economia garantida; Ganho da usina: ao final do contrato, a usina é sua. Energia limpa e barata: transforme a sua empresa em sustentável e gastando menos; Previsibilidade financeira: sem surpresas no final do mês; Sem investimentos e sem obras: montamos a usina ideal para o seu negócio"]}'::jsonb),

-- 2. Modelo de Assinatura
('modelo_assinatura',
'Como funciona o modelo de assinatura em baixa tensão para contas acima de R$4.000?',
'Nosso modelo de assinatura em baixa tensão é ideal para contas acima de R$4.000,00. Oferecemos **20% de desconto sobre toda a conta** com economia garantida em contrato. O melhor de tudo: você não precisa investir nada e não há obras no seu local nós montamos a usina ideal para o seu negócio em nossos loteamentos parceiros. Você tem **previsibilidade financeira** total, sem surpresas no final do mês, e fica protegido dos aumentos das bandeiras tarifárias porque o desconto é calculado com base na tarifa padrão. E aqui está nosso grande diferencial: **ao final do contrato, a usina é sua**, garantindo economia ainda maior por mais de 25 anos. Transforme sua empresa em sustentável gastando menos!',
ARRAY['assinatura', 'baixa tensão', 'desconto', 'economia', 'conta acima 4000'],
'{"similar_questions": ["Qual é o processo da assinatura de energia para empresas?", "Como funciona o desconto de 20% na conta de luz?", "O que inclui a assinatura de baixa tensão da Solarprime?"], "tags": ["20% de desconto sobre toda a conta: economia garantida; Sem investimentos e sem obras: montamos a usina ideal para o seu negócio; Energia limpa e barata: transforme a sua empresa em sustentável e gastando menos; Previsibilidade financeira: sem surpresas no final do mês; Ganho da usina: ao final do contrato, a usina é sua."]}'::jsonb),

-- 3. Comparação com Origo
('concorrentes',
'Qual a diferença entre vocês e a Origo Energia?',
'Conheço sim o modelo da Origo, inclusive estamos migrando alguns clientes da Origo para o nosso modelo. A Origo fala que oferece 35% líquido, mas na verdade é bruto o desconto real fica em torno de 10 a 15% apenas sobre o consumo. Além disso, o cliente paga duas faturas: uma da Origo e outra da distribuidora com taxa de iluminação pública e bandeiras tarifárias. **Sem previsibilidade financeira** todo mês pode vir um valor diferente porque a conta varia conforme a inflação energética. A Origo também tem alto índice de reclamação no Reclame Aqui. No nosso caso, além de darmos um desconto real de 20%, **o desconto é aplicado em cima de toda a conta de luz**, não apenas do consumo, e ainda entregamos a usina para você ao final do contrato.',
ARRAY['origo', 'comparação', 'concorrente', 'diferença', 'desconto real'],
'{"similar_questions": ["Como a Solarprime se compara com a Origo?", "Por que não contratar a Origo?", "Quais os problemas da Origo Energia?"], "tags": ["Conheço sim o modelo da Origo, inclusive estamos migrando alguns clientes da Origo para o nosso modelo, porque hoje a Origo oferece em torno de 10 a 15% de desconto em cima apenas do consumo"]}'::jsonb),

-- 4. Economia sem Investimento
('economia',
'Como posso economizar na conta de luz sem fazer investimento?',
'Sim! Na Solarprime você consegue **energia solar sem gastar 1 real**. Você não paga por equipamento, instalação nem manutenção. Nós oferecemos um desconto mínimo de 20% líquido na sua conta de luz garantido em contrato, sem precisar investir nada e sem obras no seu local. Montamos uma usina personalizada para o seu negócio em nossos loteamentos parceiros e damos o desconto de 20% todo mês para você. E no final do nosso contrato você ainda se torna dono da usina. **Não é necessário nem mudar a titularidade da sua conta**. É literalmente economia sem investimento!',
ARRAY['economia', 'sem investimento', 'energia grátis', 'zero custo'],
'{"similar_questions": ["É possível ter energia solar sem gastar dinheiro?", "Como funciona energia solar sem investimento?", "Vocês instalam painéis solares de graça?"], "tags": ["Energia solar sem gastar 1 real. Você não paga por equipamento, instalação nem manutenção"]}'::jsonb),

-- 5. Valor Mínimo
('requisitos',
'Qual o valor mínimo da conta de luz para contratar vocês?',
'No nosso modelo de assinatura, atendemos contas a partir de R$4.000,00 mensais. Mas se sua conta individual não atinge esse valor, **podemos juntar a conta de luz do seu estabelecimento com a da sua casa**, por exemplo, ou outras unidades que você tenha, desde que a soma chegue em R$4.000,00. Para contas menores, entre R$400,00 e R$4.000,00, temos outra modalidade com desconto de 12% a 15%. Já para o mercado livre e alta tensão, oferecemos 35% de desconto. Cada perfil tem sua solução ideal na Solarprime!',
ARRAY['valor mínimo', 'conta mínima', 'requisitos', 'R$4000', 'consumo mínimo'],
'{"similar_questions": ["Qual o consumo mínimo para a Solarprime?", "A partir de quanto posso contratar a assinatura?", "Vocês atendem contas pequenas de energia?"], "tags": ["No nosso modelo nós pegamos contas a partir de R$4.000, mas podemos juntar a conta de luz do seu estabelecimento com a da sua casa, por exemplo ou caso você tenha com outras unidades, portanto que a soma chegue em R$4.000,00"]}'::jsonb),

-- 6. Duração do Contrato
('contrato',
'Quanto tempo dura o contrato e quando recebo a usina?',
'Nosso tempo mínimo de contrato varia em torno de **36 a 40 meses**, mas **o ganho da usina ocorre após 6 anos**. Se você desejar, também é possível comprar essa usina antes dos 6 anos nós damos essa possibilidade. Quanto ao cancelamento, se ocorrer por motivos de força maior como fechamento da empresa, **não cobramos nenhuma multa**. Mas se for por opção própria, é cobrado o valor de aluguel do lote vezes o tempo restante do contrato mínimo. Posso te passar de forma exata após a elaboração do contrato, mas hoje **nenhum cliente saiu do nosso modelo** pelo fato de todos quererem a usina no final do contrato.',
ARRAY['contrato', 'prazo', 'duração', 'usina própria', 'cancelamento'],
'{"similar_questions": ["Qual o prazo do contrato da Solarprime?", "Quando a usina fica minha?", "Posso cancelar o contrato antes do prazo?"], "tags": ["O nosso tempo mínimo de contrato varia em torno de 36 - 40 meses, mas o ganho da usina ocorre após 6 anos, mas se você desejar também é possível comprar essa usina antes dos 6 anos"]}'::jsonb),

-- 7. Posicionamento no Mercado
('empresa',
'Como vocês se posicionam no mercado brasileiro?',
'Somos **a maior rede de franquias de energia solar do Brasil** com mais de 460 franquias presentes nos 26 estados + DF. Já transformamos as vidas de **mais de 23 mil clientes satisfeitos** com + R$ 1 bilhão de faturamento em toda a rede e + R$ 23 milhões/mês de economia para nossos clientes. Além disso, somos a **única rede de franquias de energia solar Top 20 pela ABF** e fomos eleitos **Franquia 4 Estrelas** pela Pequenas Empresas & Grandes Negócios. No Reclame AQUI temos **reputação ÓTIMA** com 9,64% de nota do consumidor, 100% das reclamações respondidas e 100% voltariam a fazer negócio. Estamos no mercado desde 2014, então você pode confiar na nossa experiência e solidez.',
ARRAY['empresa', 'confiável', 'reputação', 'mercado', 'tamanho'],
'{"similar_questions": ["A Solarprime é confiável?", "Qual o tamanho da Solarprime no Brasil?", "Vocês são uma empresa grande?"], "tags": ["A maior rede do Brasil em soluções de energia. Mais de 460 franquias em todo o país. Presente nos 26 estados + DF. Mais de 23 mil clientes satisfeitos. + R$ 1 BILHÃO de faturamento em toda a rede"]}'::jsonb),

-- 8. Energia Solar Gratuita
('energia_gratis',
'Vocês realmente oferecem energia solar gratuita?',
'Sim, é verdade! **Você não paga por equipamento, instalação nem manutenção**. Nosso modelo funciona assim: montamos uma usina personalizada para você em nossos loteamentos parceiros e aplicamos o desconto direto na sua conta de luz. É como se você "alugasse" a energia da usina, pagando menos do que pagaria na distribuidora tradicional. O que você economiza todo mês já compensa qualquer "custo" do sistema. E o melhor: **no final do contrato a usina é sua**, então você passa a ter energia praticamente gratuita por mais de 25 anos. Não tem truque - é um modelo de negócio sustentável onde todos ganham: você economiza, nós construímos o negócio, e o planeta agradece!',
ARRAY['energia grátis', 'sem custo', 'gratuita', 'zero investimento'],
'{"similar_questions": ["É verdade que a energia solar é grátis?", "Como vocês conseguem dar energia solar de graça?", "Qual o truque da energia solar sem custo?"], "tags": ["Energia solar sem gastar 1 real. Você não paga por equipamento, instalação nem manutenção"]}'::jsonb),

-- 9. Proteção Bandeiras Tarifárias
('bandeiras',
'Como funciona a proteção contra as bandeiras tarifárias?',
'Exato! Você fica totalmente protegido dos aumentos das bandeiras amarela e vermelha porque **o desconto foi calculado com base na tarifa padrão**. Deixamos um valor pré-definido com base no seu consumo dos últimos 12 meses justamente para você não ser impactado com essas variações e ter surpresas no final do mês. Além disso, **não levamos em consideração a iluminação pública**, o que garante em torno de mais 1,5% de desconto. Na renovação contratual é levado em consideração o IPCA e não a inflação energética então se o IPCA for de 5% e a inflação energética for de 8%, esses 3% de diferença são ganho seu! **Previsibilidade financeira total**.',
ARRAY['bandeiras', 'tarifa', 'proteção', 'bandeira vermelha', 'bandeira amarela'],
'{"similar_questions": ["Vocês protegem contra aumento da conta de luz?", "Como fico protegido das bandeiras vermelhas?", "O desconto vale mesmo com bandeira vermelha?"], "tags": ["você fica protegido dos aumentos constantes que acontecem quando é acionado bandeira amarela, vermelha, pois o desconto foi calculado com base na tarifa padrão"]}'::jsonb),

-- 10. Comparação com Setta
('concorrentes',
'Qual a diferença entre vocês e a Setta Energia?',
'Conheço sim o modelo da Setta, inclusive estamos migrando alguns clientes da Setta para o nosso modelo. A proposta deles é bem parecida com a nossa, oferecendo 20% de desconto na conta de luz, mas temos **dois diferenciais importantes** em relação a eles. Primeiro: **a conta de luz vai ser no seu nome** você não vai precisar deixar a titularidade em nome de um terceiro como exige a Setta. Segundo: **nós vamos dar a usina para você no final do contrato**, garantindo economia ainda maior a longo prazo. Além disso, muitos relatam que a compensação da Setta não chega em 20% líquido e o valor varia todo mês de acordo com a inflação energética. Nosso modelo oferece mais segurança e transparência.',
ARRAY['setta', 'comparação', 'concorrente', 'diferença'],
'{"similar_questions": ["Como a Solarprime se compara com a Setta?", "Por que não contratar a Setta?", "Quais os problemas da Setta Energia?"], "tags": ["Conheço sim o modelo da Setta, inclusive estamos migrando alguns clientes da Setta para o nosso modelo, pois eles entenderam que fazia mais sentido, nossa proposta é bem parecida, só que temos dois diferenciais em relação a eles"]}'::jsonb),

-- 11. Mercado Livre e Alta Tensão
('mercado_livre',
'Como funciona o mercado livre e alta tensão?',
'Para mercado livre e alta tensão oferecemos **35% de desconto sobre toda a conta** com economia garantida. Assim como nossos outros modelos, **sem investimentos e sem obras** montamos a usina ideal para o seu negócio. Você tem **energia limpa e barata**, transformando sua empresa em sustentável e gastando menos, além de **previsibilidade financeira** sem surpresas no final do mês. É ideal para empresas com alto consumo energético que querem reduzir significativamente seus custos operacionais e ainda contribuir com a sustentabilidade. O processo é similar ao da baixa tensão, mas com economia ainda maior devido ao volume de energia envolvido.',
ARRAY['mercado livre', 'alta tensão', 'indústria', '35% desconto'],
'{"similar_questions": ["Qual o desconto para empresas de alta tensão?", "Como funciona o mercado livre de energia?", "Vocês atendem indústrias grandes?"], "tags": ["35% de desconto sobre toda a conta: economia garantida; Sem investimentos e sem obras: montamos a usina ideal para o seu negócio; Energia limpa e barata: transforme a sua empresa em sustentável e gastando menos; Previsibilidade financeira: sem surpresas no final do mês"]}'::jsonb),

-- 12. Custo após Ganhar a Usina
('custos',
'Qual será meu custo após ganhar a usina?',
'Depois que a usina for sua, **o único custo será o aluguel do lote** hoje o aluguel do lote é de R$500,00. Mas se você desejar, pode levar a usina para outro lugar. Durante o contrato, **toda a parte de manutenção é nossa responsabilidade**. Após a usina ser sua, você fica responsável pela manutenção, mas é algo muito esporádico como contratar alguém para lavar as placas 1x no ano. É um custo muito baixo comparado à economia que você vai ter. Você terá energia praticamente gratuita por mais de 25 anos, já que os painéis solares têm garantia de performance de 25 anos!',
ARRAY['custo usina', 'manutenção', 'aluguel lote', 'após contrato'],
'{"similar_questions": ["Quando a usina for minha, vou pagar alguma coisa?", "Tem manutenção depois que a usina é minha?", "Qual o custo para manter a usina própria?"], "tags": ["Depois que a usina for sua o único custo será o aluguel do lote, hoje o aluguel do lote é de R$500,00, mas caso você deseje pode levar a usina para outro lugar"]}'::jsonb),

-- 13. Processo Comercial
('processo',
'Como é o processo comercial da Solarprime?',
'Nosso processo é bem estruturado e transparente. Primeiro, nos posicionamos como **consultores de energia** que vão analisar sua conta de luz buscando a melhor economia. Fazemos uma **análise gratuita da sua fatura** para identificar formas de economizar ainda mais. Seguimos nossa **Jornada Solarprime**: começamos com análise de viabilidade, depois aceite da proposta, envio de documentação, assinatura de contrato e você já **começa a economizar**! O legal é que conseguimos analisar se o desconto prometido por outros fornecedores está sendo aplicado corretamente já atendemos empresas que diziam ter 30% de desconto e na verdade não chegava nem a 15%!',
ARRAY['processo', 'comercial', 'venda', 'análise', 'jornada'],
'{"similar_questions": ["Como funciona a venda da Solarprime?", "Qual o passo a passo para contratar?", "Como é feita a análise da minha conta?"], "tags": ["Se posicionar como um consultor de energia que vai analisar a conta de luz buscando a melhor economia. Aqui na Solarprime nós conseguimos analisar a sua fatura de forma gratuita"]}'::jsonb),

-- 14. Instalação Própria
('instalacao',
'Vocês trabalham com instalação de usina própria no meu terreno?',
'Sim! **A instalação da própria usina é a melhor forma de economizar** na sua conta de luz. Temos soluções completas para instalação no seu terreno ou telhado. O legal da energia solar é que você só tem ganhos nesse investimento você pode trocar sua conta de energia atual pela parcela do financiamento do sistema, terminar de pagar em média em 3 anos e depois garantir **mais de 25 anos gerando sua própria energia**. Você pode ter uma economia de até 90% na sua conta de luz e fica protegido dos aumentos das bandeiras tarifárias. Seguimos nossa **Jornada Solarprime** completa: estudo personalizado, projeto técnico, implementação com excelência e suporte total. **Conseguimos elaborar um projeto gratuito** basta uma conta de luz!',
ARRAY['instalação própria', 'telhado', 'terreno', 'usina própria'],
'{"similar_questions": ["Posso instalar os painéis na minha casa?", "Vocês fazem instalação no meu telhado?", "Como funciona a usina própria no meu terreno?"], "tags": ["A instalação da própria usina é a melhor forma de economizar na sua conta de luz. O legal da energia solar é que basicamente você só tem ganhos nesse investimento"]}'::jsonb),

-- 15. Usina sem Local
('loteamento',
'E se eu quiser a usina própria mas não tenho local para instalar?',
'Perfeito! **Temos uma solução onde montamos a usina para você no loteamento de um dos nossos parceiros**. Dessa forma você não precisa se descapitalizar comprando um terreno e ainda tem uma **economia superior a 80%**. Nossos lotes ficam localizados em Goiana em um loteamento seguro. O aluguel do lote custa **R$500,00** e o lote comporta 64 placas que geram em torno de **5.500kWh mensais**. É a solução ideal para quem quer ter a própria usina solar mas não possui espaço adequado. Você tem todos os benefícios da usina própria economia máxima, independência energética e sustentabilidade sem precisar de terreno próprio!',
ARRAY['loteamento', 'sem terreno', 'aluguel lote', 'usina remota'],
'{"similar_questions": ["Posso ter usina própria sem terreno?", "Como funciona o aluguel de lote?", "Vocês tem terrenos para instalar minha usina?"], "tags": ["Nós temos uma solução onde montamos a usina para você no loteamento de um dos nossos parceiros, dessa forma você não precisa se descapitalizar e ainda tem uma economia superior a 80%"]}'::jsonb),

-- 16. Confiabilidade
('confiabilidade',
'Como posso ter certeza de que vocês são confiáveis?',
'Somos uma empresa sólida com mais de 10 anos no mercado (desde 2014). Temos **reputação ÓTIMO no Reclame AQUI** com nota 9,64/10, **100% das reclamações respondidas** e **100% dos clientes voltariam a fazer negócio**. Somos a **maior rede de franquias de energia solar do Brasil** com mais de 460 franquias, reconhecidas pela ABF como **Top 20 microfranquias** e **Franquia 4 Estrelas** pela revista Pequenas Empresas & Grandes Negócios. Temos **grandes parceiros** como VoltBras, Sicredi, Belenus, Matrix e muitos outros. Com **+ R$ 1 bilhão de faturamento** em toda a rede e **+ 245 MWp de capacidade instalada**, transformamos a vida de mais de 23 mil clientes. Nossa credibilidade é comprovada pelo mercado!',
ARRAY['confiável', 'reputação', 'credibilidade', 'reclame aqui'],
'{"similar_questions": ["A Solarprime é uma empresa séria?", "Posso confiar na Solarprime?", "Qual a reputação da Solarprime?"]}'::jsonb),

-- 17. Valorização do Imóvel
('valorizacao',
'A energia solar valoriza meu imóvel?',
'Sim! Imóveis com energia solar têm **valorização significativa** no mercado. Estudos mostram que casas e empresas com sistemas fotovoltaicos podem ter valorização de 3% a 6% no valor de venda. Além disso, se tornam **mais atrativos para locação** porque os inquilinos sabem que terão economia na conta de luz. Para empresas, demonstra **compromisso com sustentabilidade**, melhorando a imagem corporativa. Com nossa solução, você não apenas economiza mensalmente, mas também **aumenta o patrimônio** do seu imóvel. É investimento que traz retorno imediato na economia e futuro na valorização imobiliária!',
ARRAY['valorização', 'imóvel', 'patrimônio', 'investimento'],
'{"similar_questions": ["Imóvel com energia solar vale mais?", "Casa com painel solar tem valorização?", "Energia solar aumenta valor do imóvel?"], "tags": ["Transformamos soluções em energia em economia e mais qualidade de vida"]}'::jsonb),

-- 18. Energia Solar Industrial
('industrial',
'Como funciona a energia solar para indústrias?',
'Para indústrias oferecemos soluções robustas! Trabalhamos com **Mercado Livre e Alta Tensão** com até **35% de desconto sobre toda a conta**. Fazemos **estudo completo** considerando o perfil de consumo industrial, picos de demanda e sazonalidade da produção. Já executamos **grandes projetos** como a usina de 1 MW para atender 43 agências da Sicredi na região. Para indústrias, o **retorno do investimento** é ainda mais rápido devido ao alto consumo energético. **Sem investimentos e sem obras** você transforma sua empresa em sustentável, reduz custos operacionais e ainda melhora a competitividade no mercado!',
ARRAY['indústria', 'industrial', 'fábrica', 'alta tensão'],
'{"similar_questions": ["Energia solar industrial é diferente?", "Como dimensionar energia solar para fábrica?", "Indústria pode usar energia solar?"], "tags": ["35% de desconto sobre toda a conta: economia garantida; Um grande projeto que atende 43 agências da Sicredi na região"]}'::jsonb),

-- 19. String vs Microinversor
('tecnologia',
'Qual a diferença entre string e microinversor?',
'Durante nossa **elaboração de projeto de ponta a ponta**, nossa **equipe de engenharia** escolhe a melhor tecnologia para seu caso específico. Inversores string são ideais para telhados sem sombreamento e oferecem menor custo inicial. Microinversores são melhores para telhados com sombreamento parcial ou geometrias complexas, pois cada painel funciona independentemente. Trabalhamos com **equipamentos de marca própria** e grandes parceiros como VoltBras, garantindo **suporte e garantia total dos equipamentos**. Nossa experiência com mais de **245 MWp de capacidade instalada** nos permite recomendar sempre a melhor solução técnica para maximizar sua economia!',
ARRAY['inversor', 'string', 'microinversor', 'tecnologia'],
'{"similar_questions": ["Que tipo de inversor é melhor?", "String ou microinversor para energia solar?", "Como escolher o inversor certo?"], "tags": ["Elaboração de projeto de ponta a ponta pelo nosso time de engenharia, utilizando softwares próprios e integrados à Plataforma Solarprime"]}'::jsonb),

-- 20. Reduzir Conta Imediatamente
('economia_imediata',
'Como reduzir minha conta de luz imediatamente?',
'Além da energia solar, que é a **solução definitiva**, posso te dar algumas dicas imediatas! Use LED em toda iluminação, aproveite luz natural, desligue equipamentos da tomada quando não usar, ajuste temperatura do ar condicionado para 23°C, use timer em aquecedores. Mas o mais importante: **solicite nossa análise gratuita da conta** para descobrir se você já tem algum desconto que não está sendo aplicado corretamente! Já encontramos empresas pagando 30% a mais do que deveriam. Enquanto isso, posso mostrar como ter **economia garantida de 20%** desde o primeiro mês sem qualquer investimento. Que tal marcarmos uma conversa?',
ARRAY['reduzir conta', 'economia imediata', 'dicas economia', 'análise gratuita'],
'{"similar_questions": ["Quero diminuir a conta de energia agora mesmo", "Como economizar energia rapidamente?", "Dicas para reduzir consumo elétrico?"], "tags": ["conseguimos analisar a sua fatura de forma gratuita para saber se o desconto está sendo aplicado da maneira prometida"]}'::jsonb),

-- 21. Sistema Híbrido
('hibrido',
'Energia solar funciona com gerador a diesel?',
'Sim! Podemos projetar **sistemas híbridos** que integram energia solar com geradores existentes. Nossa **equipe de engenharia** desenvolve projetos que priorizam o uso da energia solar limpa e barata, acionando o gerador apenas quando necessário. Isso reduz drasticamente o **consumo de combustível** e os custos operacionais, além de diminuir ruído e emissões. Para empresas que dependem de geradores, é uma evolução natural rumo à **sustentabilidade**. **Elaboramos projeto de ponta a ponta** considerando suas necessidades específicas de backup energético. É tecnologia e economia trabalhando juntas!',
ARRAY['gerador', 'diesel', 'híbrido', 'backup'],
'{"similar_questions": ["Posso integrar solar com gerador?", "Como funciona energia solar e gerador juntos?", "Sistema híbrido solar e diesel?"], "tags": ["Elaboração de projeto de ponta a ponta pelo nosso time de engenharia"]}'::jsonb),

-- 22. Compensação Energética
('compensacao',
'Como funciona o sistema de compensação energética?',
'O sistema de compensação permite que toda energia excedente gerada pela sua usina seja **injetada na rede elétrica** da distribuidora, virando créditos energéticos que podem ser usados em até 60 meses. Durante o dia sua usina gera energia, à noite você usa os créditos acumulados. É como ter uma "conta corrente de energia"! Por isso oferecemos **previsibilidade financeira** total você sempre sabe quanto vai economizar. Nossa **análise gratuita** calcula exatamente quantos créditos sua usina vai gerar mensalmente, garantindo que o dimensionamento seja perfeito para seu perfil de consumo.',
ARRAY['compensação', 'créditos', 'rede elétrica', 'excedente'],
'{"similar_questions": ["O que é compensação de energia elétrica?", "Como ganho créditos com energia solar?", "Sistema de compensação REN 482?"], "tags": ["Previsibilidade financeira: sem surpresas no final do mês"]}'::jsonb),

-- 23. Consumo Mínimo
('consumo_minimo',
'Qual o consumo mínimo que fica na conta mesmo com energia solar?',
'Sempre permanece o **custo de disponibilidade** da distribuidora, que varia conforme o tipo de ligação: monofásica (R$ 30-50), bifásica (R$ 50-80) e trifásica (R$ 80-120) aproximadamente. Esse valor corresponde ao "aluguel" da infraestrutura elétrica e não pode ser zerado. Mas com nossos sistemas bem dimensionados, você pode ter **economia de até 90%** da sua conta total! Nossa **análise gratuita** mostra exatamente qual será sua conta mínima e máxima economia possível. É transparência total para você tomar a melhor decisão sobre seu investimento energético.',
ARRAY['consumo mínimo', 'taxa mínima', 'custo disponibilidade', 'conta zero'],
'{"similar_questions": ["Sempre vai ter uma taxa mínima na conta?", "Zero reais na conta de luz é possível?", "Custo de disponibilidade da distribuidora?"], "tags": ["Você pode ter uma economia de até 90% na sua conta de luz"]}'::jsonb),

-- 24. Geração Distribuída vs Compartilhada
('geracao',
'Como escolher entre geração distribuída e energia solar compartilhada?',
'Excelente pergunta! **Geração própria no seu telhado** oferece máxima economia (até 90%) e valorização do imóvel, ideal se você tem espaço adequado. Nossa **solução de assinatura** é perfeita se você não tem local adequado ou não quer investir nada oferecemos **20% de economia garantida** sem obras, com o **ganho da usina ao final**. Para apartamentos, nosso **aluguel de lote** proporciona **economia superior a 80%** com usina própria em local seguro. Cada situação tem sua solução ideal! Nossa **análise de viabilidade gratuita** avalia qual opção maximiza sua economia específica.',
ARRAY['geração distribuída', 'energia compartilhada', 'fazenda solar', 'GD'],
'{"similar_questions": ["Usina própria ou energia compartilhada?", "Qual é melhor: GD ou fazenda solar?", "Diferença entre geração própria e assinatura?"], "tags": ["economia superior a 80%. 20% de desconto sobre toda a conta: economia garantida. Ganho da usina: ao final do contrato, a usina é sua"]}'::jsonb),

-- 25. Interferência em Equipamentos
('interferencia',
'A energia solar interfere no WiFi ou outros equipamentos?',
'Não! Sistemas fotovoltaicos **não causam interferência** em WiFi, celular ou outros equipamentos eletrônicos quando instalados corretamente. Nossa **equipe técnica especializada** segue rigorosamente todas as normas de **instalação dos equipamentos** e aterramento adequado. Trabalhamos com **equipamentos certificados** pelo INMETRO que atendem padrões internacionais de qualidade electromagnética. Pelo contrário, muitos clientes relatam que a **economia na conta de luz** permite investir em melhores equipamentos de internet! **Garantimos um serviço de excelência técnica** em todas as instalações.',
ARRAY['interferência', 'wifi', 'equipamentos', 'ruído elétrico'],
'{"similar_questions": ["Painéis solares causam interferência?", "Energia solar afeta internet?", "Sistema fotovoltaico gera ruído elétrico?"], "tags": ["Instalação dos equipamentos e homologação do sistema, garantindo um serviço de excelência técnica do projeto"]}'::jsonb),

-- 26. Agronegócio
('agronegocio',
'Como funciona energia solar para agronegócio?',
'O agronegócio é um dos setores que **mais se beneficia** da energia solar! Propriedades rurais geralmente têm muito espaço e alta incidência solar, condições ideais para grandes sistemas. Podemos alimentar **sistemas de irrigação, estufas, granjas, ordenha** e toda infraestrutura rural. Oferecemos soluções desde **residências rurais** até **grandes instalações agroindustriais**. Nossa experiência inclui projetos para cooperativas como a **Sicredi** com 43 agências atendidas por uma única usina. **Elaboramos projetos específicos** para cada tipo de atividade rural, maximizando economia e produtividade. É sustentabilidade gerando mais competitividade no campo!',
ARRAY['agronegócio', 'rural', 'fazenda', 'agricultura'],
'{"similar_questions": ["Energia solar rural é diferente?", "Como usar energia solar no campo?", "Agronegócio pode ter energia solar?"], "tags": ["Um grande projeto que atende 43 agências da Sicredi na região"]}'::jsonb),

-- 27. Monitoramento
('monitoramento',
'Posso monitorar minha economia em tempo real?',
'Claro! Todos nossos sistemas incluem **monitoramento completo** da geração, consumo e economia. Você acompanha em tempo real **quanto sua usina está gerando**, **quanto está economizando** e **performance histórica** detalhada. Durante nosso contrato de assinatura, também fornecemos **relatórios periódicos** de desempenho. É muito gratificante ver sua **economia crescendo** todos os dias! O monitoramento também nos ajuda a garantir **máximo desempenho** do sistema e detectar rapidamente qualquer necessidade de manutenção preventiva. Transparência total no seu investimento energético!',
ARRAY['monitoramento', 'acompanhar', 'economia real', 'app'],
'{"similar_questions": ["Como acompanhar a economia da energia solar?", "Tem app para ver quanto estou economizando?", "Posso ver minha geração ao vivo?"], "tags": ["Suporte e garantia total dos serviços e equipamentos fotovoltaicos"]}'::jsonb),

-- 28. Inflação Energética
('inflacao',
'Como a inflação energética afeta minha economia solar?',
'Essa é uma das **maiores vantagens** da energia solar! Quanto mais a tarifa elétrica sobe, **maior fica sua economia absoluta**. Se hoje você economiza R$ 1.000/mês e a tarifa sobe 10%, sua economia vai para R$ 1.100/mês automaticamente! Por isso nossa **análise de viabilidade** projeta economias crescentes ao longo dos anos. Em nosso modelo de assinatura, na renovação contratual consideramos o **IPCA e não a inflação energética** se o IPCA for menor, a diferença é ganho seu! É proteção total contra os aumentos constantes das **bandeiras tarifárias** e inflação do setor elétrico.',
ARRAY['inflação energética', 'aumento tarifa', 'proteção inflação', 'IPCA'],
'{"similar_questions": ["Energia solar protege da inflação?", "Minha economia aumenta com o tempo?", "Como fica economia solar com aumento da tarifa?"], "tags": ["fica protegido dos aumentos constantes que acontecem quando é acionado bandeira amarela, vermelha"]}'::jsonb),

-- 29. Vida Útil
('vida_util',
'Qual a vida útil real dos painéis solares?',
'Os painéis solares têm **vida útil superior a 25 anos** mantendo pelo menos 80% da capacidade original. Na prática, muitos sistemas funcionam com boa eficiência por 30-35 anos! Nossa **garantia de performance de 25 anos** assegura essa durabilidade. Trabalhamos com **equipamentos de primeira linha** que seguem padrões internacionais rígidos. Após 25 anos, os painéis não "morrem" apenas têm eficiência ligeiramente reduzida. Considerando que o **retorno do investimento** acontece em 4-6 anos, você terá pelo menos 20 anos de energia praticamente gratuita! É tecnologia comprovada mundialmente.',
ARRAY['vida útil', 'durabilidade', 'quanto dura', '25 anos'],
'{"similar_questions": ["Quanto tempo duram os painéis fotovoltaicos?", "Painéis solares são duráveis?", "Preciso trocar painéis quando?"], "tags": ["garantia de performance de 25 anos"]}'::jsonb),

-- 30. Empresa em Crescimento
('crescimento',
'Como dimensionar energia solar para uma empresa que está crescendo?',
'Excelente visão estratégica! Nossa **análise de viabilidade** considera projeções de crescimento da sua empresa. Podemos dimensionar o sistema **contemplando expansão futura** ou começar com um sistema base e **ampliar posteriormente**. Para empresas em crescimento, nosso modelo de **assinatura** é ideal você pode ajustar facilmente conforme necessidade, **sem investimento adicional**. Se optar por usina própria, projetamos infraestrutura preparada para futuras ampliações. **Conseguimos elaborar projeto gratuito** considerando seus planos de expansão. É planejamento energético alinhado com visão de negócio!',
ARRAY['crescimento', 'expansão', 'empresa crescendo', 'dimensionamento'],
'{"similar_questions": ["E se minha empresa expandir?", "Como calcular energia solar para crescimento?", "Sistema solar acompanha crescimento da empresa?"], "tags": ["conseguimos elaborar um projeto gratuito para ele"]}'::jsonb),

-- 31. Regiões com Pouco Sol
('irradiacao',
'Energia solar funciona em regiões com pouco sol?',
'Sim! Energia solar funciona em **todo território nacional**. Mesmo regiões com menor irradiação solar, como Sul do país, têm **viabilidade econômica excelente**! Alemanha, com irradiação menor que qualquer região brasileira, é líder mundial em energia solar. Nossa **análise personalizada da irradiação local** usa **plataformas mais avançadas do mercado** para dimensionamento correto de cada região. O Brasil inteiro tem potencial solar superior à média mundial! Com nossa rede de **460 franquias** presentes nos **26 estados + DF**, temos experiência prática em todas as condições climáticas brasileiras.',
ARRAY['pouco sol', 'região sul', 'nublado', 'irradiação'],
'{"similar_questions": ["Sul do Brasil tem energia solar?", "Funciona energia solar em lugar nublado?", "Regiões frias podem ter energia solar?"], "tags": ["Estudo completo e personalizado da irradiação local e o dimensionamento correto do sistema fotovoltaico, por meio das plataformas mais avançadas do mercado"]}'::jsonb),

-- 32. ESG
('esg',
'Como energia solar ajuda na ESG da minha empresa?',
'Energia solar é **fundamental para estratégias ESG**! No pilar ambiental (E), reduz drasticamente emissões de CO2 e pegada de carbono. No social (S), demonstra responsabilidade com futuras gerações. Na governança (G), mostra gestão eficiente e visão de longo prazo. Com a Solarprime, sua empresa já **evita toneladas de CO2** mensalmente e pode quantificar esse impacto em relatórios ESG. Grandes investidores e clientes corporativos valorizam empresas sustentáveis. **Transformamos sua empresa em sustentável** e ainda reduzimos custos operacionais. É competitividade e responsabilidade socioambiental juntas!',
ARRAY['ESG', 'sustentabilidade', 'meio ambiente', 'CO2'],
'{"similar_questions": ["Energia solar melhora indicadores ESG?", "Como energia renovável impacta sustentabilidade corporativa?", "ESG e energia solar?"], "tags": ["8 mil toneladas de CO2 emitidos ao mês na atmosfera. Energia limpa e barata: transforme a sua empresa em sustentável e gastando menos"]}'::jsonb),

-- 33. Backup com Bateria
('backup',
'Posso ter backup de energia com sistema solar?',
'Para **backup de energia**, oferecemos sistemas híbridos com baterias que mantêm equipamentos críticos funcionando mesmo durante blecautes. Nossa **equipe de engenharia** projeta sistemas personalizados conforme suas necessidades prioritárias: geladeira, iluminação, computadores, etc. É uma evolução dos sistemas conectados à rede para **máxima segurança energética**. Sistemas com bateria têm investimento maior, mas garantem **independência energética total**. **Elaboramos projeto específico** analisando quais cargas são essenciais para sua continuidade operacional. É tranquilidade energética em qualquer situação!',
ARRAY['backup', 'bateria', 'blackout', 'falta energia'],
'{"similar_questions": ["Energia solar funciona quando falta luz?", "Como ter energia solar em blackout?", "Sistema solar com bateria?"], "tags": ["Elaboração de projeto de ponta a ponta pelo nosso time de engenharia"]}'::jsonb),

-- 34. Comparar Propostas
('comparacao',
'Como comparar propostas de energia solar de diferentes empresas?',
'Excelente pergunta! Compare: **transparência do desconto** (líquido vs bruto), **se a usina fica sua ao final**, se há **taxa de adesão ou investimento inicial**, **reputação da empresa** (Reclame Aqui, tempo de mercado), **suporte pós-venda** e **garantias oferecidas**. Cuidado com promessas irreais! Oferecemos **análise gratuita** inclusive de propostas que você já tenha, podemos mostrar os "pegadinhas" comuns do mercado. Nossa **transparência total** e **10 anos de experiência** com **reputação ÓTIMO** no Reclame Aqui garantem segurança na sua escolha. Já migramos clientes de concorrentes que prometiam muito e entregavam pouco!',
ARRAY['comparar', 'propostas', 'orçamento', 'escolher empresa'],
'{"similar_questions": ["Como escolher empresa de energia solar?", "O que analisar em orçamento solar?", "Como não cair em pegadinha de energia solar?"], "tags": ["O Reclame AQUI comprova que a Solarprime é uma confiável e que tem o melhor pós-venda do mercado fotovoltaico"]}'::jsonb),

-- 35. Impacto na Rede Elétrica
('rede_eletrica',
'Qual o impacto da energia solar na rede elétrica brasileira?',
'Energia solar **fortalece** o sistema elétrico brasileiro! A geração distribuída reduz perdas na transmissão, diminui sobrecarga nas redes e oferece energia nos horários de maior demanda (meio-dia). Com mais de **245 MWp de capacidade instalada**, contribuímos para um sistema mais **resiliente e sustentável**. Cada usina solar reduz pressão sobre hidrelétricas e termelétricas, melhorando segurança energética nacional. Por isso o governo incentiva através de regulamentações favoráveis. **Transformamos o Brasil em potência** em energia renovável, criando empregos verdes e reduzindo dependência de combustíveis fósseis!',
ARRAY['rede elétrica', 'sistema elétrico', 'impacto', 'geração distribuída'],
'{"similar_questions": ["Energia solar sobrecarrega a rede elétrica?", "Como energia solar afeta sistema elétrico?", "Energia distribuída é boa para o país?"], "tags": ["+ 245 MWp de capacidade instalada"]}'::jsonb),

-- 36. Resistência a Intempéries
('intemperies',
'Como energia solar se comporta em tempestades e ventos fortes?',
'Nossos sistemas são projetados para **resistir a condições climáticas extremas**! Seguimos rigorosamente normas técnicas de **resistência a ventos** (até 200 km/h) e granizo. A **instalação dos equipamentos** inclui fixação estrutural adequada para cada tipo de telhado e região. Trabalhamos apenas com **equipamentos certificados** que passaram por testes rigorosos de durabilidade. Nossa **garantia total dos serviços** cobre danos por intempéries durante a vigência contratual. Em mais de 10 anos e **23 mil clientes atendidos**, temos histórico comprovado de **sistemas resilientes** em todas as regiões brasileiras!',
ARRAY['tempestade', 'vento forte', 'granizo', 'intempéries'],
'{"similar_questions": ["Painéis resistem a vendaval?", "Energia solar aguenta temporal?", "Sistema solar é seguro contra intempéries?"], "tags": ["Instalação dos equipamentos e homologação do sistema, garantindo um serviço de excelência técnica do projeto"]}'::jsonb),

-- 37. Outras Soluções
('outras_solucoes',
'Vocês têm outras soluções além da energia solar?',
'Temos **soluções em energia para todos os clientes**! Além da geração de energia solar, oferecemos **Mercado Livre e Alta Tensão** (35% desconto), **Assinatura em Baixa Tensão** (20% desconto), **Mobilidade Elétrica** com nossa marca Moby, **Consórcio para Energia Solar** e **Soluções alternativas de investimentos**. Na mobilidade elétrica, você pode **investir em seu próprio carregador** e rentabilizar com total controle, ou optar pelo **carregador por assinatura** onde nós investimos no seu espaço e você ganha sem desembolsar nada. Somos uma **empresa completa de soluções energéticas**, não apenas energia solar transformamos soluções em energia em economia e mais qualidade de vida!',
ARRAY['outras soluções', 'mobilidade elétrica', 'mercado livre', 'consórcio'],
'{"similar_questions": ["Que outros serviços a Solarprime oferece?", "Vocês trabalham só com energia solar?", "Quais são todas as soluções da Solarprime?"], "tags": ["Soluções em energia para todos os clientes. Geração de Energia Solar, Mercado Livre e Alta Tensão, Assinatura em Baixa Tensão, Mobilidade Elétrica, Consórcio para Energia Solar, Solução alternativa de investimentos"]}'::jsonb),

-- 38. Análise Gratuita
('analise_gratuita',
'Como funciona a análise gratuita da conta de luz?',
'Sim! **Conseguimos analisar a sua fatura de forma gratuita** para saber se algum desconto que você já tem está sendo aplicado da maneira prometida e identificamos formas do seu negócio economizar ainda mais. É importante saber que grande parte dos empresários hoje já recebe algum tipo de desconto na conta de luz devido ao alto valor pago, mas por conta da correria não consegue acompanhar se o desconto prometido está sendo realmente aplicado. Já atendemos empresas que diziam ter desconto de 30% e na verdade não chegava nem a 15%! Nossa análise é completa e transparente você vai saber exatamente quanto pode economizar e como.',
ARRAY['análise gratuita', 'análise conta', 'verificar desconto', 'consultoria'],
'{"similar_questions": ["Vocês analisam minha conta de energia de graça?", "Como descobrir se estou pagando muito na conta de luz?", "Posso enviar minha conta para análise?"], "tags": ["Aqui na Solarprime nós conseguimos analisar a sua fatura de forma gratuita para saber se o desconto está sendo aplicado da maneira prometida e identificamos formas de seu (SEGMENTO) economizar ainda mais"]}'::jsonb),

-- 39. Jornada Solarprime
('jornada',
'Qual é a Jornada Solarprime?',
'Nossa **Jornada Solarprime** é um processo completo e estruturado. Primeiro fazemos a **Análise de viabilidade** com estudo completo e personalizado da irradiação local e dimensionamento correto usando as plataformas mais avançadas do mercado. Depois vem o **Aceite da proposta**, seguido do **Envio de documentação**. Na sequência temos a **Assinatura de contrato** e então você **Começa a economizar**! Para projetos de instalação própria, incluímos **PROJETO** (elaboração de ponta a ponta por nosso time de engenharia), **IMPLEMENTAÇÃO** (instalação dos equipamentos e homologação) e **SUPORTE** (garantia total dos serviços e equipamentos fotovoltaicos, incluindo materiais de marca própria Solarprime).',
ARRAY['jornada', 'processo', 'etapas', 'fluxo'],
'{"similar_questions": ["Como funciona o processo da Solarprime?", "Quais são as etapas do projeto solar?", "Como vocês fazem a instalação?"], "tags": ["Jornada Solarprime: Análise de viabilidade, Aceite da proposta, Envio de documentação, Assinatura de contrato, Começa a economizar!"]}'::jsonb),

-- 40. Equipamentos Próprios
('equipamentos',
'Vocês têm equipamentos próprios?',
'Sim! Com a **SPD Solar, a Solarprime passou a gerir todas as etapas do processo de importação e distribuição** de seus produtos, lançando **equipamentos de marca própria**. Temos **importação e distribuição próprias**, o que nos garante melhor qualidade, preços competitivos e disponibilidade de estoque. Trabalhamos com **grandes parceiros** como VoltBras, Sicredi, Belenus e outros fornecedores de primeira linha. Durante o contrato, oferecemos **suporte e garantia total dos serviços e equipamentos fotovoltaicos, incluindo materiais de marca própria da Solarprime**. Isso nos diferencia no mercado porque controlamos toda a cadeia de fornecimento!',
ARRAY['equipamentos próprios', 'marca própria', 'SPD Solar', 'fabricação'],
'{"similar_questions": ["A Solarprime fabrica seus próprios equipamentos?", "Que marca de painéis vocês usam?", "Vocês têm marca própria de equipamentos?"], "tags": ["Com a SPD Solar, a Solarprime passou a gerir todas as etapas do processo de importação e distribuição de seus produtos, lançando equipamentos de marca própria"]}'::jsonb),

-- 41. Transferir Usina
('transferencia',
'Posso transferir a usina para outro local depois?',
'Sim! **Caso você deseje pode levar a usina para outro lugar**. Quando a usina já for sua (após 6 anos), você tem total liberdade para transferi-la. Essa informação sobre o custo para tirar a usina de um local e levar para outro **só conseguimos repassar após a elaboração da proposta**, pois vai variar de acordo com o tamanho da usina. O legal é que você não fica "amarrado" ao local tem flexibilidade total. Enquanto isso, se preferir manter no nosso loteamento parceiro, o único custo será o aluguel do lote de R$500,00. É sua escolha: máxima economia mantendo no lote ou flexibilidade total levando para onde quiser!',
ARRAY['transferir', 'mudar usina', 'levar usina', 'outro local'],
'{"similar_questions": ["É possível mudar a usina de lugar?", "Quanto custa transferir a usina?", "Posso levar a usina se eu mudar?"], "tags": ["Essa informação a gente só consegue te repassar após a elaboração da proposta, pois vai variar de acordo com o tamanho da usina. caso você deseje pode levar a usina para outro lugar"]}'::jsonb),

-- 42. Desconto Real
('desconto_real',
'Como sei que o desconto de 20% é real?',
'Nosso desconto é **20% líquido garantido em contrato** sobre toda a conta, não apenas sobre o consumo como fazem outros fornecedores. Diferente da concorrência que promete uma coisa e entrega outra, **nós garantimos transparência total**. O desconto é aplicado em cima de toda a conta de luz, incluindo impostos e taxas. Além disso, **não levamos em consideração a iluminação pública**, o que garante em torno de mais 1,5% de desconto real. Na renovação contratual consideramos o IPCA e não a inflação energética se o IPCA for menor que a inflação energética, a diferença é ganho seu! **Tudo documentado em contrato** para sua segurança.',
ARRAY['desconto real', 'garantia desconto', '20% líquido', 'transparência'],
'{"similar_questions": ["Vocês garantem mesmo 20% de desconto?", "Como posso confiar no desconto prometido?", "O desconto é líquido ou bruto?"], "tags": ["nós oferecemos um desconto de 20% líquido garantido em contrato. Fora os 20% de desconto garantido em contrato, o desconto acaba sendo maior, pois não levamos em consideração a iluminação pública"]}'::jsonb),

-- 43. Cobertura Nacional
('cobertura',
'Vocês atendem em todo o Brasil?',
'Sim! Somos **a maior rede do Brasil em soluções de energia** com **mais de 460 franquias em todo o país**, presentes nos **26 estados + DF**. Nossa cobertura é nacional e estamos sempre expandindo. Temos franquias desde o interior até as grandes capitais, garantindo atendimento próximo e personalizado em qualquer região. Cada franquia conhece as particularidades locais, desde questões climáticas até regulamentações regionais da distribuidora de energia. Se você está em qualquer lugar do Brasil, muito provavelmente temos uma unidade Solarprime perto de você para oferecer o melhor atendimento e suporte!',
ARRAY['cobertura', 'todo brasil', 'atendimento', 'franquias'],
'{"similar_questions": ["A Solarprime atende em que regiões?", "Onde vocês trabalham?", "Tem Solarprime na minha cidade?"], "tags": ["A maior rede do Brasil em soluções de energia. Mais de 460 franquias em todo o país. Presente nos 26 estados + DF"]}'::jsonb),

-- 44. Contato
('contato',
'Como posso entrar em contato com vocês?',
'É muito fácil entrar em contato conosco! Você pode acessar nosso site **solarprime.com.br/franquia/recife-boaviagem**, nos seguir no Instagram **@solarprimeboaviagem** ou falar diretamente comigo aqui no WhatsApp mesmo. Estamos sempre disponíveis para esclarecer suas dúvidas e mostrar como você pode economizar na sua conta de energia! Você também pode enviar sua conta de luz para análise gratuita através deste canal.',
ARRAY['contato', 'whatsapp', 'instagram', 'site'],
'{"similar_questions": ["Qual o contato da Solarprime?", "Como falo com um consultor?", "Onde posso tirar dúvidas sobre energia solar?"]}'::jsonb),

-- 45. Prazo de Instalação
('prazo_instalacao',
'Quanto tempo demora para instalar a usina solar?',
'O prazo de instalação varia de acordo com o tamanho do projeto, mas geralmente a **instalação física dos equipamentos** leva entre 1 a 3 dias para residências e até 1 semana para projetos comerciais maiores. Após a instalação, temos o processo de **homologação junto à distribuidora**, que pode levar de 30 a 90 dias dependendo da região. Durante todo esse processo, **nossa equipe técnica acompanha cada etapa** e você recebe atualizações constantes. O importante é que seguimos nossa **Jornada Solarprime** com cronograma bem definido, garantindo que tudo seja feito com excelência técnica e dentro dos prazos estabelecidos.',
ARRAY['prazo', 'tempo instalação', 'quanto demora', 'cronograma'],
'{"similar_questions": ["Qual o prazo de instalação da energia solar?", "Em quanto tempo minha usina fica pronta?", "Demora muito para instalar os painéis solares?"], "tags": ["Instalação dos equipamentos e homologação do sistema, garantindo um serviço de excelência técnica do projeto"]}'::jsonb),

-- 46. Financiamento
('financiamento',
'Como funciona o financiamento da usina própria?',
'Temos várias opções de financiamento para que você possa **trocar sua conta de energia atual pela parcela do financiamento** do sistema solar. O legal é que você pode terminar de pagar em média em 3 anos e depois garantir mais de 25 anos gerando sua própria energia. Trabalhamos com diferentes linhas de crédito e podemos fazer **simulações de parcelas** personalizadas para seu perfil. Durante nossa reunião, apresento todas as opções disponíveis, incluindo financiamento bancário tradicional e linhas específicas para energia renovável. O investimento se paga com a própria economia gerada!',
ARRAY['financiamento', 'parcelamento', 'crédito', 'pagamento'],
'{"similar_questions": ["Posso financiar a energia solar?", "Quais as opções de pagamento para usina própria?", "Como pagar a usina solar parcelado?"], "tags": ["Você pode trocar sua conta de energia atual pela parcela do financiamento do seu sistema, terminar de pagar em média em 3 anos"]}'::jsonb),

-- 47. Documentação
('documentacao',
'Que documentos preciso para contratar a energia solar?',
'A documentação básica inclui **conta de luz** (fundamental para dimensionamento), **CPF/CNPJ**, **comprovante de renda** e **documentos do imóvel**. Para pessoas jurídicas, também solicitamos contrato social e documentos do representante legal. O bom é que todo o processo de **envio de documentação** faz parte da nossa Jornada Solarprime, então nossa equipe te orienta passo a passo sobre cada documento necessário. Para projetos financiados, pode haver documentação adicional do banco, mas sempre te acompanhamos em todo o processo para facilitar sua vida.',
ARRAY['documentos', 'documentação', 'contratar', 'papelada'],
'{"similar_questions": ["Quais documentos são necessários?", "O que preciso levar para assinar o contrato?", "Documentação exigida para energia solar?"], "tags": ["Envio de documentação, Assinatura de contrato"]}'::jsonb),

-- 48. Dias Nublados
('dias_nublados',
'A energia solar funciona em dias nublados e chuvosos?',
'Sim! Os painéis solares **continuam gerando energia mesmo em dias nublados e chuvosos**, embora com menor intensidade. A tecnologia fotovoltaica capta não apenas a luz solar direta, mas também a luz difusa. Nosso **estudo completo e personalizado da irradiação local** já considera todas essas variações climáticas da sua região no dimensionamento do sistema. Por isso fazemos o projeto usando **as plataformas mais avançadas do mercado**, garantindo que sua economia seja real durante todo o ano. O importante é que o sistema é dimensionado para compensar essas variações naturais, mantendo sua economia constante.',
ARRAY['nublado', 'chuva', 'inverno', 'clima'],
'{"similar_questions": ["Painéis solares geram energia com chuva?", "E quando está nublado, a energia funciona?", "Energia solar funciona no inverno?"], "tags": ["Estudo completo e personalizado da irradiação local e o dimensionamento correto do sistema fotovoltaico, por meio das plataformas mais avançadas do mercado"]}'::jsonb),

-- 49. Acompanhar Desempenho
('desempenho',
'Como posso acompanhar o desempenho da minha usina?',
'Claro! Todos os sistemas que instalamos vêm com **monitoramento em tempo real** através de aplicativos e plataformas online. Você pode acompanhar **quanto sua usina está gerando**, **quanto você está economizando** e **o desempenho histórico** do sistema. Durante o contrato, oferecemos **suporte e garantia total dos serviços e equipamentos**, incluindo acompanhamento do desempenho. É muito gratificante ver sua usina gerando energia limpa e economia real todos os dias! O monitoramento também nos ajuda a detectar qualquer necessidade de manutenção preventiva.',
ARRAY['desempenho', 'monitorar', 'aplicativo', 'acompanhar'],
'{"similar_questions": ["Tem aplicativo para monitorar a energia solar?", "Como saber quanto minha usina está gerando?", "Posso ver a produção em tempo real?"], "tags": ["Suporte e garantia total dos serviços e equipamentos fotovoltaicos"]}'::jsonb),

-- 50. Garantias
('garantias',
'Qual a garantia dos equipamentos solares?',
'Oferecemos **garantia total dos serviços e equipamentos fotovoltaicos**, incluindo **materiais de marca própria da Solarprime**. Os painéis solares têm **garantia de performance de 25 anos**, ou seja, garantimos que eles manterão pelo menos 80% da capacidade original após 25 anos. Os inversores têm garantia de 10 a 12 anos dependendo do modelo. Durante todo o contrato de assinatura, **toda a parte de manutenção é nossa responsabilidade**. Após a usina ser sua, você continua com as garantias de fábrica de todos os equipamentos. É segurança total para seu investimento!',
ARRAY['garantia', 'garantias', 'cobertura', 'proteção'],
'{"similar_questions": ["Quanto tempo de garantia tem a energia solar?", "Os painéis têm garantia?", "O que está coberto na garantia?"], "tags": ["Suporte e garantia total dos serviços e equipamentos fotovoltaicos, incluindo materiais de marca própria da Solarprime"]}'::jsonb),

-- 51. Ampliar Sistema
('ampliacao',
'Posso ampliar minha usina solar no futuro?',
'Sim, é totalmente possível ampliar seu sistema solar! Se seu consumo aumentar ou você quiser expandir para outros imóveis, podemos **dimensionar a ampliação** conforme sua nova necessidade. Para usinas próprias instaladas no seu telhado, analisamos o espaço disponível e fazemos o projeto de expansão. Para nosso modelo de assinatura, podemos ajustar o contrato ou adicionar novos lotes conforme necessário. O legal é que **conseguimos elaborar um projeto gratuito** para avaliar todas as possibilidades de ampliação. Nossa flexibilidade garante que o sistema cresça junto com suas necessidades!',
ARRAY['ampliar', 'expandir', 'aumentar', 'crescer'],
'{"similar_questions": ["É possível aumentar o sistema solar depois?", "Como expandir a usina se meu consumo aumentar?", "Posso adicionar mais painéis?"], "tags": ["conseguimos elaborar um projeto gratuito para ele"]}'::jsonb),

-- 52. Meio Ambiente
('meio_ambiente',
'Como a energia solar ajuda o meio ambiente?',
'A energia solar é uma das formas mais limpas de gerar eletricidade! Cada usina que instalamos evita a emissão de toneladas de CO2 na atmosfera. Na Solarprime, já **evitamos 8 mil toneladas de CO2 emitidas ao mês na atmosfera** com nossos projetos. Quando você escolhe energia solar, está contribuindo diretamente para um **planeta mais sustentável**. Além disso, **transformamos soluções em energia em economia e mais qualidade de vida**, criando um ciclo virtuoso onde você economiza dinheiro e ainda ajuda a preservar o meio ambiente para as próximas gerações. É investimento que faz bem para o bolso e para o planeta!',
ARRAY['meio ambiente', 'sustentável', 'CO2', 'ecológico'],
'{"similar_questions": ["Energia solar é sustentável?", "Qual o impacto ambiental da energia solar?", "Como contribuo para o planeta com energia solar?"], "tags": ["8 mil toneladas de CO2 emitidos ao mês na atmosfera. Transformamos soluções em energia em economia e mais qualidade de vida"]}'::jsonb),

-- 53. Energia à Noite
('noite',
'A energia solar funciona à noite?',
'Os painéis solares **não geram energia à noite** porque precisam da luz solar, mas isso não é problema! Durante o dia, sua usina gera energia que é **injetada na rede elétrica da distribuidora**, criando créditos energéticos. À noite, você usa esses créditos para consumir energia normalmente. É como se a rede elétrica fosse uma "bateria gigante" que armazena sua energia excedente. Por isso oferecemos **previsibilidade financeira** total todo mês você tem o desconto garantido independente de sol ou chuva, dia ou noite. O sistema funciona em perfeita harmonia com a rede elétrica tradicional!',
ARRAY['noite', 'energia noturna', 'sem sol', 'escuro'],
'{"similar_questions": ["Painéis solares geram energia de noite?", "Como ter energia solar sem sol?", "O que acontece quando escurece?"], "tags": ["Previsibilidade financeira: sem surpresas no final do mês"]}'::jsonb),

-- 54. Padrão de Energia
('padrao_energia',
'Preciso trocar meu padrão de energia para instalar solar?',
'Na maioria dos casos **não é necessário trocar o padrão de energia**. Para sistemas residenciais pequenos, geralmente só precisamos **instalar um medidor bidirecional** (que mede energia consumida e energia injetada na rede). Nossa equipe técnica faz toda a avaliação durante o estudo e te informa se há necessidade de adequações. O processo de **homologação do sistema** inclui todas as adequações necessárias junto à distribuidora. Em nosso modelo de assinatura, isso é ainda mais simples você **não precisa nem mudar a titularidade da sua conta**. Cuidamos de toda a parte técnica para você!',
ARRAY['padrão energia', 'relógio luz', 'entrada energia', 'medidor'],
'{"similar_questions": ["É necessário mudar o relógio de luz?", "Tenho que mexer na entrada de energia?", "Precisa trocar equipamentos da distribuidora?"], "tags": ["Não é necessário nem mudar a titularidade da sua conta"]}'::jsonb),

-- 55. Estrutura do Telhado
('estrutura',
'Como sei se meu telhado aguenta os painéis solares?',
'Nossa **equipe de engenharia** faz uma avaliação estrutural completa durante o estudo de viabilidade. Os painéis solares são relativamente leves (cerca de 20kg/m²) e a maioria dos telhados suporta perfeitamente. **Elaboramos projeto de ponta a ponta** considerando tipo de telha, inclinação, orientação solar e capacidade estrutural. Se houver necessidade de reforços, orientamos sobre as melhores soluções. Trabalhamos com **instalação dos equipamentos** seguindo todas as normas técnicas e de segurança. Temos experiência com todos os tipos de telhado cerâmica, metálica, fibrocimento e laje. Sua segurança é nossa prioridade!',
ARRAY['telhado', 'estrutura', 'peso', 'suporta'],
'{"similar_questions": ["Meu telhado suporta energia solar?", "Precisa reforçar o telhado?", "Painéis são muito pesados?"], "tags": ["Elaboração de projeto de ponta a ponta pelo nosso time de engenharia"]}'::jsonb),

-- 56. Payback
('payback',
'Quanto tempo leva para o sistema se pagar?',
'Para usinas próprias, o **retorno do investimento** geralmente acontece entre 4 a 6 anos, dependendo do tamanho do sistema e tarifa local. Após esse período, você tem **mais de 25 anos gerando energia praticamente gratuita**! Para nosso modelo de assinatura, **você já economiza desde o primeiro mês** sem qualquer investimento inicial. O mais legal é que você pode ter uma **economia de até 90% na sua conta de luz** e ainda fica protegido dos aumentos das bandeiras tarifárias. É um investimento que literalmente se paga sozinho e depois vira fonte de economia por décadas!',
ARRAY['payback', 'retorno investimento', 'tempo pagar', 'lucro'],
'{"similar_questions": ["Em quanto tempo recupero o investimento?", "Qual o payback da energia solar?", "Quando começo a ter lucro real?"], "tags": ["Você pode ter uma economia de até 90% na sua conta de luz e fica protegido desses inúmeros aumentos que estão ocorrendo com bandeira vermelha"]}'::jsonb),

-- 57. Venda de Energia
('venda_energia',
'Posso vender energia para a distribuidora?',
'No Brasil, o sistema atual é de **compensação energética**, não venda direta. Quando sua usina gera mais energia do que você consome, o excedente é **injetado na rede elétrica** e vira créditos que podem ser usados em até 60 meses. Esses créditos compensam seu consumo nos períodos de menor geração. É como se você "emprestasse" energia para a distribuidora e depois "pegasse de volta" quando precisar. Por isso oferecemos **previsibilidade financeira** total você sempre sabe quanto vai economizar, sem surpresas no final do mês. O foco é economia garantida, não especulação!',
ARRAY['vender energia', 'excedente', 'créditos', 'compensação'],
'{"similar_questions": ["Como funciona a venda de energia excedente?", "Ganho dinheiro vendendo energia?", "Posso lucrar com energia solar?"], "tags": ["Previsibilidade financeira: sem surpresas no final do mês"]}'::jsonb),

-- 58. Apartamento
('apartamento',
'Energia solar funciona em apartamento?',
'Para apartamentos, temos **soluções específicas**! Se o condomínio permitir, podemos instalar um sistema coletivo no telhado do prédio com rateio entre as unidades. Outra opção é nosso modelo de **aluguel de lote** onde montamos sua usina própria em nossos loteamentos parceiros você não precisa de espaço no prédio e ainda tem **economia superior a 80%**. Para contas menores (R$400 a R$4.000), oferecemos nossa modalidade com **12% a 15% de desconto**. Cada situação tem sua solução ideal na Solarprime! O importante é que você pode economizar independente do tipo de moradia.',
ARRAY['apartamento', 'prédio', 'condomínio', 'coletivo'],
'{"similar_questions": ["Posso ter energia solar morando em prédio?", "Como instalar painéis em condomínio?", "Apartamento pode ter energia solar?"], "tags": ["Temos uma solução onde montamos a usina para você no loteamento de um dos nossos parceiros, dessa forma você não precisa se descapitalizar e ainda tem uma economia superior a 80%"]}'::jsonb),

-- 59. Mudança de Endereço
('mudanca',
'O que acontece se eu me mudar de casa?',
'Temos flexibilidade total para essas situações! Se você tem **usina própria instalada**, pode levá-la para a nova residência (com custos de remoção e reinstalação). Outra opção é **transferir o sistema para o novo proprietário** mediante negociação. Para nosso modelo de assinatura, podemos **transferir o contrato** para o novo endereço se atender aos critérios, ou você pode **transferir os créditos energéticos** entre unidades consumidoras do mesmo CPF/CNPJ. E se preferir nossa solução de **aluguel de lote**, sua usina continua gerando normalmente independente de onde você more. Sempre encontramos a melhor solução!',
ARRAY['mudança', 'mudar casa', 'transferir', 'novo endereço'],
'{"similar_questions": ["Posso levar a energia solar se mudar?", "Como fica o contrato se trocar de endereço?", "Energia solar é transferível?"], "tags": ["pode levar a usina para outro lugar"]}'::jsonb),

-- 60. Manutenção
('manutencao',
'Como funciona a manutenção da energia solar?',
'A energia solar tem **manutenção muito simples**! Durante nosso contrato de assinatura, **toda a parte de manutenção é nossa responsabilidade** você não se preocupa com nada. Para usinas próprias, a manutenção é mínima basicamente **lavar as placas 1x no ano** e inspeção visual periódica dos equipamentos. É um custo muito baixo comparado à economia que você tem. Os sistemas são projetados para funcionar com mínima intervenção por mais de 25 anos. Nosso **suporte e garantia total** inclui orientações sobre manutenção preventiva e atendimento técnico sempre que necessário.',
ARRAY['manutenção', 'manter', 'limpeza', 'cuidados'],
'{"similar_questions": ["Precisa fazer manutenção nos painéis?", "Com que frequência limpar os painéis solares?", "Energia solar dá trabalho para manter?"], "tags": ["Durante o contrato toda a parte de manutenção é nossa responsabilidade, após a usina ser sua, você fica responsável pela manutenção, mas é algo muito esporádico, como contratar alguém para lavar as placas 1x no ano"]}'::jsonb),

-- 61. Fotovoltaica vs Térmica
('tipos_energia_solar',
'Qual a diferença entre energia solar fotovoltaica e térmica?',
'Trabalhamos com **energia solar fotovoltaica**, que converte luz solar diretamente em eletricidade através dos painéis. É diferente da solar térmica, que apenas aquece água. A fotovoltaica é mais versátil porque **gera eletricidade** que pode ser usada para qualquer equipamento da sua casa ou empresa iluminação, ar condicionado, geladeira, computadores, tudo! Por isso conseguimos oferecer **economia de até 90% na sua conta de luz** completa. Nossa tecnologia fotovoltaica é a mesma usada mundialmente e tem **garantia de performance de 25 anos**. É a solução mais completa e eficiente para sua independência energética!',
ARRAY['fotovoltaica', 'térmica', 'tipos', 'diferença'],
'{"similar_questions": ["Energia solar fotovoltaica é igual à térmica?", "Que tipo de energia solar vocês instalam?", "Qual a melhor energia solar?"], "tags": ["Você pode ter uma economia de até 90% na sua conta de luz"]}'::jsonb),

-- 62. Viabilidade
('viabilidade',
'Como sei se a energia solar é viável no meu caso?',
'Fazemos **análise de viabilidade gratuita** completa! Começamos analisando sua **conta de luz atual** para entender seu perfil de consumo. Depois realizamos **estudo completo e personalizado da irradiação local** e dimensionamento correto usando **as plataformas mais avançadas do mercado**. Consideramos fatores como orientação solar, sombreamentos, tipo de telhado e projeções de economia. Se já tem algum desconto, verificamos se está sendo aplicado corretamente já atendemos empresas que achavam ter 30% e na verdade tinham apenas 15%! Nossa análise mostra exatamente **quanto você pode economizar** e qual a melhor solução para seu perfil.',
ARRAY['viabilidade', 'vale a pena', 'compensa', 'estudo'],
'{"similar_questions": ["Vale a pena energia solar para mim?", "Como saber se compensa instalar?", "Vocês fazem estudo de viabilidade?"], "tags": ["Estudo completo e personalizado da irradiação local e o dimensionamento correto do sistema fotovoltaico, por meio das plataformas mais avançadas do mercado"]}'::jsonb),

-- 63. Certificações
('certificacoes',
'Quais são as certificações da Solarprime?',
'Temos todas as **certificações de qualidade** necessárias! Somos credenciados pela **ABF (Associação Brasileira de Franchising)** como **Top 20 microfranquias** e **Franquia 4 Estrelas** pela revista Pequenas Empresas & Grandes Negócios. Nossos equipamentos seguem padrões internacionais como **TIER 1**, **IEC**, **TÜV** e **ISO 9001 e 14001**. Somos associados à **ABSOLAR** (Associação Brasileira de Energia Solar Fotovoltaica) e seguimos todas as normas do **INMETRO** e **PROCEL**. Com mais de 10 anos no mercado e **reputação ÓTIMO no Reclame AQUI**, nossa credibilidade é comprovada!',
ARRAY['certificações', 'credenciamento', 'qualidade', 'selos'],
'{"similar_questions": ["A Solarprime tem certificações de qualidade?", "Vocês são credenciados?", "Que selos de qualidade vocês têm?"], "tags": ["Líder no segmento fotovoltaico com reputação excepcional no Reclame AQUI"]}'::jsonb),

-- 64. Pós-Venda
('pos_venda',
'Como é o pós-venda da Solarprime?',
'Nosso pós-venda é reconhecido como **o melhor do mercado fotovoltaico**! Temos **100% das reclamações respondidas** no Reclame AQUI e **100% dos clientes voltariam a fazer negócio** conosco. Oferecemos **suporte e garantia total dos serviços e equipamentos**, incluindo monitoramento, manutenção e assistência técnica. Nossa equipe acompanha o desempenho da sua usina e está sempre disponível para esclarecer dúvidas. Com mais de **460 franquias** em todo Brasil, você sempre terá atendimento próximo. **Transformamos soluções em energia em economia e mais qualidade de vida** também no relacionamento pós-venda!',
ARRAY['pós-venda', 'suporte', 'atendimento', 'assistência'],
'{"similar_questions": ["Vocês dão suporte depois da instalação?", "Como é o atendimento pós-venda?", "Posso contar com vocês após a compra?"], "tags": ["O Reclame AQUI comprova que a Solarprime é uma confiável e que tem o melhor pós-venda do mercado fotovoltaico, atendendo a todas as reclamações e alcançando alto índice de aprovação dos consumidores"]}'::jsonb),

-- 65. Leonardo Ferraz
('contato',
'Quem é o Leonardo Ferraz?',
'Leonardo Ferraz é sócio da Solarprime Boa Viagem! Para conhecer mais sobre nosso trabalho e ver cases de sucesso, recomendo que você siga nosso Instagram **@solarprimeboaviagem** onde compartilhamos sempre novidades e projetos realizados. Qualquer dúvida sobre nossas soluções energéticas, posso te ajudar diretamente aqui mesmo!',
ARRAY['leonardo ferraz', 'sócio', 'responsável', 'dono'],
'{"similar_questions": ["Posso falar com o Leonardo Ferraz?", "O Leonardo trabalha aí?", "Quem é o responsável pela Solarprime em Recife?"], "tags": ["Leonardo Ferraz, Sócio Solarprime Boa Viagem, instagram.com/solarprimeboaviagem"]}'::jsonb);

-- Criar índice para melhorar performance de busca
CREATE INDEX IF NOT EXISTS idx_knowledge_base_question_gin ON knowledge_base USING gin(to_tsvector('portuguese', question));
CREATE INDEX IF NOT EXISTS idx_knowledge_base_answer_gin ON knowledge_base USING gin(to_tsvector('portuguese', answer));

-- Atualizar timestamps
UPDATE knowledge_base SET updated_at = CURRENT_TIMESTAMP WHERE created_at IS NOT NULL;

-- Contar registros inseridos
SELECT COUNT(*) as total_conhecimentos FROM knowledge_base;