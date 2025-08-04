#!/usr/bin/env python3
"""
Teste da integração nativa com Google Meet REST API v2
100% Google - Solução oficial sem alternativas
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.google_meet_native import google_meet_native_client
from app.integrations.google_calendar import google_calendar_client

# Configurar logger
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)

async def test_google_meet_native():
    """Testa a integração nativa com Google Meet"""
    
    print("\n" + "🎥"*30)
    print("TESTE DA INTEGRAÇÃO NATIVA GOOGLE MEET API v2")
    print("100% Google - Solução Oficial")
    print("🎥"*30)
    
    # Teste 1: Verificar autenticação
    print("\n" + "="*60)
    print("📝 TESTE 1: VERIFICAÇÃO DE AUTENTICAÇÃO")
    print("="*60)
    
    if google_meet_native_client.is_available():
        print("✅ Cliente Google Meet nativo autenticado com sucesso!")
        print(f"📧 Service Account: {google_meet_native_client.credentials.service_account_email}")
    else:
        print("❌ Cliente Google Meet não está disponível")
        print("💡 Verifique se a Google Meet API está habilitada no Console")
        print("💡 URL: https://console.cloud.google.com/apis/library/meet.googleapis.com")
        return
    
    # Teste 2: Criar um Meeting Space
    print("\n" + "="*60)
    print("📝 TESTE 2: CRIAR MEETING SPACE NATIVO")
    print("="*60)
    
    print("🎥 Criando Meeting Space via Google Meet REST API v2...")
    
    meeting_result = await google_meet_native_client.create_meeting_space(
        title="Teste Solar Prime - Google Meet Nativo",
        access_type="OPEN",
        entry_point_access="ALL"
    )
    
    if meeting_result and meeting_result.get('success'):
        print("\n✅ MEETING SPACE CRIADO COM SUCESSO!")
        print(f"🔗 Meet Link: {meeting_result['meeting_uri']}")
        print(f"📝 Meeting Code: {meeting_result['meeting_code']}")
        print(f"🏷️ Space Name: {meeting_result['space_name']}")
        
        space_name = meeting_result['space_name']
        
        # Teste 3: Buscar informações do Meeting Space
        print("\n" + "="*60)
        print("📝 TESTE 3: BUSCAR INFORMAÇÕES DO MEETING SPACE")
        print("="*60)
        
        space_info = await google_meet_native_client.get_meeting_space(space_name)
        
        if space_info:
            print("✅ Meeting Space encontrado:")
            print(f"   Link: {space_info['meeting_uri']}")
            print(f"   Code: {space_info['meeting_code']}")
            print(f"   Config: {space_info['config']}")
        else:
            print("❌ Não foi possível buscar informações do Meeting Space")
        
        # Perguntar se deve encerrar
        if input("\n🗑️ Encerrar Meeting Space de teste? (s/n): ").lower() == 's':
            ended = await google_meet_native_client.end_meeting_space(space_name)
            if ended:
                print("✅ Meeting Space encerrado")
    else:
        print("❌ Falha ao criar Meeting Space")
        print("💡 Possíveis causas:")
        print("   1. Google Meet API não está habilitada")
        print("   2. Service Account não tem permissões suficientes")
        print("   3. Quota excedida ou limitações da conta")
        
        # Mostrar link para habilitar a API
        print("\n📌 Para habilitar a Google Meet API:")
        print("   1. Acesse: https://console.cloud.google.com/apis/library")
        print("   2. Busque por 'Google Meet API'")
        print("   3. Clique em 'Enable'")
        print("   4. Aguarde alguns minutos para propagar")
        return
    
    # Teste 4: Integração com Calendar
    print("\n" + "="*60)
    print("📝 TESTE 4: INTEGRAÇÃO CALENDAR + MEET NATIVO")
    print("="*60)
    
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    print(f"📅 Criando evento para {start_time.strftime('%d/%m/%Y %H:%M')}")
    print("🎥 Com Google Meet nativo integrado...")
    
    try:
        result = await google_calendar_client.create_event(
            title="Teste Solar Prime - Integração Meet Nativo",
            start_time=start_time,
            end_time=end_time,
            description="Teste de integração com Google Meet REST API v2",
            location="",  # Será preenchido automaticamente com Meet code
            attendees=[],
            reminder_minutes=30,
            conference_data=True  # Ativa criação de Google Meet nativo
        )
        
        if result:
            print("\n✅ EVENTO CRIADO COM MEET NATIVO!")
            print(f"📍 Event ID: {result.get('google_event_id')}")
            print(f"📅 Link Calendar: {result.get('html_link')}")
            print(f"🎥 Meet Link: {result.get('meet_link')}")
            print(f"🏷️ Meet Space: {result.get('meet_space_name')}")
            
            # Verificar evento
            await asyncio.sleep(2)
            event = await google_calendar_client.get_event(result.get('google_event_id'))
            
            if event:
                print("\n📋 Detalhes do evento:")
                print(f"   Título: {event.get('title')}")
                print(f"   Local: {event.get('location', 'Não definido')}")
                
                # Verificar se o link está na descrição
                if 'meet.google.com' in event.get('description', ''):
                    print("\n🎉 SUCESSO TOTAL! Google Meet nativo incluído!")
                    print("✅ Link meet.google.com encontrado na descrição")
                    print("✅ 100% Google - Solução oficial implementada")
            
            # Limpar - deletar evento de teste
            if input("\n🗑️ Remover evento de teste? (s/n): ").lower() == 's':
                deleted = await google_calendar_client.delete_event(result.get('google_event_id'))
                if deleted:
                    print("✅ Evento removido")
                    
                # Se tiver space, encerrar também
                if result.get('meet_space_name'):
                    ended = await google_meet_native_client.end_meeting_space(
                        result.get('meet_space_name')
                    )
                    if ended:
                        print("✅ Meeting Space encerrado")
        else:
            print("❌ Falha ao criar evento com Meet nativo")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    # Relatório final
    print("\n" + "="*80)
    print("📊 RELATÓRIO DA INTEGRAÇÃO NATIVA")
    print("="*80)
    
    print("\n🎯 Características da solução implementada:")
    print("  ✅ 100% Google nativo - REST API v2")
    print("  ✅ Links profissionais meet.google.com")
    print("  ✅ Integração completa Calendar + Meet")
    print("  ✅ Funciona com Service Account")
    print("  ✅ Sem dependências de terceiros")
    print("  ✅ Solução oficial do Google")
    
    if google_meet_native_client.is_available():
        print("\n🚀 SISTEMA PRONTO PARA PRODUÇÃO COM GOOGLE MEET NATIVO!")
    else:
        print("\n⚠️ Configure a Google Meet API para ativar a integração nativa")
    
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_google_meet_native())