#!/usr/bin/env python3
"""
Teste de Pipeline Correto - Kommo CRM
=====================================
Verifica se está usando o pipeline correto do .env
"""

import asyncio
import sys
from datetime import datetime
from loguru import logger
import os
import random

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from services.kommo_service import KommoService
from config.config import get_config


async def test_pipeline():
    """Teste do pipeline correto"""
    logger.info("=" * 80)
    logger.info("🎯 TESTE DE PIPELINE CORRETO - KOMMO CRM")
    logger.info("=" * 80)
    
    service = KommoService()
    config = get_config()
    
    # Pipeline esperado do .env
    expected_pipeline_id = config.kommo.pipeline_id
    logger.info(f"\n📋 Pipeline configurado no .env: {expected_pipeline_id}")
    logger.info("   Nome esperado: Funil IA SDR")
    
    # 1. Verificar configuração
    logger.info("\n1️⃣ Verificando configuração do serviço...")
    
    pipeline_config = await service.get_pipeline_configuration()
    logger.info(f"   Pipeline no serviço: {pipeline_config.get('pipeline_id')}")
    
    if pipeline_config.get('pipeline_id') != expected_pipeline_id:
        logger.error(f"❌ Pipeline incorreto! Esperado: {expected_pipeline_id}, Atual: {pipeline_config.get('pipeline_id')}")
        return False
    
    # 2. Buscar detalhes do pipeline
    logger.info("\n2️⃣ Buscando detalhes do pipeline...")
    
    try:
        response = await service._make_request(
            "GET",
            f"/leads/pipelines/{expected_pipeline_id}",
            params={"with": "statuses"}
        )
        
        pipeline_name = response.get("name", "N/A")
        logger.info(f"✅ Pipeline encontrado: {pipeline_name}")
        
        if "IA SDR" not in pipeline_name:
            logger.warning(f"⚠️  Nome do pipeline não contém 'IA SDR': {pipeline_name}")
        
        # Listar estágios
        statuses = response.get("_embedded", {}).get("statuses", [])
        logger.info(f"\n📊 Estágios do pipeline ({len(statuses)} total):")
        
        for status in statuses[:5]:  # Mostrar apenas 5 primeiros
            logger.info(f"   - {status['name']} (ID: {status['id']})")
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar pipeline: {str(e)}")
        return False
    
    # 3. Criar lead de teste no pipeline correto
    logger.info("\n3️⃣ Criando lead de teste...")
    
    test_id = random.randint(1000, 9999)
    lead_payload = [{
        "name": f"Teste Pipeline #{test_id}",
        "price": 1000,
        "pipeline_id": expected_pipeline_id  # Forçar pipeline correto
    }]
    
    try:
        response = await service._make_request("POST", "/leads", lead_payload)
        
        if "_embedded" in response and "leads" in response["_embedded"]:
            lead = response["_embedded"]["leads"][0]
            lead_id = lead['id']
            
            logger.info(f"✅ Lead criado com sucesso!")
            logger.info(f"   ID: {lead_id}")
            
            # Buscar detalhes completos do lead
            lead_details = await service.get_lead(lead_id)
            if lead_details:
                created_pipeline_id = lead_details.get('pipeline_id')
                logger.info(f"   Nome: {lead_details.get('name', 'N/A')}")
                logger.info(f"   Pipeline ID: {created_pipeline_id}")
            else:
                logger.error("❌ Erro ao buscar detalhes do lead")
                return False
            
            # Verificar se foi criado no pipeline correto
            if created_pipeline_id == expected_pipeline_id:
                logger.info(f"✅ SUCESSO! Lead criado no pipeline correto: Funil IA SDR ({expected_pipeline_id})")
                
                # Adicionar nota confirmando
                note_payload = [{
                    "entity_type": "leads",
                    "entity_id": lead_id,
                    "note_type": "common",
                    "params": {
                        "text": f"""✅ Lead criado no pipeline correto!
                        
Pipeline: Funil IA SDR
Pipeline ID: {expected_pipeline_id}
Teste ID: #{test_id}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Este lead pode ser deletado."""
                    }
                }]
                
                await service._make_request("POST", "/leads/notes", note_payload)
                logger.info("✅ Nota de confirmação adicionada!")
                
                # Adicionar tag
                update_payload = {
                    "id": lead_id,
                    "_embedded": {
                        "tags": [
                            {"name": "Teste Pipeline"},
                            {"name": "IA SDR"},
                            {"name": f"ID {test_id}"},
                            {"name": "Pode Deletar"}
                        ]
                    }
                }
                
                await service._make_request("PATCH", f"/leads/{lead_id}", update_payload)
                logger.info("✅ Tags adicionadas!")
                
                # Resumo final
                logger.info("\n" + "=" * 80)
                logger.info("🎉 PIPELINE CORRETO CONFIRMADO!")
                logger.info("=" * 80)
                logger.info(f"✅ Pipeline ID: {expected_pipeline_id}")
                logger.info(f"✅ Pipeline Nome: Funil IA SDR")
                logger.info(f"✅ Lead de teste: ID {lead_id}")
                logger.info(f"\n🔗 Ver no Kommo:")
                logger.info(f"   https://leonardofvieira00.kommo.com/leads/detail/{lead_id}")
                logger.info("\n✅ A integração está usando o pipeline correto!")
                
                return True
            else:
                logger.error(f"❌ Lead criado no pipeline errado! Esperado: {expected_pipeline_id}, Criado em: {created_pipeline_id}")
                return False
                
        else:
            logger.error("❌ Resposta inesperada da API")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar lead: {str(e)}")
        return False


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
    
    # Verificar configurações
    token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
    pipeline_id = os.getenv("KOMMO_PIPELINE_ID")
    
    if not token:
        logger.error("❌ KOMMO_LONG_LIVED_TOKEN não encontrado!")
        return
        
    if not pipeline_id:
        logger.error("❌ KOMMO_PIPELINE_ID não encontrado!")
        return
    
    logger.info(f"✅ Token encontrado: {token[:30]}...")
    logger.info(f"✅ Pipeline ID configurado: {pipeline_id}")
    
    # Executar teste
    success = await test_pipeline()
    
    if success:
        logger.info("\n✅ Pipeline correto confirmado! Funil IA SDR está sendo usado.")
    else:
        logger.error("\n❌ Pipeline incorreto! Verifique a configuração.")


if __name__ == "__main__":
    asyncio.run(main())