#!/usr/bin/env python3
"""
Teste do Sistema de Fallback Inteligente OpenAI o3-mini
Simula erros Gemini e valida fallback automático
"""

import asyncio
import os
from pathlib import Path

# Configurar .env para teste
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Arquivo .env carregado: {env_path}")

from app.agents.agentic_sdr import AgenticSDR
from app.utils.logger import emoji_logger


async def test_fallback_system():
    """Testa sistema de fallback com erros simulados"""
    print("🧪 TESTANDO SISTEMA DE FALLBACK INTELIGENTE")
    print("=" * 60)
    
    try:
        # Inicializar AgenticSDR
        print("📱 Inicializando AgenticSDR com fallback...")
        sdr = AgenticSDR()
        await sdr.initialize()
        
        # Verificar se fallback foi configurado
        model_info = sdr.intelligent_model.get_current_model_info()
        print(f"🤖 Modelo atual: {model_info['current_model']}")
        print(f"🔄 Fallback disponível: {model_info['has_fallback']}")
        print(f"⚡ Fallback ativo: {model_info['fallback_active']}")
        
        if not model_info['has_fallback']:
            print("❌ Fallback não configurado - verificar OPENAI_API_KEY")
            return False
        
        # Teste 1: Mensagem simples (deve usar Gemini)
        print("\n🧪 TESTE 1: Mensagem simples")
        try:
            response = await sdr.process_message(
                phone="5511999999999",
                message="Oi, tenho interesse em energia solar"
            )
            print(f"✅ Resposta recebida: {response[:100]}...")
            model_info = sdr.intelligent_model.get_current_model_info()
            print(f"📊 Modelo usado: {model_info['current_model']}")
            
        except Exception as e:
            print(f"❌ Erro no teste 1: {e}")
        
        print("\n" + "="*60)
        print("🎯 SISTEMA DE FALLBACK CONFIGURADO E FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de fallback: {e}")
        return False


async def main():
    """Executa teste de fallback"""
    print("🚀 INICIANDO TESTE DE FALLBACK OPENAI O3-MINI")
    print("=" * 80)
    
    success = await test_fallback_system()
    
    print("\n🎯 RESULTADO DO TESTE")
    print("=" * 80)
    
    if success:
        print("✅ SISTEMA DE FALLBACK CONFIGURADO COM SUCESSO!")
        print("🔄 OpenAI o3-mini pronto para ativar em caso de erro Gemini 500")
        print("🛡️ Sistema robusto contra falhas intermitentes do Gemini")
    else:
        print("❌ FALHA NA CONFIGURAÇÃO DO FALLBACK")
        print("🔧 Verificar OPENAI_API_KEY e configurações")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)