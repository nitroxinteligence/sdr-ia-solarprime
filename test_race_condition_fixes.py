#!/usr/bin/env python3
"""
Script de teste para validar correções de race conditions.

Simula múltiplas requisições simultâneas para testar:
1. UPSERT atômico no Supabase
2. Context dict approach para conversation_id
3. Error handling robusto
4. AGnO async optimization

Execução: python test_race_condition_fixes.py
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import random

# Configurações do teste
WEBHOOK_URL = "http://localhost:8000/webhook/whatsapp"
CONCURRENCY_LEVEL = 10  # Número de requisições simultâneas
TEST_DURATION_SECONDS = 30
PHONE_NUMBERS = [f"5511999{i:06d}" for i in range(100, 110)]  # 10 números de teste

class RaceConditionTester:
    """Classe para testar race conditions nas correções implementadas"""
    
    def __init__(self):
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "constraint_violations": 0,
            "pydantic_errors": 0,
            "other_errors": 0,
            "response_times": [],
            "error_details": []
        }
        self.start_time = time.time()
    
    def generate_webhook_payload(self, phone: str, message_content: str = None) -> Dict[str, Any]:
        """Gera payload de webhook Evolution API realístico"""
        message_id = f"msg_{uuid.uuid4().hex[:10]}"
        timestamp = int(time.time())
        
        if not message_content:
            messages = [
                "Olá, tenho interesse em energia solar",
                "Qual o valor da instalação?",
                "Vocês fazem financiamento?",
                "Quando posso agendar uma visita?",
                "Preciso de mais informações"
            ]
            message_content = random.choice(messages)
        
        # Payload realístico baseado na Evolution API v2
        return {
            "event": "messages.upsert",
            "instance": {
                "instanceId": "test_instance",
                "instanceName": "test_solar_prime"
            },
            "data": {
                "key": {
                    "remoteJid": f"{phone}@s.whatsapp.net",
                    "fromMe": False,
                    "id": message_id
                },
                "message": {
                    "conversation": message_content
                },
                "messageTimestamp": timestamp,
                "pushName": f"Lead {phone[-4:]}",
                "instanceId": "test_instance"
            }
        }
    
    async def send_webhook_request(
        self, 
        session: aiohttp.ClientSession, 
        phone: str, 
        request_id: int
    ) -> Dict[str, Any]:
        """Envia uma requisição de webhook"""
        payload = self.generate_webhook_payload(phone)
        
        start_time = time.time()
        try:
            async with session.post(
                WEBHOOK_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = (time.time() - start_time) * 1000  # ms
                
                self.results["total_requests"] += 1
                self.results["response_times"].append(response_time)
                
                response_data = await response.json()
                
                if response.status == 200:
                    self.results["successful_requests"] += 1
                    return {
                        "request_id": request_id,
                        "phone": phone,
                        "status": "success",
                        "response_time_ms": response_time,
                        "response": response_data
                    }
                else:
                    # Analisar tipo de erro
                    error_text = str(response_data)
                    
                    if "duplicate key value violates unique constraint" in error_text:
                        self.results["constraint_violations"] += 1
                        error_type = "constraint_violation"
                    elif "WhatsAppMessage" in error_text and "conversation_id" in error_text:
                        self.results["pydantic_errors"] += 1
                        error_type = "pydantic_field_error"
                    else:
                        self.results["other_errors"] += 1
                        error_type = "other_error"
                    
                    error_detail = {
                        "request_id": request_id,
                        "phone": phone,
                        "error_type": error_type,
                        "status_code": response.status,
                        "error": error_text[:500],  # Limitar tamanho
                        "response_time_ms": response_time
                    }
                    
                    self.results["error_details"].append(error_detail)
                    
                    return {
                        "request_id": request_id,
                        "phone": phone,
                        "status": "error",
                        "error_type": error_type,
                        "response_time_ms": response_time
                    }
        
        except asyncio.TimeoutError:
            self.results["other_errors"] += 1
            error_detail = {
                "request_id": request_id,
                "phone": phone,
                "error_type": "timeout",
                "error": "Request timeout after 10s"
            }
            self.results["error_details"].append(error_detail)
            
            return {
                "request_id": request_id,
                "phone": phone,
                "status": "timeout"
            }
        
        except Exception as e:
            self.results["other_errors"] += 1
            error_detail = {
                "request_id": request_id,
                "phone": phone,
                "error_type": "connection_error",
                "error": str(e)[:500]
            }
            self.results["error_details"].append(error_detail)
            
            return {
                "request_id": request_id,
                "phone": phone,
                "status": "connection_error",
                "error": str(e)
            }
    
    async def simulate_concurrent_requests(self, duration_seconds: int = 30):
        """Simula múltiplas requisições simultâneas"""
        print(f"🚀 Iniciando simulação de race conditions...")
        print(f"   - Duração: {duration_seconds}s")
        print(f"   - Concorrência: {CONCURRENCY_LEVEL}")
        print(f"   - Números de teste: {len(PHONE_NUMBERS)}")
        print(f"   - URL: {WEBHOOK_URL}")
        
        end_time = time.time() + duration_seconds
        request_id = 0
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                # Criar batch de requisições simultâneas
                tasks = []
                
                for _ in range(CONCURRENCY_LEVEL):
                    # Usar o mesmo número às vezes para forçar race conditions
                    if random.random() < 0.3:  # 30% chance de usar o mesmo número
                        phone = random.choice(PHONE_NUMBERS[:3])  # Usar apenas os 3 primeiros
                    else:
                        phone = random.choice(PHONE_NUMBERS)
                    
                    task = self.send_webhook_request(session, phone, request_id)
                    tasks.append(task)
                    request_id += 1
                
                # Executar batch simultaneamente
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log progresso
                elapsed = time.time() - self.start_time
                print(f"⏱️  {elapsed:.1f}s - Batch completo: {len(batch_results)} requests")
                
                # Pequena pausa entre batches
                await asyncio.sleep(0.1)
        
        print(f"✅ Simulação completa!")
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório detalhado dos testes"""
        total_time = time.time() - self.start_time
        
        # Calcular estatísticas de response time
        response_times = self.results["response_times"]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calcular taxa de sucesso
        success_rate = (
            self.results["successful_requests"] / self.results["total_requests"] 
            if self.results["total_requests"] > 0 else 0
        ) * 100
        
        report = {
            "test_summary": {
                "total_duration_seconds": round(total_time, 2),
                "total_requests": self.results["total_requests"],
                "requests_per_second": round(self.results["total_requests"] / total_time, 2),
                "success_rate_percent": round(success_rate, 2)
            },
            "performance_metrics": {
                "average_response_time_ms": round(avg_response_time, 2),
                "min_response_time_ms": min(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "total_successful_requests": self.results["successful_requests"]
            },
            "error_analysis": {
                "constraint_violations": self.results["constraint_violations"],
                "pydantic_field_errors": self.results["pydantic_errors"],
                "other_errors": self.results["other_errors"],
                "total_errors": (
                    self.results["constraint_violations"] + 
                    self.results["pydantic_errors"] + 
                    self.results["other_errors"]
                )
            },
            "race_condition_analysis": {
                "expected_race_conditions": "constraint_violations should be 0 after UPSERT fixes",
                "expected_pydantic_errors": "pydantic_field_errors should be 0 after context dict fixes",
                "constraint_violations_detected": self.results["constraint_violations"],
                "pydantic_errors_detected": self.results["pydantic_errors"],
                "fixes_working": (
                    self.results["constraint_violations"] == 0 and 
                    self.results["pydantic_errors"] == 0
                )
            },
            "detailed_errors": self.results["error_details"][:10]  # Primeiros 10 erros
        }
        
        return report
    
    def print_report(self):
        """Imprime relatório formatado"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE TESTE - RACE CONDITIONS")
        print("="*60)
        
        # Resumo do teste
        summary = report["test_summary"]
        print(f"\n🎯 RESUMO DO TESTE:")
        print(f"   ⏱️  Duração: {summary['total_duration_seconds']}s")
        print(f"   📨 Total de requisições: {summary['total_requests']}")
        print(f"   ⚡ Requisições/segundo: {summary['requests_per_second']}")
        print(f"   ✅ Taxa de sucesso: {summary['success_rate_percent']}%")
        
        # Métricas de performance
        perf = report["performance_metrics"]
        print(f"\n⚡ PERFORMANCE:")
        print(f"   📊 Tempo médio de resposta: {perf['average_response_time_ms']}ms")
        print(f"   🚀 Tempo mínimo: {perf['min_response_time_ms']}ms")
        print(f"   🐌 Tempo máximo: {perf['max_response_time_ms']}ms")
        print(f"   ✅ Requisições bem-sucedidas: {perf['total_successful_requests']}")
        
        # Análise de erros
        errors = report["error_analysis"]
        print(f"\n❌ ANÁLISE DE ERROS:")
        print(f"   🔐 Constraint violations: {errors['constraint_violations']}")
        print(f"   🏷️  Pydantic field errors: {errors['pydantic_field_errors']}")
        print(f"   ❓ Outros erros: {errors['other_errors']}")
        print(f"   📊 Total de erros: {errors['total_errors']}")
        
        # Análise de race conditions
        race = report["race_condition_analysis"]
        print(f"\n🏁 ANÁLISE DE RACE CONDITIONS:")
        print(f"   🎯 Constraint violations detectadas: {race['constraint_violations_detected']}")
        print(f"   🎯 Pydantic errors detectados: {race['pydantic_errors_detected']}")
        
        if race["fixes_working"]:
            print(f"   ✅ CORREÇÕES FUNCIONANDO! Nenhum race condition detectado.")
        else:
            print(f"   ❌ CORREÇÕES PRECISAM DE AJUSTES!")
            if race["constraint_violations_detected"] > 0:
                print(f"      - UPSERT atômico ainda apresenta problemas")
            if race["pydantic_errors_detected"] > 0:
                print(f"      - Context dict approach ainda apresenta problemas")
        
        # Detalhes de erros se houver
        if report["detailed_errors"]:
            print(f"\n🔍 PRIMEIROS ERROS DETECTADOS:")
            for i, error in enumerate(report["detailed_errors"][:5], 1):
                print(f"   {i}. Tipo: {error.get('error_type', 'unknown')}")
                print(f"      Telefone: {error.get('phone', 'unknown')}")
                print(f"      Erro: {error.get('error', 'No details')[:100]}...")
        
        print("\n" + "="*60)
        
        # Salvar relatório em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"race_condition_test_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"📄 Relatório salvo em: {filename}")

async def main():
    """Função principal do teste"""
    print("🧪 TESTADOR DE RACE CONDITIONS - SDR IA SOLARPRIME")
    print("="*60)
    
    # Verificar se o servidor está rodando
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    print("✅ Servidor detectado e rodando")
                else:
                    print(f"⚠️  Servidor respondeu com status {response.status}")
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        print("💡 Certifique-se de que o servidor está rodando em localhost:8000")
        return
    
    # Executar testes
    tester = RaceConditionTester()
    await tester.simulate_concurrent_requests(TEST_DURATION_SECONDS)
    
    # Gerar e imprimir relatório
    tester.print_report()

if __name__ == "__main__":
    # Executar teste
    asyncio.run(main())