#!/usr/bin/env python3
"""
Teste específico para race conditions críticos relatados em produção.

Foca especificamente em:
1. "duplicate key value violates unique constraint 'conversations_session_id_key'"
2. "WhatsAppMessage object has no field 'conversation_id'"
3. Validação das correções UPSERT e context dict

Execução: python test_critical_race_conditions.py
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import List, Dict
import random

class CriticalRaceConditionTester:
    """Tester focado nos race conditions críticos específicos"""
    
    def __init__(self):
        self.results = {
            "constraint_violation_tests": {
                "total": 0,
                "detected": 0,
                "details": []
            },
            "pydantic_field_tests": {
                "total": 0,
                "detected": 0,
                "details": []
            },
            "concurrent_same_session_tests": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "details": []
            },
            "performance_under_load": {
                "avg_response_time": 0,
                "max_response_time": 0,
                "timeouts": 0,
                "response_times": []
            }
        }
    
    async def test_session_id_constraint_violation(self, session: aiohttp.ClientSession):
        """
        Teste específico para constraint violation 'conversations_session_id_key'
        Envia múltiplas requisições com mesmo session_id simultaneamente
        """
        print("🔍 Testando constraint violation 'conversations_session_id_key'...")
        
        # Usar mesmo session_id para forçar race condition
        fixed_session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        phone = "5511999000001"
        
        # Criar múltiplas requisições simultâneas com mesmo session_id
        tasks = []
        for i in range(15):  # 15 requisições simultâneas
            payload = {
                "event": "messages.upsert",
                "instance": {
                    "instanceId": fixed_session_id,  # MESMO session_id para forçar race condition
                    "instanceName": "race_test"
                },
                "data": {
                    "key": {
                        "remoteJid": f"{phone}@s.whatsapp.net",
                        "fromMe": False,
                        "id": f"race_msg_{i}_{uuid.uuid4().hex[:6]}"
                    },
                    "message": {
                        "conversation": f"Mensagem de teste race condition #{i}"
                    },
                    "messageTimestamp": int(time.time()),
                    "pushName": "Race Test User",
                    "instanceId": fixed_session_id
                }
            }
            
            task = self._send_request_with_timing(session, payload, f"constraint_test_{i}")
            tasks.append(task)
        
        # Executar todas simultaneamente
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analisar resultados
        constraint_violations = 0
        for i, result in enumerate(results):
            self.results["constraint_violation_tests"]["total"] += 1
            
            if isinstance(result, dict) and result.get("error"):
                error_text = str(result["error"])
                if "duplicate key value violates unique constraint" in error_text and "session_id" in error_text:
                    constraint_violations += 1
                    self.results["constraint_violation_tests"]["detected"] += 1
                    self.results["constraint_violation_tests"]["details"].append({
                        "test_id": f"constraint_test_{i}",
                        "error": error_text,
                        "session_id": fixed_session_id,
                        "timestamp": datetime.now().isoformat()
                    })
        
        print(f"   📊 Constraint violations detectadas: {constraint_violations}/15")
        return constraint_violations
    
    async def test_pydantic_field_access_error(self, session: aiohttp.ClientSession):
        """
        Teste específico para 'WhatsAppMessage object has no field conversation_id'
        Envia requisições que podem causar tentativa de acesso ao campo conversation_id
        """
        print("🔍 Testando Pydantic field access error 'conversation_id'...")
        
        # Enviar requisições que podem causar o erro
        tasks = []
        for i in range(10):
            phone = f"5511999{i:06d}"
            payload = {
                "event": "messages.upsert",
                "instance": {
                    "instanceId": f"pydantic_test_{i}",  
                    "instanceName": "pydantic_test"
                },
                "data": {
                    "key": {
                        "remoteJid": f"{phone}@s.whatsapp.net",
                        "fromMe": False,
                        "id": f"pydantic_msg_{i}_{uuid.uuid4().hex[:6]}"
                    },
                    "message": {
                        "conversation": f"Teste pydantic field error #{i}"
                    },
                    "messageTimestamp": int(time.time()),
                    "pushName": f"Pydantic Test {i}",
                    "instanceId": f"pydantic_test_{i}"
                }
            }
            
            task = self._send_request_with_timing(session, payload, f"pydantic_test_{i}")
            tasks.append(task)
        
        # Executar todas simultaneamente
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analisar resultados
        pydantic_errors = 0
        for i, result in enumerate(results):
            self.results["pydantic_field_tests"]["total"] += 1
            
            if isinstance(result, dict) and result.get("error"):
                error_text = str(result["error"])
                if "WhatsAppMessage" in error_text and "conversation_id" in error_text:
                    pydantic_errors += 1
                    self.results["pydantic_field_tests"]["detected"] += 1
                    self.results["pydantic_field_tests"]["details"].append({
                        "test_id": f"pydantic_test_{i}",
                        "error": error_text,
                        "timestamp": datetime.now().isoformat()
                    })
        
        print(f"   📊 Pydantic field errors detectados: {pydantic_errors}/10")
        return pydantic_errors
    
    async def test_concurrent_same_phone_different_sessions(self, session: aiohttp.ClientSession):
        """
        Teste de múltiplas sessões para o mesmo telefone (cenário comum em produção)
        """
        print("🔍 Testando múltiplas sessões simultâneas para mesmo telefone...")
        
        phone = "5511999888888"  # Mesmo telefone
        tasks = []
        
        # Criar 8 sessões diferentes para o mesmo telefone
        for i in range(8):
            session_id = f"multi_session_{i}_{uuid.uuid4().hex[:6]}"
            payload = {
                "event": "messages.upsert",
                "instance": {
                    "instanceId": session_id,  # Sessões diferentes
                    "instanceName": "multi_session_test"
                },
                "data": {
                    "key": {
                        "remoteJid": f"{phone}@s.whatsapp.net",  # MESMO telefone
                        "fromMe": False,
                        "id": f"multi_msg_{i}_{uuid.uuid4().hex[:6]}"
                    },
                    "message": {
                        "conversation": f"Mensagem multi-sessão #{i}"
                    },
                    "messageTimestamp": int(time.time()),
                    "pushName": "Multi Session User",
                    "instanceId": session_id
                }
            }
            
            task = self._send_request_with_timing(session, payload, f"multi_session_test_{i}")
            tasks.append(task)
        
        # Executar todas simultaneamente
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analisar resultados
        successful = 0
        failed = 0
        
        for i, result in enumerate(results):
            self.results["concurrent_same_session_tests"]["total"] += 1
            
            if isinstance(result, dict):
                if result.get("success"):
                    successful += 1
                    self.results["concurrent_same_session_tests"]["successful"] += 1
                else:
                    failed += 1
                    self.results["concurrent_same_session_tests"]["failed"] += 1
                    self.results["concurrent_same_session_tests"]["details"].append({
                        "test_id": f"multi_session_test_{i}",
                        "error": result.get("error", "Unknown error"),
                        "timestamp": datetime.now().isoformat()
                    })
        
        print(f"   📊 Sucessos: {successful}/8, Falhas: {failed}/8")
        return successful, failed
    
    async def test_high_load_performance(self, session: aiohttp.ClientSession):
        """
        Teste de performance sob alta carga
        """
        print("🔍 Testando performance sob alta carga...")
        
        # 50 requisições rápidas
        tasks = []
        for i in range(50):
            phone = f"5511999{random.randint(100000, 999999)}"
            session_id = f"load_test_{i}_{uuid.uuid4().hex[:6]}"
            
            payload = {
                "event": "messages.upsert",
                "instance": {
                    "instanceId": session_id,
                    "instanceName": "load_test"
                },
                "data": {
                    "key": {
                        "remoteJid": f"{phone}@s.whatsapp.net",
                        "fromMe": False,
                        "id": f"load_msg_{i}_{uuid.uuid4().hex[:6]}"
                    },
                    "message": {
                        "conversation": f"Mensagem de carga #{i}"
                    },
                    "messageTimestamp": int(time.time()),
                    "pushName": f"Load Test {i}",
                    "instanceId": session_id
                }
            }
            
            task = self._send_request_with_timing(session, payload, f"load_test_{i}")
            tasks.append(task)
        
        # Executar todas simultaneamente
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Calcular métricas
        response_times = []
        timeouts = 0
        
        for result in results:
            if isinstance(result, dict) and result.get("response_time"):
                response_times.append(result["response_time"])
            elif isinstance(result, dict) and "timeout" in str(result.get("error", "")).lower():
                timeouts += 1
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            self.results["performance_under_load"]["avg_response_time"] = avg_response_time
            self.results["performance_under_load"]["max_response_time"] = max_response_time
            self.results["performance_under_load"]["response_times"] = response_times
        
        self.results["performance_under_load"]["timeouts"] = timeouts
        
        print(f"   📊 Tempo total: {total_time:.2f}s")
        print(f"   📊 Tempo médio de resposta: {avg_response_time:.2f}ms")
        print(f"   📊 Tempo máximo: {max_response_time:.2f}ms")
        print(f"   📊 Timeouts: {timeouts}/50")
        
        return avg_response_time, max_response_time, timeouts
    
    async def _send_request_with_timing(self, session: aiohttp.ClientSession, payload: dict, test_id: str):
        """Envia requisição com medição de tempo"""
        start_time = time.time()
        
        try:
            async with session.post(
                "http://localhost:8000/webhook/whatsapp",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response_time = (time.time() - start_time) * 1000  # ms
                
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "test_id": test_id,
                        "success": True,
                        "response_time": response_time,
                        "response": response_data
                    }
                else:
                    error_data = await response.text()
                    return {
                        "test_id": test_id,
                        "success": False,
                        "response_time": response_time,
                        "error": error_data,
                        "status_code": response.status
                    }
        
        except asyncio.TimeoutError:
            return {
                "test_id": test_id,
                "success": False,
                "error": "Request timeout",
                "response_time": (time.time() - start_time) * 1000
            }
        except Exception as e:
            return {
                "test_id": test_id,
                "success": False,
                "error": str(e),
                "response_time": (time.time() - start_time) * 1000
            }
    
    def print_final_report(self):
        """Imprime relatório final focado nos race conditions críticos"""
        print("\n" + "="*70)
        print("🎯 RELATÓRIO CRÍTICO - RACE CONDITIONS ESPECÍFICOS")
        print("="*70)
        
        # Constraint violations
        cv = self.results["constraint_violation_tests"]
        print(f"\n🔐 CONSTRAINT VIOLATIONS 'conversations_session_id_key':")
        print(f"   📊 Total de testes: {cv['total']}")
        print(f"   ❌ Violations detectadas: {cv['detected']}")
        
        if cv['detected'] == 0:
            print(f"   ✅ SUCESSO! UPSERT atômico funcionando corretamente")
        else:
            print(f"   ❌ FALHA! UPSERT precisa de mais ajustes")
            print(f"   🔍 Primeiros detalhes:")
            for detail in cv['details'][:3]:
                print(f"      - {detail['test_id']}: {detail['error'][:80]}...")
        
        # Pydantic errors
        pf = self.results["pydantic_field_tests"]
        print(f"\n🏷️  PYDANTIC FIELD ERRORS 'conversation_id':")
        print(f"   📊 Total de testes: {pf['total']}")
        print(f"   ❌ Errors detectados: {pf['detected']}")
        
        if pf['detected'] == 0:
            print(f"   ✅ SUCESSO! Context dict approach funcionando corretamente")
        else:
            print(f"   ❌ FALHA! Context dict precisa de mais ajustes")
            print(f"   🔍 Primeiros detalhes:")
            for detail in pf['details'][:3]:
                print(f"      - {detail['test_id']}: {detail['error'][:80]}...")
        
        # Concurrent sessions
        cs = self.results["concurrent_same_session_tests"]
        print(f"\n🔄 SESSÕES CONCORRENTES (mesmo telefone):")
        print(f"   📊 Total de testes: {cs['total']}")
        print(f"   ✅ Sucessos: {cs['successful']}")
        print(f"   ❌ Falhas: {cs['failed']}")
        
        if cs['failed'] == 0:
            print(f"   ✅ SUCESSO! Sessões concorrentes funcionando corretamente")
        else:
            print(f"   ⚠️  ATENÇÃO! {cs['failed']} falhas em sessões concorrentes")
        
        # Performance
        perf = self.results["performance_under_load"]
        print(f"\n⚡ PERFORMANCE SOB CARGA:")
        print(f"   📊 Tempo médio: {perf['avg_response_time']:.2f}ms")
        print(f"   📊 Tempo máximo: {perf['max_response_time']:.2f}ms")
        print(f"   📊 Timeouts: {perf['timeouts']}")
        
        # Veredicto final
        print(f"\n🎯 VEREDICTO FINAL:")
        fixes_working = (cv['detected'] == 0 and pf['detected'] == 0)
        
        if fixes_working:
            print(f"   ✅ TODAS AS CORREÇÕES FUNCIONANDO!")
            print(f"   🚀 Sistema pronto para produção")
        else:
            print(f"   ❌ CORREÇÕES PRECISAM DE AJUSTES!")
            if cv['detected'] > 0:
                print(f"      - UPSERT atômico ainda apresenta problemas")
            if pf['detected'] > 0:
                print(f"      - Context dict ainda apresenta problemas")
            print(f"   ⚠️  Não implantar em produção ainda")
        
        print("="*70)
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"critical_race_conditions_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"📄 Relatório detalhado salvo em: {filename}")

async def main():
    """Executa todos os testes críticos"""
    print("🧪 TESTE CRÍTICO DE RACE CONDITIONS")
    print("="*50)
    print("Testando especificamente os problemas relatados em produção:")
    print("1. duplicate key value violates unique constraint 'conversations_session_id_key'")
    print("2. WhatsAppMessage object has no field 'conversation_id'")
    print("="*50)
    
    # Verificar servidor
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    print("✅ Servidor detectado e rodando\n")
                else:
                    print(f"⚠️  Servidor respondeu com status {response.status}\n")
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        print("💡 Certifique-se de que o servidor está rodando em localhost:8000")
        return
    
    # Executar testes
    tester = CriticalRaceConditionTester()
    
    async with aiohttp.ClientSession() as session:
        # Teste 1: Constraint violations
        await tester.test_session_id_constraint_violation(session)
        await asyncio.sleep(1)  # Pausa entre testes
        
        # Teste 2: Pydantic field errors  
        await tester.test_pydantic_field_access_error(session)
        await asyncio.sleep(1)
        
        # Teste 3: Sessões concorrentes
        await tester.test_concurrent_same_phone_different_sessions(session)
        await asyncio.sleep(1)
        
        # Teste 4: Performance sob carga
        await tester.test_high_load_performance(session)
    
    # Gerar relatório final
    tester.print_final_report()

if __name__ == "__main__":
    asyncio.run(main())