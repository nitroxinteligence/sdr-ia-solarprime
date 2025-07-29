#!/usr/bin/env python3
"""
Test Google Calendar Integration
================================
Script para testar a integração com Google Calendar
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from config.google_calendar_config import google_calendar_config
from services.google_calendar_service import GoogleCalendarService


async def test_calendar_integration():
    """Testa todas as funcionalidades do Google Calendar"""
    
    print("\n🔧 TESTE DE INTEGRAÇÃO DO GOOGLE CALENDAR\n")
    print("="*50)
    
    # 1. Verificar configuração
    print("\n1️⃣ Verificando configuração...")
    if not google_calendar_config.validate():
        print("❌ Configuração inválida. Siga as instruções acima.")
        return
    print("✅ Configuração válida")
    
    # 2. Inicializar serviço
    print("\n2️⃣ Inicializando serviço...")
    try:
        service = GoogleCalendarService(google_calendar_config)
        if not service.service:
            print("❌ Falha ao inicializar serviço")
            return
        print("✅ Serviço inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return
    
    # 3. Testar listagem de eventos
    print("\n3️⃣ Listando eventos dos próximos 7 dias...")
    try:
        events = await service.list_events()
        print(f"✅ Encontrados {len(events)} eventos")
        for event in events[:3]:  # Mostrar apenas 3 primeiros
            print(f"   - {event['summary']} em {event['start']}")
    except Exception as e:
        print(f"❌ Erro ao listar eventos: {e}")
    
    # 4. Testar criação de evento
    print("\n4️⃣ Criando evento de teste...")
    try:
        # Agendar para amanhã às 14h
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_14h = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        test_lead_data = {
            'id': 'test-123',
            'name': 'João Teste',
            'phone': '(81) 99999-9999',
            'email': 'teste@example.com',
            'bill_value': 850.00,
            'consumption_kwh': 450,
            'solution_interest': 'Energia Solar Residencial',
            'crm_link': 'https://crm.example.com/lead/123'
        }
        
        event_result = await service.create_event(
            title="☀️ [TESTE] Reunião SolarPrime - João Teste",
            start_datetime=tomorrow_14h,
            description="Este é um evento de teste da integração",
            location=google_calendar_config.meeting_location,
            lead_data=test_lead_data
        )
        
        if event_result:
            print(f"✅ Evento criado com sucesso!")
            print(f"   ID: {event_result['id']}")
            print(f"   Link: {event_result['link']}")
            
            # Guardar ID para próximos testes
            test_event_id = event_result['id']
        else:
            print("❌ Falha ao criar evento")
            return
            
    except Exception as e:
        print(f"❌ Erro ao criar evento: {e}")
        return
    
    # 5. Testar atualização de evento
    print("\n5️⃣ Atualizando evento de teste...")
    try:
        # Adiar em 1 hora
        new_time = tomorrow_14h + timedelta(hours=1)
        
        update_result = await service.update_event(
            event_id=test_event_id,
            updates={
                'start_datetime': new_time,
                'end_datetime': new_time + timedelta(hours=1),
                'summary': '☀️ [TESTE - ATUALIZADO] Reunião SolarPrime - João Teste'
            }
        )
        
        if update_result:
            print("✅ Evento atualizado com sucesso!")
            print(f"   Novo horário: {new_time.strftime('%d/%m/%Y %H:%M')}")
        else:
            print("❌ Falha ao atualizar evento")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar evento: {e}")
    
    # 6. Testar verificação de disponibilidade
    print("\n6️⃣ Verificando disponibilidade para amanhã...")
    try:
        slots = await service.check_availability(
            date=tomorrow,
            duration_minutes=60
        )
        
        print(f"✅ Encontrados {len(slots)} horários disponíveis:")
        for slot in slots[:5]:  # Mostrar apenas 5 primeiros
            print(f"   - {slot['start']} até {slot['end']}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar disponibilidade: {e}")
    
    # 7. Testar cancelamento de evento
    print("\n7️⃣ Cancelando evento de teste...")
    try:
        cancel_result = await service.cancel_event(
            event_id=test_event_id,
            send_notifications=False  # Não enviar notificações para teste
        )
        
        if cancel_result:
            print("✅ Evento cancelado com sucesso!")
        else:
            print("❌ Falha ao cancelar evento")
            
    except Exception as e:
        print(f"❌ Erro ao cancelar evento: {e}")
    
    print("\n" + "="*50)
    print("✅ TESTE CONCLUÍDO!")
    print("\nPróximos passos:")
    print("1. Verifique seu Google Calendar para confirmar as operações")
    print("2. Configure as variáveis de ambiente no .env")
    print("3. Execute o agente e teste o agendamento via WhatsApp")


async def test_authentication_only():
    """Testa apenas a autenticação"""
    print("\n🔐 TESTE DE AUTENTICAÇÃO\n")
    print("="*50)
    
    # Verificar arquivo de credenciais
    creds_path = google_calendar_config.credentials_path
    if not Path(creds_path).exists():
        print(f"❌ Arquivo de credenciais não encontrado: {creds_path}")
        print("\n📝 Instruções:")
        print("1. Acesse https://console.cloud.google.com/")
        print("2. Crie um projeto e ative a Google Calendar API")
        print("3. Crie credenciais OAuth 2.0 para aplicativo desktop")
        print(f"4. Baixe o JSON e salve em: {creds_path}")
        return
    
    print(f"✅ Arquivo de credenciais encontrado: {creds_path}")
    
    # Tentar inicializar
    print("\n🔄 Iniciando autenticação...")
    print("Uma janela do navegador será aberta para autorização.")
    print("Faça login e autorize o acesso ao Google Calendar.")
    
    try:
        service = GoogleCalendarService(google_calendar_config)
        if service.service:
            print("\n✅ Autenticação concluída com sucesso!")
            print(f"Token salvo em: {google_calendar_config.token_path}")
        else:
            print("\n❌ Falha na autenticação")
    except Exception as e:
        print(f"\n❌ Erro durante autenticação: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Testar integração com Google Calendar")
    parser.add_argument(
        "--auth-only",
        action="store_true",
        help="Testar apenas autenticação"
    )
    
    args = parser.parse_args()
    
    if args.auth_only:
        asyncio.run(test_authentication_only())
    else:
        asyncio.run(test_calendar_integration())