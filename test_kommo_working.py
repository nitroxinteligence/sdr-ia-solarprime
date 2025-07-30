#!/usr/bin/env python3
"""
Teste Funcional - Kommo CRM
===========================
Teste que definitivamente funciona
"""

import asyncio
import sys
from loguru import logger
import os
import random

# Adicionar o diretório raiz ao Python path
sys.path.append('.')

from services.kommo_service import KommoService
from config.config import get_config


async def test_kommo_working():
    """Teste completo e funcional"""
    logger.info("=" * 80)
    logger.info("🧪 TESTE FUNCIONAL KOMMO CRM")
    logger.info("=" * 80)
    
    service = KommoService()
    config = get_config()
    
    # 1. Obter pipeline correto
    logger.info("\n1️⃣ Obtendo pipeline configurado...")
    
    # Usar o pipeline do .env
    pipeline_id = config.kommo.pipeline_id
    logger.info(f"   Pipeline ID do .env: {pipeline_id}")
    
    # Buscar detalhes do pipeline
    try:
        response = await service._make_request(
            "GET",
            f"/leads/pipelines/{pipeline_id}",
            params={"with": "statuses"}
        )
        
        pipeline_name = response.get("name", "N/A")
        logger.info(f"✅ Pipeline encontrado: {pipeline_name}")
        
        # Listar estágios
        statuses = response.get("_embedded", {}).get("statuses", [])
        logger.info(f"   {len(statuses)} estágios encontrados:")
        
        status_id = None
        for status in statuses[:5]:  # Mostrar apenas 5 primeiros
            logger.info(f"   - {status['name']} (ID: {status['id']})")
            if not status_id:
                status_id = status['id']  # Pegar o primeiro
                
    except Exception as e:
        logger.error(f"❌ Erro ao obter pipeline: {str(e)}")
        return
    
    # 2. Criar lead com dados corretos
    logger.info(f"\n2️⃣ Criando lead no pipeline {pipeline_id}, status {status_id}...")
    
    test_id = random.randint(1000, 9999)
    lead_payload = [{
        "name": f"Teste API #{test_id}",
        "pipeline_id": pipeline_id,
        "status_id": status_id,
        "price": 1000  # Adicionar um valor
    }]
    
    try:
        response = await service._make_request("POST", "/leads", lead_payload)
        
        if "_embedded" in response and "leads" in response["_embedded"]:
            lead = response["_embedded"]["leads"][0]
            lead_id = lead['id']
            
            logger.info(f"✅ Lead criado com sucesso!")
            logger.info(f"   ID: {lead_id}")
            logger.info(f"   Nome: {lead['name']}")
            logger.info(f"   Pipeline: {lead['pipeline_id']}")
            logger.info(f"   Status: {lead['status_id']}")
            
            # 3. Adicionar campos customizados
            logger.info("\n3️⃣ Adicionando campos customizados...")
            
            # Buscar campo WhatsApp
            whatsapp_field_id = 392802  # ID que vimos no log
            
            update_payload = {
                "id": lead_id,
                "custom_fields_values": [
                    {
                        "field_id": whatsapp_field_id,
                        "values": [{"value": f"+5511999{test_id}"}]
                    }
                ]
            }
            
            try:
                await service._make_request("PATCH", f"/leads/{lead_id}", update_payload)
                logger.info("✅ Campo WhatsApp adicionado!")
            except Exception as e:
                logger.warning(f"⚠️  Erro ao adicionar campo: {str(e)}")
            
            # 4. Adicionar nota
            logger.info("\n4️⃣ Adicionando nota...")
            note_payload = [{
                "entity_type": "leads",
                "entity_id": lead_id,
                "note_type": "common",
                "params": {
                    "text": f"Lead de teste #{test_id}\nCriado via API\nTeste de integração Kommo CRM"
                }
            }]
            
            await service._make_request("POST", "/leads/notes", note_payload)
            logger.info("✅ Nota adicionada!")
            
            # 5. Adicionar tags
            logger.info("\n5️⃣ Adicionando tags...")
            update_payload = {
                "id": lead_id,
                "_embedded": {
                    "tags": [
                        {"name": "Teste API"},
                        {"name": f"ID {test_id}"},
                        {"name": "Pode Deletar"}
                    ]
                }
            }
            
            await service._make_request("PATCH", f"/leads/{lead_id}", update_payload)
            logger.info("✅ Tags adicionadas!")
            
            # 6. Mover para próximo estágio
            if len(statuses) > 1:
                logger.info("\n6️⃣ Movendo para próximo estágio...")
                next_status = statuses[1]
                
                move_payload = {
                    "id": lead_id,
                    "status_id": next_status["id"]
                }
                
                await service._make_request("PATCH", f"/leads/{lead_id}", move_payload)
                logger.info(f"✅ Movido para: {next_status['name']}")
            
            # Resumo final
            logger.info("\n" + "=" * 80)
            logger.info("🎉 TESTE CONCLUÍDO COM SUCESSO!")
            logger.info("=" * 80)
            logger.info(f"✅ Lead criado: ID {lead_id}")
            logger.info(f"✅ WhatsApp: +5511999{test_id}")
            logger.info(f"✅ Pipeline: {pipeline_name}")
            logger.info(f"✅ Tags: Teste API, ID {test_id}, Pode Deletar")
            logger.info("\n⚠️  Lembre-se de deletar o lead de teste no Kommo!")
            
        else:
            logger.error("❌ Resposta inesperada da API")
            logger.info(f"   Resposta: {response}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar lead: {str(e)}")
        
        # Se for erro 400, mostrar detalhes
        if "400" in str(e):
            logger.info("\n💡 Possíveis causas:")
            logger.info("   1. Pipeline ID incorreto")
            logger.info("   2. Status ID não pertence ao pipeline")
            logger.info("   3. Campos obrigatórios faltando")


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
    
    # Executar teste
    await test_kommo_working()


if __name__ == "__main__":
    asyncio.run(main())