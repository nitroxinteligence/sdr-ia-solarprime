#!/usr/bin/env python
"""
Test Script - Sincronização Mínima Kommo ↔ Google Calendar
==========================================================
Testa a integração simplificada entre Kommo e Google Calendar
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger

# Carregar variáveis de ambiente
load_dotenv()

# Imports necessários
from agents.tools.google_calendar_tools import (
    schedule_solar_meeting,
    cancel_meeting
)
from services.kommo_service import kommo_service
from repositories.lead_repository import lead_repository
from models.lead import LeadCreate, LeadUpdate
from models.kommo_models import KommoLead
from uuid import uuid4


async def test_minimal_sync():
    """Testa a sincronização mínima implementada"""
    
    print("\n=== TESTE DE SINCRONIZAÇÃO MÍNIMA KOMMO ↔ GOOGLE CALENDAR ===\n")
    
    # 1. Criar um lead de teste
    test_phone = f"5511{str(uuid4().int)[:9]}"
    print(f"📱 Criando lead de teste: {test_phone}")
    
    lead_data = LeadCreate(
        phone_number=test_phone,
        name="Pedro Sync Teste",
        email="pedro.sync@example.com"
    )
    
    lead = await lead_repository.create(lead_data.model_dump())
    
    # 2. Criar lead no Kommo primeiro
    print("📊 Criando lead no Kommo CRM...")
    
    # Criar lead simples sem campos problemáticos
    lead_payload = [{
        "name": "Pedro Sync Teste",
        "price": 6000,  # Valor da oportunidade
        "pipeline_id": int(os.getenv("KOMMO_PIPELINE_ID", 11672895)),  # Funil IA SDR
        "_embedded": {
            "tags": [
                {"name": "Teste"},
                {"name": "Sync"},
                {"name": "Calendar"}
            ]
        }
    }]
    
    # Criar no Kommo diretamente
    try:
        result = await kommo_service._make_request("POST", "/leads", lead_payload)
    except Exception as e:
        print(f"❌ Erro ao criar lead no Kommo: {e}")
        result = None
    
    if result and "_embedded" in result and "leads" in result["_embedded"]:
        kommo_lead_id = str(result["_embedded"]["leads"][0]["id"])
        print(f"✅ Lead criado no Kommo: ID {kommo_lead_id}")
        
        # Atualizar lead local com ID do Kommo
        update_data = LeadUpdate(
            kommo_lead_id=kommo_lead_id,
            bill_value=6000.00,
            is_decision_maker=True,
            has_solar_system=False,
            has_active_contract=False,
            qualification_status="QUALIFIED",
            qualification_score=90
        )
        
        await lead_repository.update(lead.id, update_data.model_dump(exclude_unset=True))
        
        # 3. Agendar reunião (deve salvar link no Kommo)
        print("\n📅 Agendando reunião no Google Calendar...")
        
        tomorrow = datetime.now() + timedelta(days=1)
        if tomorrow.weekday() >= 5:  # Fim de semana
            tomorrow = tomorrow + timedelta(days=(7 - tomorrow.weekday()))
        
        date_str = tomorrow.strftime("%d/%m/%Y")
        time_str = "15:00"
        
        meeting_result = await schedule_solar_meeting(
            lead_phone=test_phone,
            date=date_str,
            time=time_str,
            lead_name="Pedro Sync Teste"
        )
        
        print(f"\nResultado do agendamento: {meeting_result['status']}")
        
        if meeting_result['status'] == 'sucesso':
            print(f"📍 Link do evento: {meeting_result['event_link']}")
            
            # 4. Verificar se o link foi salvo no Kommo
            print("\n🔍 Verificando se o link foi salvo no Kommo...")
            
            # Aguardar um pouco para garantir que foi salvo
            await asyncio.sleep(2)
            
            # Buscar lead atualizado no Kommo
            updated_kommo_lead = await kommo_service.get_lead(int(kommo_lead_id))
            
            if updated_kommo_lead:
                custom_fields = updated_kommo_lead.get("custom_fields_values", [])
                
                # Procurar campo google_calendar_link
                calendar_link_found = False
                meeting_status_found = False
                
                for field in custom_fields:
                    field_name = field.get("field_name", "")
                    values = field.get("values", [])
                    
                    if values:
                        value = values[0].get("value", "")
                        
                        if "calendar" in field_name.lower() and "google.com/calendar" in value:
                            calendar_link_found = True
                            print(f"✅ Link do Calendar encontrado no Kommo: {value[:50]}...")
                        
                        if "meeting" in field_name.lower() and "status" in field_name.lower():
                            meeting_status_found = True
                            print(f"✅ Status da reunião no Kommo: {value}")
                
                if not calendar_link_found:
                    print("⚠️ Link do Calendar não encontrado nos campos customizados")
                    print("   Verifique se o campo KOMMO_FIELD_GOOGLE_CALENDAR_LINK está configurado no .env")
                
                if not meeting_status_found:
                    print("⚠️ Status da reunião não encontrado nos campos customizados")
                    print("   Verifique se o campo KOMMO_FIELD_MEETING_STATUS está configurado no .env")
            
            # 5. Testar cancelamento (opcional)
            print("\n❌ Testando cancelamento de reunião...")
            
            cancel_result = await cancel_meeting(
                lead_phone=test_phone,
                reason="Teste de cancelamento via sistema"
            )
            
            print(f"Resultado do cancelamento: {cancel_result['status']}")
            
            # Verificar se o status foi atualizado no Kommo
            await asyncio.sleep(2)
            
            # Nota: Em produção, o cancelamento seria feito via webhook do Kommo
            # e automaticamente cancelaria no Google Calendar
            
        # 6. Limpar dados de teste
        print("\n🧹 Limpando dados de teste...")
        
        # Deletar lead do Kommo
        try:
            await kommo_service._make_request("DELETE", f"/leads/{kommo_lead_id}")
            print("✅ Lead removido do Kommo")
        except:
            print("⚠️ Não foi possível remover lead do Kommo")
        
        # Deletar lead local
        await lead_repository.delete(lead.id)
        print("✅ Lead removido do banco local")
        
    else:
        print("❌ Erro ao criar lead no Kommo")
    
    # Sempre limpar lead local
    try:
        await lead_repository.delete(lead.id)
        print("✅ Lead local removido")
    except:
        pass
    
    print("\n✅ Teste de sincronização mínima concluído!")


async def test_webhook_simulation():
    """Simula eventos de webhook do Kommo"""
    
    print("\n=== SIMULAÇÃO DE WEBHOOK DO KOMMO ===\n")
    
    # Simular estrutura de webhook
    webhook_data = {
        "tasks": {
            "delete": [{
                "id": 12345,
                "entity_id": 67890,
                "text": "Reunião agendada via WhatsApp"
            }]
        }
    }
    
    print("📨 Simulando webhook de cancelamento de reunião...")
    print(f"Dados do webhook: {webhook_data}")
    
    # Nota: Em produção, isso seria processado pelo endpoint /webhook/kommo/events
    print("\n💡 Em produção, o webhook seria processado automaticamente:")
    print("   1. Kommo envia webhook quando tarefa de reunião é deletada")
    print("   2. Sistema cancela automaticamente no Google Calendar")
    print("   3. Cliente recebe notificação via WhatsApp")
    
    print("\n✅ Simulação concluída!")


if __name__ == "__main__":
    print("🚀 Iniciando testes de sincronização mínima...")
    
    # Executar testes
    asyncio.run(test_minimal_sync())
    asyncio.run(test_webhook_simulation())
    
    print("\n🎉 Todos os testes concluídos!")
    print("\n📝 IMPORTANTE:")
    print("   - Configure os campos customizados no Kommo:")
    print("     • google_calendar_link (tipo: link/URL)")
    print("     • meeting_status (tipo: texto ou select)")
    print("   - Adicione os IDs dos campos no arquivo .env")
    print("   - Configure o webhook no Kommo para /webhook/kommo/events")