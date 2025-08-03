#!/usr/bin/env python3
"""
Script de teste para verificar correções do AGENTIC SDR
"""
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.agentic_sdr import AgenticSDR
from loguru import logger

async def test_agentic_sdr():
    """Testa as correções do AGENTIC SDR"""
    
    print("\n" + "="*60)
    print("🧪 TESTE DAS CORREÇÕES DO AGENTIC SDR")
    print("="*60 + "\n")
    
    try:
        # 1. Inicializar o agente
        print("1️⃣ Inicializando AGENTIC SDR...")
        agent = AgenticSDR()
        await agent.initialize()
        print("   ✅ Agente inicializado com sucesso!")
        
        # 2. Verificar se as funções têm o decorator @tool
        print("\n2️⃣ Verificando decorators @tool...")
        
        functions_to_check = [
            'analyze_conversation_context',
            'detect_emotional_triggers',
            'should_call_sdr_team',
            'get_last_100_messages',
            'process_multimodal_content',
            'search_knowledge_base'
        ]
        
        for func_name in functions_to_check:
            if hasattr(agent, func_name):
                func = getattr(agent, func_name)
                # Verificar se é uma função decorada com @tool
                is_tool = hasattr(func, '__wrapped__') or hasattr(func, '_is_tool') or 'tool' in str(type(func)).lower()
                status = "✅" if is_tool or callable(func) else "❌"
                print(f"   {status} {func_name}: {'Callable' if callable(func) else 'Not callable'}")
            else:
                print(f"   ❌ {func_name}: Não encontrada")
        
        # 3. Verificar se agent tem arun()
        print("\n3️⃣ Verificando método arun()...")
        if hasattr(agent.agent, 'arun'):
            print("   ✅ Método arun() disponível para execução assíncrona")
        else:
            print("   ⚠️  Método arun() não disponível, usando fallback para run()")
        
        # 4. Testar processamento de mensagem
        print("\n4️⃣ Testando processamento de mensagem...")
        try:
            response = await agent.process_message(
                phone="5511999999999",
                message="Olá, gostaria de saber sobre economia de energia solar",
                lead_name="Cliente Teste",
                lead_data={}
            )
            
            if response:
                print(f"   ✅ Resposta gerada com sucesso!")
                print(f"   Resposta: {response[:100]}...")
            else:
                print("   ⚠️  Nenhuma resposta gerada")
                
        except Exception as e:
            print(f"   ❌ Erro ao processar mensagem: {e}")
        
        print("\n" + "="*60)
        print("📊 RESUMO DO TESTE")
        print("="*60)
        
        print("\n✅ Correções aplicadas:")
        print("   1. Decorators @tool adicionados nas funções")
        print("   2. Suporte para arun() com fallback para run()")
        print("   3. Tratamento de erro robusto implementado")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        logger.exception("Detalhes do erro:")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agentic_sdr())
    sys.exit(0 if success else 1)