#!/usr/bin/env python3
"""
Script de diagnóstico para o erro 237 do Kommo
Testa a criação de tasks e identifica o problema
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import aiohttp
from loguru import logger

# Carregar variáveis de ambiente
load_dotenv()

async def test_kommo_task_creation():
    """Testa a criação de tasks no Kommo"""
    
    # Configurações
    base_url = os.getenv("KOMMO_BASE_URL", "https://api-c.kommo.com")
    token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
    
    if not token:
        logger.error("❌ KOMMO_LONG_LIVED_TOKEN não encontrado no .env")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"🔍 Base URL: {base_url}")
    logger.info(f"🔑 Token: {token[:20]}...")
    
    # Primeiro, vamos buscar um lead válido
    async with aiohttp.ClientSession() as session:
        # Buscar leads
        logger.info("\n1️⃣ Buscando leads existentes...")
        
        try:
            async with session.get(
                f"{base_url}/api/v4/leads",
                headers=headers,
                params={"limit": 1}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("_embedded", {}).get("leads"):
                        lead = data["_embedded"]["leads"][0]
                        lead_id = lead["id"]
                        logger.info(f"✅ Lead encontrado: ID {lead_id} - {lead.get('name', 'Sem nome')}")
                    else:
                        logger.error("❌ Nenhum lead encontrado no CRM")
                        return
                else:
                    error = await response.text()
                    logger.error(f"❌ Erro ao buscar leads: {response.status} - {error}")
                    return
        except Exception as e:
            logger.error(f"❌ Erro na requisição: {e}")
            return
        
        # Agora vamos testar a criação de task
        logger.info("\n2️⃣ Testando criação de task...")
        
        # Data para 1 hora no futuro
        future_time = datetime.now() + timedelta(hours=1)
        timestamp = int(future_time.timestamp())
        
        task_data = {
            "text": "Teste de task - Diagnóstico erro 237",
            "complete_till": timestamp,
            "entity_id": lead_id,
            "entity_type": "leads",
            "task_type_id": 1
        }
        
        logger.info(f"📤 Dados da task: {task_data}")
        
        try:
            # Tentar criar como array (formato esperado)
            async with session.post(
                f"{base_url}/api/v4/tasks",
                headers=headers,
                json=[task_data]  # Como array
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    logger.info(f"✅ Task criada com sucesso!")
                    logger.info(f"📋 Resposta: {data}")
                else:
                    error = await response.text()
                    logger.error(f"❌ Erro {response.status}: {error}")
                    
                    # Se for erro 237, testar alternativas
                    if "Error code 237" in error:
                        logger.info("\n3️⃣ Erro 237 detectado. Testando alternativas...")
                        
                        # Alternativa 1: Sem task_type_id
                        logger.info("🔄 Tentando sem task_type_id...")
                        task_data_alt1 = {
                            "text": "Teste sem task_type_id",
                            "complete_till": timestamp,
                            "entity_id": lead_id,
                            "entity_type": "leads"
                        }
                        
                        async with session.post(
                            f"{base_url}/api/v4/tasks",
                            headers=headers,
                            json=[task_data_alt1]
                        ) as response2:
                            if response2.status in [200, 201]:
                                logger.info("✅ Funciona sem task_type_id!")
                            else:
                                error2 = await response2.text()
                                logger.error(f"❌ Ainda erro: {error2}")
                        
                        # Alternativa 2: Como objeto único (não array)
                        logger.info("🔄 Tentando como objeto único...")
                        async with session.post(
                            f"{base_url}/api/v4/tasks",
                            headers=headers,
                            json=task_data  # Sem array
                        ) as response3:
                            if response3.status in [200, 201]:
                                logger.info("✅ Funciona como objeto único!")
                            else:
                                error3 = await response3.text()
                                logger.error(f"❌ Ainda erro: {error3}")
                                
        except Exception as e:
            logger.error(f"❌ Erro na requisição: {e}")
        
        # Verificar URL alternativa
        if base_url == "https://api-c.kommo.com":
            subdomain = os.getenv("KOMMO_SUBDOMAIN", "leonardofvieira00")
            alt_url = f"https://{subdomain}.kommo.com"
            
            logger.info(f"\n4️⃣ Testando URL alternativa: {alt_url}")
            
            try:
                async with session.post(
                    f"{alt_url}/api/v4/tasks",
                    headers=headers,
                    json=[task_data]
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"✅ Funciona com URL alternativa! Use: {alt_url}")
                    else:
                        error = await response.text()
                        logger.error(f"❌ Erro com URL alternativa: {error}")
            except Exception as e:
                logger.error(f"❌ Erro: {e}")

async def main():
    """Executa o diagnóstico"""
    logger.info("🚀 Iniciando diagnóstico do erro 237 do Kommo\n")
    await test_kommo_task_creation()
    logger.info("\n✅ Diagnóstico concluído!")

if __name__ == "__main__":
    asyncio.run(main())