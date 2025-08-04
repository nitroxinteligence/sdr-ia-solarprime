#!/usr/bin/env python3
"""
Teste do Sistema de Retry + Fallback Inteligente
Testa o fluxo: Gemini → Retry (5s delay) → Fallback OpenAI
"""

import asyncio
import os
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Configurar .env para teste
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Arquivo .env carregado: {env_path}")

from app.agents.agentic_sdr import IntelligentModelFallback
from app.config import settings
from app.utils.logger import emoji_logger


async def test_retry_system():
    """Testa o sistema de retry com diferentes cenários"""
    print("🧪 TESTANDO SISTEMA DE RETRY + FALLBACK")
    print("=" * 80)
    
    # Configurar modelo
    fallback_system = IntelligentModelFallback(settings)
    
    # Obter informações do sistema
    model_info = fallback_system.get_current_model_info()
    print(f"🤖 Modelo primário: {model_info['current_model']}")
    print(f"🔄 Fallback disponível: {model_info['has_fallback']}")
    print(f"⏱️ Retry configurado: {fallback_system.max_retry_attempts} tentativas")
    print(f"⏰ Delay entre tentativas: {fallback_system.retry_delay}s")
    print()
    
    # TESTE 1: Operação normal (sem erro)
    print("📝 TESTE 1: Operação normal (sem erro)")
    print("-" * 40)
    try:
        response = await fallback_system.run("Olá, teste simples")
        print(f"✅ Resposta recebida com sucesso")
        print(f"📍 Modelo usado: {fallback_system.get_current_model_info()['current_model']}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # TESTE 2: Simular erro temporário do Gemini (com mock)
    print("📝 TESTE 2: Simulando erro 500 do Gemini (ativará retry)")
    print("-" * 40)
    
    # Salvar referência original
    original_invoke = fallback_system.primary_model.invoke if fallback_system.primary_model else None
    
    if original_invoke:
        # Contador de tentativas
        attempt_count = 0
        
        def mock_gemini_error(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            
            # Falha nas primeiras 2 tentativas, sucesso na 3ª
            if attempt_count <= 2:
                print(f"   ⚠️ Simulando erro 500 (tentativa {attempt_count})")
                raise Exception("500 Internal Server Error - Simulated")
            else:
                print(f"   ✅ Gemini recuperado na tentativa {attempt_count}")
                return "Resposta simulada após retry"
        
        # Aplicar mock
        fallback_system.primary_model.invoke = mock_gemini_error
        
        try:
            start_time = datetime.now()
            response = await fallback_system.run("Teste com retry")
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ Sistema recuperou com retry!")
            print(f"⏱️ Tempo total: {duration:.1f}s")
            print(f"📍 Tentativas: {attempt_count}")
            
        except Exception as e:
            print(f"❌ Erro após retry: {e}")
        
        # Restaurar método original
        fallback_system.primary_model.invoke = original_invoke
    else:
        print("⚠️ Modelo primário não disponível para teste")
    
    print()
    
    # TESTE 3: Testar fallback real (se configurado)
    if model_info['has_fallback']:
        print("📝 TESTE 3: Testando fallback para OpenAI (erro persistente)")
        print("-" * 40)
        
        # Mock para forçar erro persistente
        def mock_persistent_error(*args, **kwargs):
            raise Exception("503 Service Unavailable - Persistent error")
        
        if fallback_system.primary_model:
            original_invoke = fallback_system.primary_model.invoke
            fallback_system.primary_model.invoke = mock_persistent_error
            
            try:
                response = await fallback_system.run("Teste com fallback")
                print(f"✅ Fallback ativado com sucesso!")
                print(f"📍 Modelo atual: {fallback_system.get_current_model_info()['current_model']}")
                print(f"⚡ Fallback ativo: {fallback_system.get_current_model_info()['fallback_active']}")
            except Exception as e:
                print(f"❌ Erro no fallback: {e}")
            
            # Restaurar
            fallback_system.primary_model.invoke = original_invoke
            fallback_system.reset_to_primary()
    else:
        print("⚠️ Fallback não configurado (OPENAI_API_KEY necessária)")
    
    print()
    print("=" * 80)
    print("🎯 TESTE CONCLUÍDO")
    
    # Resumo
    print("\n📊 RESUMO DO SISTEMA:")
    print(f"  • Retry configurado: {fallback_system.max_retry_attempts} tentativas com {fallback_system.retry_delay}s de delay")
    print(f"  • Fallback disponível: {'✅ Sim' if model_info['has_fallback'] else '❌ Não'}")
    print(f"  • Fluxo: Gemini → Retry ({fallback_system.max_retry_attempts}x) → {'OpenAI o3-mini' if model_info['has_fallback'] else 'Sem fallback'}")


async def main():
    """Executa os testes"""
    print("🚀 INICIANDO TESTE DO SISTEMA DE RETRY + FALLBACK")
    print("=" * 80)
    print()
    
    await test_retry_system()
    
    print("\n✅ TESTE FINALIZADO COM SUCESSO!")


if __name__ == "__main__":
    asyncio.run(main())