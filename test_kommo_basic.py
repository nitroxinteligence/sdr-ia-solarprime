#!/usr/bin/env python3
"""
Teste Básico - Criar Lead Simples no Kommo
==========================================
Teste mínimo para verificar criação de lead
"""

import asyncio
import sys
from loguru import logger
import os

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from services.kommo_service import KommoService
from config.config import get_config


async def test_basic_lead():
    """Cria um lead básico sem campos customizados complexos"""
    logger.info("=" * 80)
    logger.info("🧪 TESTE BÁSICO - CRIAR LEAD SIMPLES")
    logger.info("=" * 80)
    
    service = KommoService()
    
    # 1. Testar conexão
    logger.info("\n1️⃣ Testando conexão...")
    try:
        pipelines = await service.get_pipelines()
        logger.info(f"✅ Conectado! {len(pipelines)} pipelines encontrados")
        
        # Pegar o primeiro pipeline
        if pipelines:
            pipeline = pipelines[0]
            pipeline_id = pipeline["id"]
            logger.info(f"   Usando pipeline: {pipeline['name']} (ID: {pipeline_id})")
            
            # Listar estágios
            statuses = pipeline.get("_embedded", {}).get("statuses", [])
            if statuses:
                first_status = statuses[0]
                logger.info(f"   Primeiro estágio: {first_status['name']} (ID: {first_status['id']})")
                
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {str(e)}")
        return
    
    # 2. Criar lead básico
    logger.info("\n2️⃣ Criando lead básico...")
    
    # Lead SUPER simples
    lead_payload = [{
        "name": "Teste Básico API",
        "pipeline_id": pipeline_id,
        "status_id": first_status["id"]
    }]
    
    try:
        response = await service._make_request("POST", "/leads", lead_payload)
        
        if "_embedded" in response and "leads" in response["_embedded"]:
            lead = response["_embedded"]["leads"][0]
            logger.info(f"✅ Lead criado com sucesso!")
            logger.info(f"   ID: {lead['id']}")
            logger.info(f"   Nome: {lead['name']}")
            logger.info(f"   Pipeline: {lead['pipeline_id']}")
            logger.info(f"   Status: {lead['status_id']}")
            
            # 3. Adicionar nota
            logger.info("\n3️⃣ Adicionando nota...")
            note_payload = [{
                "entity_type": "leads",
                "entity_id": lead['id'],
                "note_type": "common",
                "params": {
                    "text": "Lead criado via API de teste\nTeste básico funcionando!"
                }
            }]
            
            await service._make_request("POST", "/leads/notes", note_payload)
            logger.info("✅ Nota adicionada!")
            
            # 4. Adicionar tag
            logger.info("\n4️⃣ Adicionando tag...")
            update_payload = {
                "id": lead['id'],
                "_embedded": {
                    "tags": [
                        {"name": "Teste API"},
                        {"name": "Pode Deletar"}
                    ]
                }
            }
            
            await service._make_request("PATCH", f"/leads/{lead['id']}", update_payload)
            logger.info("✅ Tags adicionadas!")
            
            logger.info("\n" + "=" * 80)
            logger.info("🎉 TESTE BÁSICO CONCLUÍDO COM SUCESSO!")
            logger.info(f"   Lead ID: {lead['id']} criado e pode ser deletado")
            logger.info("=" * 80)
            
        else:
            logger.error("❌ Resposta inesperada da API")
            logger.info(f"   Resposta: {response}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar lead: {str(e)}")


async def main():
    """Função principal"""
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    # Carregar .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar token
    token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
    if not token:
        logger.error("❌ KOMMO_LONG_LIVED_TOKEN não encontrado no .env!")
        return
    
    logger.info(f"✅ Token encontrado: {token[:30]}...")
    
    # Executar teste
    await test_basic_lead()


if __name__ == "__main__":
    asyncio.run(main())