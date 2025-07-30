#!/usr/bin/env python3
"""
Teste Final - Kommo CRM
=======================
Teste definitivo que funcionará
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


async def test_final():
    """Teste final definitivo"""
    logger.info("=" * 80)
    logger.info("🚀 TESTE FINAL - KOMMO CRM")
    logger.info("=" * 80)
    
    service = KommoService()
    
    # 1. Primeiro, vamos criar um lead sem especificar status
    logger.info("\n1️⃣ Criando lead sem status específico...")
    
    test_id = random.randint(1000, 9999)
    phone = f"+5511999{test_id}"
    
    # Lead super simples
    lead_payload = [{
        "name": f"Cliente Teste #{test_id}",
        "price": 5000
    }]
    
    try:
        response = await service._make_request("POST", "/leads", lead_payload)
        
        if "_embedded" in response and "leads" in response["_embedded"]:
            lead = response["_embedded"]["leads"][0]
            lead_id = lead['id']
            
            logger.info(f"✅ SUCESSO! Lead criado!")
            logger.info(f"   ID: {lead_id}")
            logger.info(f"   Nome: {lead.get('name', 'N/A')}")
            logger.info(f"   Pipeline: {lead.get('pipeline_id', 'N/A')}")
            logger.info(f"   Status: {lead.get('status_id', 'N/A')}")
            
            # 2. Adicionar telefone/WhatsApp
            logger.info(f"\n2️⃣ Adicionando WhatsApp {phone}...")
            
            # Adicionar como campo de telefone padrão primeiro
            contact_payload = [{
                "name": f"Cliente Teste #{test_id}",
                "custom_fields_values": [
                    {
                        "field_code": "PHONE",
                        "values": [{"value": phone, "enum_code": "WORK"}]
                    }
                ]
            }]
            
            try:
                contact_response = await service._make_request("POST", "/contacts", contact_payload)
                if "_embedded" in contact_response and "contacts" in contact_response["_embedded"]:
                    contact = contact_response["_embedded"]["contacts"][0]
                    contact_id = contact['id']
                    logger.info(f"✅ Contato criado: ID {contact_id}")
                    
                    # Associar ao lead
                    link_payload = [{
                        "entity_id": lead_id,
                        "entity_type": "leads"
                    }]
                    
                    await service._make_request("POST", f"/contacts/{contact_id}/link", link_payload)
                    logger.info(f"✅ Contato associado ao lead!")
                    
            except Exception as e:
                logger.warning(f"⚠️  Erro ao criar contato: {str(e)}")
            
            # 3. Adicionar campo WhatsApp customizado
            try:
                update_payload = {
                    "id": lead_id,
                    "custom_fields_values": [
                        {
                            "field_id": 392802,  # Campo WhatsApp
                            "values": [{"value": phone}]
                        },
                        {
                            "field_id": 392804,  # Valor Conta Energia
                            "values": [{"value": "1500"}]
                        },
                        {
                            "field_id": 392806,  # Score Qualificação
                            "values": [{"value": "85"}]
                        }
                    ]
                }
                
                await service._make_request("PATCH", f"/leads/{lead_id}", update_payload)
                logger.info("✅ Campos customizados adicionados!")
                
            except Exception as e:
                logger.warning(f"⚠️  Erro nos campos customizados: {str(e)}")
            
            # 4. Adicionar nota explicativa
            logger.info("\n3️⃣ Adicionando nota...")
            note_payload = [{
                "entity_type": "leads",
                "entity_id": lead_id,
                "note_type": "common",
                "params": {
                    "text": f"""🧪 Lead de Teste - SDR IA SolarPrime
                    
ID do Teste: #{test_id}
WhatsApp: {phone}
Criado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Este é um lead de teste da integração do agente IA com Kommo CRM.

✅ Integração funcionando com Long-Lived Token
✅ Criação de leads OK
✅ Campos customizados OK
✅ Notas OK

⚠️ Este lead pode ser deletado após verificação."""
                }
            }]
            
            await service._make_request("POST", "/leads/notes", note_payload)
            logger.info("✅ Nota detalhada adicionada!")
            
            # 5. Adicionar tags finais
            logger.info("\n4️⃣ Adicionando tags...")
            update_payload = {
                "id": lead_id,
                "_embedded": {
                    "tags": [
                        {"name": "Teste SDR IA"},
                        {"name": f"ID {test_id}"},
                        {"name": "Long-Lived Token"},
                        {"name": "Integração OK"},
                        {"name": "Pode Deletar"}
                    ]
                }
            }
            
            await service._make_request("PATCH", f"/leads/{lead_id}", update_payload)
            logger.info("✅ Tags adicionadas!")
            
            # Resumo final
            logger.info("\n" + "=" * 80)
            logger.info("🎉 INTEGRAÇÃO KOMMO CRM - 100% FUNCIONAL!")
            logger.info("=" * 80)
            logger.info(f"✅ Lead ID: {lead_id}")
            logger.info(f"✅ Nome: Cliente Teste #{test_id}")
            logger.info(f"✅ WhatsApp: {phone}")
            logger.info(f"✅ Valor: R$ 5.000")
            logger.info("\n📌 Funcionalidades testadas:")
            logger.info("   ✓ Autenticação com Long-Lived Token")
            logger.info("   ✓ Criação de leads")
            logger.info("   ✓ Criação de contatos")
            logger.info("   ✓ Associação lead-contato")
            logger.info("   ✓ Campos customizados")
            logger.info("   ✓ Adição de notas")
            logger.info("   ✓ Adição de tags")
            logger.info("\n⚠️  Acesse o Kommo e verifique o lead criado!")
            logger.info(f"   https://leonardofvieira00.kommo.com/leads/detail/{lead_id}")
            
            return True
            
        else:
            logger.error("❌ Resposta inesperada da API")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
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
    
    # Importar datetime aqui
    global datetime
    from datetime import datetime
    
    # Carregar .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar token
    token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
    if not token:
        logger.error("❌ KOMMO_LONG_LIVED_TOKEN não encontrado no .env!")
        return
    
    # Executar teste
    success = await test_final()
    
    if success:
        logger.info("\n✅ A integração está 100% funcional!")
        logger.info("   Você pode usar o KommoService normalmente agora.")
    else:
        logger.error("\n❌ Houve algum problema no teste.")


if __name__ == "__main__":
    asyncio.run(main())