"""
Exemplo de Uso - Google Calendar Integration
Demonstra como usar o CalendarWorkflow para gerenciar eventos em escala
"""

import asyncio
from datetime import datetime, timedelta
from app.workflows.workflow_manager import workflow_manager
from app.workflows.calendar_workflow import calendar_workflow, CalendarOperation
from app.services.calendar_sync_service import calendar_sync_service

async def example_usage():
    """
    Exemplos de uso do sistema de calendário integrado
    Preparado para lidar com 1-2k leads simultâneos
    """
    
    print("🚀 Iniciando exemplos de uso do Google Calendar")
    print("=" * 50)
    
    # ========== EXEMPLO 1: AGENDAR REUNIÃO ==========
    print("\n📅 EXEMPLO 1: Agendando reunião")
    print("-" * 30)
    
    # Agendar reunião para amanhã às 14h
    tomorrow = datetime.now() + timedelta(days=1)
    meeting_start = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    meeting_end = meeting_start + timedelta(hours=1)
    
    result = await workflow_manager.schedule_meeting(
        lead_id="123e4567-e89b-12d3-a456-426614174000",  # UUID do lead
        title="Apresentação Solar Prime - João Silva",
        start_time=meeting_start,
        end_time=meeting_end,
        description="Apresentação da solução de energia solar para economia de 20% na conta de luz",
        location="Online - Google Meet",
        attendees=["joao.silva@example.com", "helen.vieira@solarprime.com.br"],
        meeting_link="https://meet.google.com/abc-defg-hij"
    )
    
    if result['success']:
        print(f"✅ Reunião agendada com sucesso!")
        print(f"   Mensagem: {result['message']}")
    else:
        print(f"❌ Erro ao agendar: {result['error']}")
    
    # Aguardar processamento
    await asyncio.sleep(2)
    
    # ========== EXEMPLO 2: VERIFICAR DISPONIBILIDADE ==========
    print("\n🔍 EXEMPLO 2: Verificando disponibilidade")
    print("-" * 30)
    
    # Verificar se há disponibilidade para depois de amanhã às 10h
    day_after_tomorrow = datetime.now() + timedelta(days=2)
    check_start = day_after_tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    check_end = check_start + timedelta(hours=1)
    
    result = await workflow_manager.check_availability(
        start_time=check_start,
        end_time=check_end
    )
    
    print(f"🕐 Verificando horário: {check_start.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Status: {result['message']}")
    
    # ========== EXEMPLO 3: REAGENDAR REUNIÃO ==========
    print("\n🔄 EXEMPLO 3: Reagendando reunião")
    print("-" * 30)
    
    # Reagendar para novo horário
    new_start = meeting_start + timedelta(hours=2)
    new_end = new_start + timedelta(hours=1)
    
    # Nota: você precisaria do google_event_id real retornado ao criar o evento
    google_event_id = "exemplo_event_id_123"
    
    result = await workflow_manager.reschedule_meeting(
        google_event_id=google_event_id,
        new_start_time=new_start,
        new_end_time=new_end
    )
    
    print(f"📝 Reagendamento solicitado")
    print(f"   Novo horário: {new_start.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Status: {result['message']}")
    
    # ========== EXEMPLO 4: ATUALIZAR DETALHES ==========
    print("\n✏️ EXEMPLO 4: Atualizando detalhes da reunião")
    print("-" * 30)
    
    updates = {
        'title': 'Apresentação Solar Prime - João Silva (ATUALIZADA)',
        'description': 'Apresentação focada em usina própria - economia de 25%',
        'location': 'Presencial - Escritório Solar Prime Recife'
    }
    
    result = await workflow_manager.update_meeting(
        google_event_id=google_event_id,
        updates=updates
    )
    
    print(f"📝 Atualização solicitada")
    print(f"   Status: {result['message']}")
    
    # ========== EXEMPLO 5: PROCESSAMENTO EM LOTE ==========
    print("\n🚀 EXEMPLO 5: Agendamento em lote (simulando alta carga)")
    print("-" * 30)
    
    # Simular agendamento de múltiplas reuniões (como seria com 1-2k leads)
    leads_to_schedule = [
        {"id": f"lead_{i}", "name": f"Cliente {i}", "email": f"cliente{i}@example.com"}
        for i in range(10)  # Reduzido para exemplo, mas funciona com 1000+
    ]
    
    print(f"📊 Agendando {len(leads_to_schedule)} reuniões em paralelo...")
    
    tasks = []
    base_time = datetime.now() + timedelta(days=3)
    
    for i, lead in enumerate(leads_to_schedule):
        # Distribuir reuniões ao longo do dia
        meeting_time = base_time.replace(hour=9 + (i % 8), minute=0, second=0, microsecond=0)
        
        task = workflow_manager.schedule_meeting(
            lead_id=lead['id'],
            title=f"Apresentação Solar Prime - {lead['name']}",
            start_time=meeting_time,
            end_time=meeting_time + timedelta(hours=1),
            description=f"Apresentação para {lead['name']}",
            attendees=[lead['email']]
        )
        tasks.append(task)
    
    # Executar todas as tarefas em paralelo
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    print(f"✅ {successful}/{len(leads_to_schedule)} reuniões adicionadas à fila")
    
    # ========== EXEMPLO 6: CANCELAR REUNIÃO ==========
    print("\n❌ EXEMPLO 6: Cancelando reunião")
    print("-" * 30)
    
    result = await workflow_manager.cancel_meeting(
        google_event_id=google_event_id
    )
    
    print(f"🗑️ Cancelamento solicitado")
    print(f"   Status: {result['message']}")
    
    # ========== EXEMPLO 7: MÉTRICAS DO SISTEMA ==========
    print("\n📊 EXEMPLO 7: Métricas do CalendarWorkflow")
    print("-" * 30)
    
    metrics = workflow_manager.get_calendar_metrics()
    
    print("📈 Métricas de Desempenho:")
    print(f"   Total de requisições: {metrics['total_requests']}")
    print(f"   Bem-sucedidas: {metrics['successful']}")
    print(f"   Falhadas: {metrics['failed']}")
    print(f"   Tentativas de retry: {metrics['retries']}")
    print(f"   Tamanho da fila: {metrics['queue_size']}")
    print(f"   Workers ativos: {metrics['workers']}")
    print(f"   Taxa de sucesso: {metrics['success_rate']:.1f}%")
    
    # ========== EXEMPLO 8: SINCRONIZAÇÃO MANUAL ==========
    print("\n🔄 EXEMPLO 8: Forçando sincronização")
    print("-" * 30)
    
    sync_result = await calendar_sync_service.force_sync()
    
    if sync_result['success']:
        print("✅ Sincronização concluída com sucesso")
    else:
        print(f"❌ Erro na sincronização: {sync_result['error']}")
    
    # ========== EXEMPLO 9: ADICIONAR OPERAÇÃO DIRETAMENTE ==========
    print("\n⚡ EXEMPLO 9: Adicionando operação diretamente ao workflow")
    print("-" * 30)
    
    # Para casos específicos, você pode adicionar operações diretamente
    await calendar_workflow.add_operation(
        CalendarOperation.LIST_EVENTS,
        {
            'time_min': datetime.now(),
            'time_max': datetime.now() + timedelta(days=7),
            'max_results': 5
        }
    )
    
    print("📋 Operação de listagem adicionada à fila")
    
    # ========== EXEMPLO 10: ENVIO DE LEMBRETES ==========
    print("\n🔔 EXEMPLO 10: Enviando lembretes pendentes")
    print("-" * 30)
    
    # O serviço de sincronização envia lembretes automaticamente
    # Mas você pode forçar o envio manualmente
    await calendar_sync_service.send_pending_reminders()
    
    print("📱 Lembretes verificados e enviados")
    
    print("\n" + "=" * 50)
    print("✅ Exemplos concluídos!")
    print("\n💡 DICAS IMPORTANTES:")
    print("1. O sistema usa filas para processar até 2000 operações simultâneas")
    print("2. Rate limiting automático garante respeito aos limites da API Google (5 req/s)")
    print("3. Retry automático com backoff exponencial em caso de falhas")
    print("4. Sincronização automática a cada 5 minutos")
    print("5. Lembretes enviados automaticamente 30 minutos antes das reuniões")
    print("6. 10 workers processam operações em paralelo para máxima eficiência")

async def main():
    """Função principal para executar os exemplos"""
    print("=" * 60)
    print("GOOGLE CALENDAR INTEGRATION - EXEMPLOS DE USO")
    print("SDR IA SolarPrime v0.2")
    print("=" * 60)
    
    # Inicializar o workflow manager
    print("\n🔧 Inicializando sistema...")
    await workflow_manager.initialize()
    
    # Iniciar o serviço de sincronização
    await calendar_sync_service.start()
    
    print("✅ Sistema inicializado\n")
    
    # Executar exemplos
    await example_usage()
    
    # Aguardar um pouco para processar operações pendentes
    print("\n⏳ Aguardando processamento das operações...")
    await asyncio.sleep(5)
    
    # Parar o serviço
    await calendar_sync_service.stop()
    
    print("\n🏁 Exemplo finalizado!")

if __name__ == "__main__":
    # Executar exemplos
    asyncio.run(main())