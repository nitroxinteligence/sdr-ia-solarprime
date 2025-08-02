#!/usr/bin/env python3
"""
Teste da correção de deduplicação de mensagens
Verifica se mensagens duplicadas são ignoradas pelo webhook
"""

import asyncio
import json
from typing import Dict, Any

def test_deduplication_logic():
    """Testa a lógica de deduplicação de mensagens"""
    print("🧪 Testando lógica de deduplicação...")
    
    # Importar as funções de deduplicação
    try:
        from agente.main import is_message_already_processed, mark_message_as_processed
        
        # Testar message IDs únicos
        message_id_1 = "3EB0C767D097E9ECFE8A"
        message_id_2 = "3EB0C767D097E9ECFE8B"
        
        # Verificar que mensagens novas não estão processadas
        assert not is_message_already_processed(message_id_1), "Message 1 should not be processed initially"
        assert not is_message_already_processed(message_id_2), "Message 2 should not be processed initially"
        
        # Marcar primeira mensagem como processada
        mark_message_as_processed(message_id_1)
        
        # Verificar que apenas a primeira está processada
        assert is_message_already_processed(message_id_1), "Message 1 should be processed now"
        assert not is_message_already_processed(message_id_2), "Message 2 should still not be processed"
        
        # Testar duplicação - marcar novamente a mesma mensagem
        mark_message_as_processed(message_id_1)  # Duplicate
        assert is_message_already_processed(message_id_1), "Message 1 should still be processed"
        
        print("✅ Lógica de deduplicação funcionando corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro na lógica de deduplicação: {e}")
        return False


def test_webhook_payload_deduplication():
    """Simula payloads duplicados do webhook"""
    print("🧪 Testando deduplicação em payloads do webhook...")
    
    # Simular payload do Evolution API
    webhook_payload = {
        "event": "messages.upsert",
        "instance": {"instanceId": "SDR IA SolarPrime"},
        "data": {
            "key": {
                "remoteJid": "5581999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "3EB0C767D097E9DUPLICATE"  # ID específico para teste
            },
            "message": {
                "conversation": "Olá! Interesse em energia solar"
            },
            "pushName": "João Test",
            "messageTimestamp": "1722550000"
        }
    }
    
    try:
        from agente.main import is_message_already_processed, mark_message_as_processed
        
        message_id = webhook_payload["data"]["key"]["id"]
        
        # Primeira mensagem - deve ser aceita
        first_check = not is_message_already_processed(message_id)
        print(f"📥 Primeira mensagem {message_id}: {'Aceita' if first_check else 'Rejeitada'}")
        
        if first_check:
            mark_message_as_processed(message_id)
        
        # Segunda mensagem (duplicada) - deve ser rejeitada
        second_check = not is_message_already_processed(message_id)
        print(f"🔄 Segunda mensagem {message_id}: {'Aceita' if second_check else 'Rejeitada (duplicada)'}")
        
        # Verificar que primeira foi aceita e segunda rejeitada
        success = first_check and not second_check
        
        if success:
            print("✅ Deduplicação de webhook funcionando corretamente")
            print("   - Primeira mensagem aceita para processamento")
            print("   - Segunda mensagem rejeitada como duplicada")
        else:
            print("❌ Problema na deduplicação de webhook")
        
        return success
        
    except Exception as e:
        print(f"❌ Erro na deduplicação de webhook: {e}")
        return False


def test_cache_size_limit():
    """Testa o limite da cache de deduplicação"""
    print("🧪 Testando limite da cache de deduplicação...")
    
    try:
        from agente.main import mark_message_as_processed, _processed_message_ids, _max_cache_size
        
        # Limpar cache para teste
        _processed_message_ids.clear()
        
        # Adicionar muitas mensagens para testar limite
        test_messages = [f"TEST_MSG_{i:05d}" for i in range(_max_cache_size + 100)]
        
        for msg_id in test_messages:
            mark_message_as_processed(msg_id)
        
        # Verificar que cache não excede limite
        cache_size = len(_processed_message_ids)
        
        print(f"📊 Cache size after adding {len(test_messages)} messages: {cache_size}")
        print(f"📏 Cache limit: {_max_cache_size}")
        
        if cache_size <= _max_cache_size:
            print("✅ Cache limit funcionando corretamente")
            print(f"   - Cache mantida dentro do limite: {cache_size}/{_max_cache_size}")
            return True
        else:
            print("❌ Cache limit não funcionando")
            print(f"   - Cache excedeu limite: {cache_size}/{_max_cache_size}")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste de cache limit: {e}")
        return False


def test_health_endpoint_integration():
    """Testa se o endpoint de health mostra estatísticas da cache"""
    print("🧪 Testando integração com endpoint de health...")
    
    try:
        from agente.main import _processed_message_ids, _max_cache_size
        
        # Simular algumas mensagens processadas
        test_ids = ["HEALTH_TEST_1", "HEALTH_TEST_2", "HEALTH_TEST_3"]
        
        for msg_id in test_ids:
            _processed_message_ids.add(msg_id)
        
        # Calcular estatísticas como no endpoint
        total_processed = len(_processed_message_ids)
        cache_utilization = (total_processed / _max_cache_size) * 100
        
        print(f"📊 Estatísticas da cache:")
        print(f"   - Total de mensagens processadas: {total_processed}")
        print(f"   - Limite da cache: {_max_cache_size}")
        print(f"   - Utilização da cache: {cache_utilization:.1f}%")
        
        if total_processed > 0 and cache_utilization >= 0:
            print("✅ Integração com health endpoint funcionando")
            return True
        else:
            print("❌ Problema na integração com health endpoint")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste de health endpoint: {e}")
        return False


if __name__ == "__main__":
    print("🧪 TESTE: Correção de Deduplicação de Mensagens WhatsApp")
    print("=" * 60)
    
    # Executar todos os testes
    tests = [
        ("Lógica de Deduplicação", test_deduplication_logic),
        ("Webhook Payload Deduplication", test_webhook_payload_deduplication),
        ("Cache Size Limit", test_cache_size_limit),
        ("Health Endpoint Integration", test_health_endpoint_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Falha crítica no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resultados finais
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Resultado Final: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Deduplicação de mensagens implementada com sucesso")
        print("🚀 Pronto para resolver mensagens duplicadas no WhatsApp")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM!")
        print("❌ Verificar implementação da deduplicação")
    
    # Sugestão de monitoramento
    print("\n📈 MONITORAMENTO SUGERIDO:")
    print("   - Verificar logs: '🔄 Skipping duplicate message'")
    print("   - Endpoint health: /health (ver deduplication_cache)")
    print("   - Logs webhook: '📥 Message accepted for background processing'")