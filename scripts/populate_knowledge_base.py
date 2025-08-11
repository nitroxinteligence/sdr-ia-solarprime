#!/usr/bin/env python3
"""
Script para popular a tabela knowledge_base no Supabase
Execute este script para adicionar documentos à base de conhecimento
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from app.integrations.supabase_client import supabase_client
from loguru import logger

# Documentos para adicionar à knowledge base
KNOWLEDGE_DOCUMENTS = [
    {
        "title": "Informações da Empresa Solar Prime",
        "content": """A Solar Prime é líder em soluções de energia solar fotovoltaica em Pernambuco, com mais de 5 anos de experiência no mercado. Nossa missão é democratizar o acesso à energia solar, proporcionando economia e sustentabilidade para residências e empresas. Oferecemos economia garantida de até 95% na conta de luz, instalação em até 30 dias, 25 anos de garantia nos painéis solares, 10 anos de garantia no inversor, monitoramento 24/7 via aplicativo, equipe técnica certificada, mais de 2000 clientes satisfeitos, nota 4.9 no Google e parceria com as melhores marcas do mercado.""",
        "category": "empresa",
        "tags": ["solar prime", "empresa", "sobre", "informações", "missão"]
    },
    {
        "title": "Processo de Instalação Solar",
        "content": """Nosso processo de instalação é simples e eficiente: 1) Análise da conta de luz para dimensionamento correto, 2) Projeto personalizado de acordo com suas necessidades, 3) Aprovação na concessionária local (cuidamos de toda burocracia), 4) Instalação profissional em até 2 dias, 5) Ativação e monitoramento do sistema. Todo o processo leva em média 30 dias do contrato até a geração de energia.""",
        "category": "instalacao",
        "tags": ["instalação", "processo", "etapas", "prazo"]
    },
    {
        "title": "Formas de Pagamento",
        "content": """Oferecemos diversas formas de pagamento para facilitar seu investimento em energia solar: À vista com 10% de desconto especial, Parcelamento em até 84x sem entrada, Financiamento bancário com carência de 6 meses, Modelo de assinatura mensal (você paga apenas pela energia gerada). Temos sempre uma opção que cabe no seu bolso!""",
        "category": "financeiro",
        "tags": ["pagamento", "financiamento", "parcelamento", "valores"]
    },
    {
        "title": "Kit Residencial Básico",
        "content": """Para contas de R$ 200 a R$ 400: Sistema de 2-3 kWp com 4 a 6 painéis de 550W, inversor de 3kW, produção média de 350 kWh/mês. Investimento a partir de R$ 8.990 com payback de 4 anos. Ideal para casas pequenas e médias.""",
        "category": "produtos",
        "tags": ["kit", "residencial", "básico", "produto", "3kwp"]
    },
    {
        "title": "Kit Residencial Intermediário",
        "content": """Para contas de R$ 400 a R$ 700: Sistema de 4-5 kWp com 8 a 10 painéis de 550W, inversor de 5kW, produção média de 600 kWh/mês. Investimento a partir de R$ 14.990 com excelente custo-benefício. Perfeito para famílias de 3-4 pessoas.""",
        "category": "produtos",
        "tags": ["kit", "residencial", "intermediário", "produto", "5kwp"]
    },
    {
        "title": "Objeção: É muito caro",
        "content": """Entendo sua preocupação! Mas veja só: não é um gasto, é um investimento. Você para de pagar conta de luz e em 4 anos o sistema se paga. Depois disso, são mais 21 anos de energia grátis! Além disso, temos parcelamento em até 84x, que fica menor que sua conta atual.""",
        "category": "objecoes",
        "tags": ["objeção", "caro", "preço", "valor", "investimento"]
    },
    {
        "title": "Objeção: Preciso pensar",
        "content": """Claro, é uma decisão importante! Enquanto você pensa, está perdendo dinheiro todo mês com a conta de luz. Que tal agendarmos uma visita sem compromisso para você tirar todas as dúvidas? Assim você pode decidir com mais segurança.""",
        "category": "objecoes",
        "tags": ["objeção", "pensar", "decidir", "dúvida"]
    },
    {
        "title": "Benefícios da Energia Solar",
        "content": """Economia de até 95% na conta de luz, proteção contra aumentos tarifários (que sobem 10% ao ano), valorização do imóvel em até 10%, contribuição para o meio ambiente, independência energética, retorno garantido do investimento, incentivos fiscais e créditos de carbono.""",
        "category": "beneficios",
        "tags": ["benefícios", "vantagens", "economia", "sustentabilidade"]
    },
    {
        "title": "Garantias Solar Prime",
        "content": """25 anos de garantia de produção nos painéis (80% da capacidade), 10 anos de garantia no inversor, 5 anos de garantia na instalação, 15 anos de garantia nas estruturas de fixação, 1 ano de manutenção preventiva gratuita, suporte técnico vitalício.""",
        "category": "garantias",
        "tags": ["garantia", "suporte", "manutenção", "assistência"]
    },
    {
        "title": "Como Funciona o Sistema Solar",
        "content": """Os painéis solares captam a luz do sol e geram energia elétrica em corrente contínua (CC). O inversor converte essa energia para corrente alternada (CA), compatível com sua casa. A energia gerada é consumida instantaneamente e o excesso vai para a rede, gerando créditos. À noite ou em dias de baixa produção, você usa os créditos acumulados.""",
        "category": "tecnologia",
        "tags": ["funcionamento", "tecnologia", "como funciona", "sistema"]
    }
]

def populate_knowledge_base():
    """Popula a knowledge base no Supabase"""
    try:
        logger.info("🚀 Iniciando população da knowledge base...")
        
        # Verificar documentos existentes
        existing = supabase_client.client.table("knowledge_base").select("title").execute()
        existing_titles = [doc["title"] for doc in existing.data] if existing.data else []
        
        logger.info(f"📊 Documentos existentes: {len(existing_titles)}")
        
        inserted = 0
        skipped = 0
        
        for doc in KNOWLEDGE_DOCUMENTS:
            try:
                # Verificar se já existe
                if doc["title"] in existing_titles:
                    logger.warning(f"⏭️  Pulando documento existente: {doc['title']}")
                    skipped += 1
                    continue
                
                # Adicionar timestamps
                doc["created_at"] = datetime.now().isoformat()
                doc["updated_at"] = datetime.now().isoformat()
                
                # Inserir no Supabase
                result = supabase_client.client.table("knowledge_base").insert(doc).execute()
                
                if result.data:
                    logger.success(f"✅ Documento inserido: {doc['title']}")
                    inserted += 1
                else:
                    logger.error(f"❌ Erro ao inserir: {doc['title']}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar documento {doc['title']}: {e}")
                continue
        
        # Resumo final
        logger.info("=" * 50)
        logger.success(f"✅ População concluída!")
        logger.info(f"📊 Documentos inseridos: {inserted}")
        logger.info(f"⏭️  Documentos pulados: {skipped}")
        logger.info(f"📚 Total na base: {len(existing_titles) + inserted}")
        
        # Verificar categorias
        categories = supabase_client.client.table("knowledge_base").select("category").execute()
        if categories.data:
            unique_categories = set(doc["category"] for doc in categories.data)
            logger.info(f"📁 Categorias disponíveis: {', '.join(unique_categories)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        return False

if __name__ == "__main__":
    # Verificar se as variáveis de ambiente estão configuradas
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
        logger.error("❌ Configure SUPABASE_URL e SUPABASE_SERVICE_KEY no arquivo .env")
        sys.exit(1)
    
    # Popular knowledge base
    success = populate_knowledge_base()
    
    if success:
        logger.success("🎉 Script executado com sucesso!")
    else:
        logger.error("❌ Script falhou!")
        sys.exit(1)