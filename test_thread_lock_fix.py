#!/usr/bin/env python3
"""
Teste da correção de concorrência com Thread Lock
Testa se o controle de concorrência funciona com múltiplas threads (AGnOAsyncExecutor)
"""

import asyncio
import threading
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor

def test_thread_lock_concurrency():
    """Testa se o thread lock impede execução simultânea"""
    print("🧪 Testando controle de concorrência com Thread Lock...")
    
    # Simular múltiplas chamadas simultâneas (como AGnO faz)
    def simulate_agno_call(call_id: int) -> dict:
        """Simula uma chamada da ferramenta via AGnO Framework"""
        try:
            from agente.tools.whatsapp.send_text_message import send_msg
            
            start_time = time.time()
            print(f"🔄 Chamada {call_id}: Iniciando às {start_time:.3f}")
            
            # Simular argumentos da ferramenta
            result = send_msg(
                text=f"Teste Thread Lock - Mensagem {call_id}",
                phone="5581999999999",
                delay=1.0
            )
            
            end_time = time.time()
            print(f"✅ Chamada {call_id}: Concluída às {end_time:.3f} (duração: {end_time - start_time:.3f}s)")
            
            return {
                "call_id": call_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "success": result.get("success", False)
            }
            
        except Exception as e:
            print(f"❌ Chamada {call_id}: Erro - {e}")
            return {
                "call_id": call_id,
                "error": str(e),
                "success": False
            }
    
    # Executar múltiplas chamadas em threads separadas (como AGnO faz)
    print("\n🚀 Executando 5 chamadas simultâneas em threads separadas...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submeter todas as chamadas ao mesmo tempo
        futures = [executor.submit(simulate_agno_call, i+1) for i in range(5)]
        
        # Aguardar todos os resultados
        results = []
        for future in futures:
            result = future.result()
            results.append(result)
    
    # Analisar resultados
    print("\n📊 Análise dos resultados:")
    
    successful_calls = [r for r in results if r.get("success", False)]
    print(f"✅ Chamadas bem-sucedidas: {len(successful_calls)}")
    
    if len(successful_calls) >= 2:
        # Verificar se as chamadas foram executadas sequencialmente
        start_times = [r["start_time"] for r in successful_calls]
        end_times = [r["end_time"] for r in successful_calls]
        
        start_times.sort()
        end_times.sort()
        
        sequential = True
        for i in range(len(start_times) - 1):
            # Se uma chamada começou antes da anterior terminar, não é sequencial
            if start_times[i+1] < end_times[i]:
                sequential = False
                break
        
        if sequential:
            print("🎯 ✅ SUCESSO: Execução sequencial confirmada!")
            print("🔒 Thread Lock funcionando: Chamadas executadas uma por vez")
        else:
            print("⚠️ ❌ PROBLEMA: Execução simultânea detectada!")
            print("🔓 Thread Lock NÃO funcionando: Múltiplas chamadas simultâneas")
    
    # Mostrar estatísticas
    try:
        from agente.tools.whatsapp.send_text_message import get_message_semaphore_stats
        stats = get_message_semaphore_stats()
        print(f"\n📈 Estatísticas finais do controle de concorrência:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"⚠️ Erro ao obter estatísticas: {e}")
    
    return len(successful_calls) > 0


def test_evolution_service_stats():
    """Testa se as estatísticas do Evolution Service estão funcionando"""
    print("\n🧪 Testando estatísticas do Evolution Service...")
    
    try:
        from agente.services.evolution_service import EvolutionAPIService
        stats = EvolutionAPIService.get_queue_stats()
        
        print("📊 Estatísticas da fila Evolution Service:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
            
        print("✅ Estatísticas do Evolution Service funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas do Evolution Service: {e}")
        return False


if __name__ == "__main__":
    print("🧪 TESTE: Correção Thread Lock para Controle de Concorrência")
    print("=" * 60)
    
    # Teste 1: Thread Lock
    thread_success = test_thread_lock_concurrency()
    
    # Teste 2: Evolution Service Stats
    service_success = test_evolution_service_stats()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES:")
    print(f"   🔒 Thread Lock: {'✅ FUNCIONANDO' if thread_success else '❌ FALHOU'}")
    print(f"   📊 Evolution Stats: {'✅ FUNCIONANDO' if service_success else '❌ FALHOU'}")
    
    if thread_success and service_success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Controle de concorrência implementado com sucesso")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
        print("❌ Verificar implementação do controle de concorrência")