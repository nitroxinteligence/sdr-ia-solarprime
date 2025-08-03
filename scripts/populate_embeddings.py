"""
Script para popular embeddings da knowledge base
Sincroniza dados de energia solar com vector search
"""
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from app.services.embeddings_manager import embeddings_manager
from app.integrations.supabase_client import supabase_client


# Conhecimento sobre energia solar para popular a base
SOLAR_KNOWLEDGE = [
    {
        "title": "Como funciona a energia solar fotovoltaica",
        "content": """
        A energia solar fotovoltaica funciona através de painéis solares que convertem 
        a luz do sol diretamente em eletricidade. Os painéis são compostos por células 
        fotovoltaicas feitas de silício que, quando expostas à luz solar, geram corrente 
        elétrica contínua (CC). Um inversor solar converte essa corrente contínua em 
        corrente alternada (CA), que é o tipo de eletricidade usada em residências e 
        empresas. O sistema é conectado ao quadro elétrico do imóvel e a energia gerada 
        pode ser consumida imediatamente ou injetada na rede elétrica, gerando créditos 
        energéticos através do sistema de compensação.
        """,
        "category": "TECNOLOGIA",
        "tags": ["funcionamento", "paineis", "inversor", "fotovoltaica"],
        "priority": 10
    },
    {
        "title": "Economia com energia solar",
        "content": """
        A energia solar pode gerar economia de até 95% na conta de luz. Para empresas 
        com contas acima de R$ 4.000, o retorno do investimento (payback) ocorre entre 
        3 a 5 anos. Após esse período, a energia é praticamente gratuita por mais de 
        20 anos. O sistema de compensação de energia permite acumular créditos quando 
        a geração é maior que o consumo, utilizando esses créditos em períodos de menor 
        geração ou à noite. Além disso, a energia solar protege contra aumentos tarifários 
        futuros e valoriza o imóvel em até 10%.
        """,
        "category": "ECONOMIA",
        "tags": ["economia", "payback", "ROI", "investimento", "conta de luz"],
        "priority": 10
    },
    {
        "title": "Requisitos para instalação solar",
        "content": """
        Para instalar energia solar, é necessário ter: 1) Área disponível no telhado ou 
        solo (aproximadamente 7m² por kWp); 2) Telhado em boas condições estruturais; 
        3) Baixo sombreamento na área de instalação; 4) Conta de luz com histórico de 
        consumo; 5) Para empresas, recomenda-se conta acima de R$ 2.000 para melhor 
        viabilidade. O processo inclui visita técnica, projeto personalizado, aprovação 
        na concessionária, instalação (2-5 dias) e homologação do sistema.
        """,
        "category": "INSTALACAO",
        "tags": ["requisitos", "instalacao", "telhado", "area", "viabilidade"],
        "priority": 9
    },
    {
        "title": "Manutenção de sistemas solares",
        "content": """
        Sistemas solares requerem manutenção mínima. A limpeza dos painéis deve ser 
        feita a cada 6-12 meses, dependendo da incidência de poeira e poluição. 
        A chuva ajuda na limpeza natural. Inspeções anuais verificam conexões, 
        estruturas e desempenho. Os inversores têm garantia de 5-10 anos e painéis 
        de 25-30 anos, com vida útil superior a 30 anos. O monitoramento remoto 
        permite acompanhar a geração em tempo real e identificar qualquer anomalia 
        rapidamente. Custo de manutenção é inferior a 1% do valor do sistema por ano.
        """,
        "category": "MANUTENCAO",
        "tags": ["manutencao", "limpeza", "garantia", "monitoramento", "durabilidade"],
        "priority": 8
    },
    {
        "title": "Benefícios ambientais da energia solar",
        "content": """
        A energia solar é 100% limpa e renovável, não emitindo CO2 durante a geração. 
        Um sistema residencial médio evita a emissão de 1,3 toneladas de CO2 por ano, 
        equivalente ao plantio de 7 árvores anualmente. Para empresas, a pegada de 
        carbono pode ser reduzida significativamente, contribuindo para metas ESG e 
        certificações ambientais. A energia solar também não consome água, não gera 
        ruído e não produz resíduos durante operação. Painéis solares são 95% recicláveis 
        ao final de sua vida útil.
        """,
        "category": "SUSTENTABILIDADE",
        "tags": ["meio ambiente", "sustentabilidade", "CO2", "ESG", "renovavel"],
        "priority": 9
    },
    {
        "title": "Financiamento para energia solar",
        "content": """
        Existem diversas linhas de financiamento para energia solar com taxas atrativas. 
        Bancos oferecem financiamento em até 72 meses, com carência de até 6 meses. 
        Algumas modalidades permitem que a parcela seja menor que a economia na conta 
        de luz, gerando fluxo de caixa positivo desde o primeiro mês. Para empresas, 
        há linhas específicas do BNDES e outros bancos de desenvolvimento com taxas 
        subsidiadas. Também é possível fazer leasing ou aluguel de sistemas solares 
        sem investimento inicial.
        """,
        "category": "FINANCEIRO",
        "tags": ["financiamento", "credito", "banco", "BNDES", "leasing"],
        "priority": 9
    },
    {
        "title": "Energia solar em dias nublados",
        "content": """
        Painéis solares funcionam mesmo em dias nublados, pois captam radiação difusa. 
        A eficiência pode cair para 10-25% da capacidade em dias muito nublados, mas 
        ainda há geração. O sistema de compensação de energia equilibra isso: créditos 
        acumulados em dias ensolarados compensam a menor geração em dias nublados. 
        Em Pernambuco, temos média de 5,5 horas de sol pleno por dia, uma das melhores 
        do Brasil. Mesmo considerando variações climáticas, a média anual garante 
        excelente retorno do investimento.
        """,
        "category": "TECNOLOGIA",
        "tags": ["nublado", "chuva", "radiacao", "geracao", "clima"],
        "priority": 8
    },
    {
        "title": "Valorização do imóvel com energia solar",
        "content": """
        Imóveis com energia solar valorizam entre 4% a 10% segundo estudos do mercado 
        imobiliário. A valorização ocorre pela redução de custos operacionais, 
        modernização do imóvel e apelo sustentável. Para empresas, além da valorização 
        patrimonial, há benefícios fiscais como depreciação acelerada e isenção de 
        ICMS sobre a energia gerada. Compradores e locatários preferem imóveis com 
        energia solar pela economia garantida e compromisso ambiental.
        """,
        "category": "INVESTIMENTO",
        "tags": ["valorizacao", "imovel", "patrimonio", "mercado", "beneficios"],
        "priority": 8
    },
    {
        "title": "Sistema on-grid vs off-grid",
        "content": """
        Sistema on-grid (conectado à rede) é o mais comum, permitindo usar a rede 
        elétrica como 'bateria virtual' através dos créditos de energia. Não precisa 
        de baterias físicas, é mais barato e tem retorno mais rápido. Sistema off-grid 
        (isolado) usa baterias para armazenar energia, ideal para locais sem rede 
        elétrica. É mais caro devido às baterias, mas oferece independência total. 
        Sistemas híbridos combinam ambos, oferecendo backup em caso de falta de energia. 
        Para empresas urbanas, on-grid é mais vantajoso economicamente.
        """,
        "category": "TECNOLOGIA",
        "tags": ["on-grid", "off-grid", "hibrido", "bateria", "rede"],
        "priority": 7
    },
    {
        "title": "Monitoramento de geração solar",
        "content": """
        Sistemas modernos incluem monitoramento online 24/7 via aplicativo ou computador. 
        É possível acompanhar: geração em tempo real, histórico de produção, economia 
        acumulada, CO2 evitado, alertas de manutenção e comparação com metas. 
        O monitoramento identifica problemas rapidamente, como painéis sujos ou 
        falhas no inversor. Dados são armazenados na nuvem com relatórios mensais 
        automáticos. Para empresas, o monitoramento facilita gestão energética e 
        relatórios de sustentabilidade.
        """,
        "category": "TECNOLOGIA",
        "tags": ["monitoramento", "app", "online", "gestao", "relatorios"],
        "priority": 7
    }
]

FAQS = [
    {
        "title": "Quanto tempo dura um sistema solar?",
        "content": "Painéis solares têm vida útil superior a 30 anos, com garantia de performance de 25 anos (80% da capacidade). Inversores duram 10-15 anos com garantia de 5-10 anos.",
        "category": "FAQ",
        "tags": ["durabilidade", "garantia", "vida util"]
    },
    {
        "title": "Preciso de bateria para ter energia solar?",
        "content": "Não. Sistemas on-grid (conectados à rede) não precisam de bateria. A rede elétrica funciona como bateria virtual através do sistema de compensação de créditos.",
        "category": "FAQ",
        "tags": ["bateria", "on-grid", "creditos"]
    },
    {
        "title": "E se eu mudar de imóvel?",
        "content": "O sistema pode ser removido e reinstalado no novo local ou você pode vender o imóvel com o sistema, agregando valor. Créditos acumulados podem ser transferidos para outro imóvel no mesmo CPF/CNPJ e concessionária.",
        "category": "FAQ",
        "tags": ["mudanca", "transferencia", "creditos"]
    },
    {
        "title": "Quanto tempo leva a instalação?",
        "content": "A instalação física leva de 2 a 5 dias para residências e 5 a 15 dias para empresas, dependendo do tamanho. O processo completo com projeto e homologação leva 30-60 dias.",
        "category": "FAQ",
        "tags": ["instalacao", "prazo", "tempo"]
    },
    {
        "title": "Posso zerar minha conta de luz?",
        "content": "A conta nunca chega a zero devido à taxa mínima da concessionária (custo de disponibilidade). Mas é possível reduzir até 95% do valor, pagando apenas a taxa mínima.",
        "category": "FAQ",
        "tags": ["conta", "economia", "taxa minima"]
    }
]


async def populate_knowledge_base():
    """Popula a knowledge_base com dados de energia solar"""
    try:
        logger.info("Iniciando população da knowledge_base...")
        
        # Inserir conhecimento principal
        for item in SOLAR_KNOWLEDGE:
            result = supabase_client.client.table('knowledge_base').insert({
                "title": item["title"],
                "content": item["content"],
                "category": item["category"],
                "tags": item["tags"],
                "priority": item.get("priority", 5),
                "source": "Solar Prime Knowledge",
                "is_active": True
            }).execute()
            
            if result.data:
                logger.info(f"✅ Inserido: {item['title']}")
        
        # Inserir FAQs
        for faq in FAQS:
            result = await supabase_client.client.table('knowledge_base').insert({
                "title": faq["title"],
                "content": faq["content"],
                "category": "FAQ",
                "tags": faq["tags"],
                "priority": 6,
                "source": "Solar Prime FAQ",
                "is_active": True
            }).execute()
            
            if result.data:
                logger.info(f"✅ FAQ inserido: {faq['title']}")
        
        logger.info("Knowledge base populada com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao popular knowledge_base: {e}")
        return False


async def create_embeddings():
    """Cria embeddings para todos os itens da knowledge_base"""
    try:
        logger.info("Criando embeddings para knowledge_base...")
        
        # Sincronizar knowledge_base com embeddings
        await embeddings_manager.populate_knowledge_base()
        
        logger.info("Embeddings criados com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar embeddings: {e}")
        return False


async def test_vector_search():
    """Testa a busca vetorial"""
    try:
        logger.info("\n=== Testando busca vetorial ===")
        
        test_queries = [
            "quanto custa energia solar?",
            "como funciona o sistema?",
            "preciso de bateria?",
            "quanto tempo dura?",
            "economia na conta de luz"
        ]
        
        for query in test_queries:
            logger.info(f"\n📝 Query: {query}")
            
            # Busca vetorial
            results = await embeddings_manager.search_similar(
                query=query,
                match_count=3,
                content_type='KNOWLEDGE_BASE'
            )
            
            if results:
                for i, result in enumerate(results, 1):
                    logger.info(f"  {i}. {result['content'][:100]}... (score: {result['similarity']:.3f})")
            else:
                logger.warning("  Nenhum resultado encontrado")
        
        # Teste de busca híbrida
        logger.info("\n=== Testando busca híbrida ===")
        
        hybrid_results = await embeddings_manager.hybrid_search(
            query="financiamento para empresa instalar energia solar",
            match_count=3
        )
        
        if hybrid_results:
            for i, result in enumerate(hybrid_results, 1):
                logger.info(f"  {i}. {result['content'][:150]}... (score: {result['score']:.3f})")
        
        # Teste de contexto RAG
        logger.info("\n=== Testando geração de contexto RAG ===")
        
        context = await embeddings_manager.get_context_for_query(
            query="empresa com conta de 5000 reais quer saber sobre energia solar",
            max_context_length=1500
        )
        
        if context:
            logger.info(f"Contexto gerado ({len(context)} caracteres):")
            logger.info(context[:500] + "...")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro no teste de busca vetorial: {e}")
        return False


async def main():
    """Função principal"""
    try:
        logger.info("🚀 Iniciando população de embeddings...")
        
        # 1. Popular knowledge_base
        success = await populate_knowledge_base()
        if not success:
            logger.error("Falha ao popular knowledge_base")
            return
        
        # 2. Criar embeddings
        success = await create_embeddings()
        if not success:
            logger.error("Falha ao criar embeddings")
            return
        
        # 3. Testar busca vetorial
        success = await test_vector_search()
        if not success:
            logger.error("Falha nos testes de busca")
            return
        
        logger.info("\n✅ Processo concluído com sucesso!")
        logger.info("📊 Estatísticas:")
        logger.info(f"  - {len(SOLAR_KNOWLEDGE)} documentos de conhecimento")
        logger.info(f"  - {len(FAQS)} FAQs")
        logger.info(f"  - Total: {len(SOLAR_KNOWLEDGE) + len(FAQS)} itens na knowledge_base")
        logger.info("\n🎯 Sistema RAG pronto para uso!")
        
    except Exception as e:
        logger.error(f"Erro no processo principal: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())