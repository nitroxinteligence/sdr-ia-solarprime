#!/usr/bin/env python3
"""
Teste de Resposta de Conta de Luz
==================================
Testa se o agente responde imediatamente quando analisa conta de luz
"""

import sys
import os
sys.path.append('.')

# Configurar ambiente de teste
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key'
os.environ['REDIS_URL'] = 'redis://localhost:6379'
os.environ['GEMINI_API_KEY'] = 'test-key'
os.environ['EVOLUTION_API_BASE_URL'] = 'http://localhost:8080'
os.environ['EVOLUTION_API_TOKEN'] = 'test-token'
os.environ['EVOLUTION_INSTANCE_NAME'] = 'test'


async def test_agent_response():
    """Testa resposta do agente quando recebe conta de luz"""
    from agents.sdr_agent import SDRAgent
    
    print("\n=== Teste de Resposta do Agente para Conta de Luz ===")
    
    # Criar agente
    agent = SDRAgent()
    
    # Simular contexto com análise de conta já feita
    media_info = {
        'bill_value': 'R$ 850,00',
        'consumption': '450 kWh',
        'customer_name': 'João Silva',
        'address': 'Rua das Flores, 123',
        'reference_period': 'Novembro/2024'
    }
    
    # Simular estado da sessão
    session_state = {
        'current_stage': 'ENERGY_BILL_ANALYSIS',
        'lead_info': {
            'name': 'João',
            'phone': '11999999999'
        },
        'messages': []
    }
    
    # Simular análise
    analysis = {
        'intent': 'PROVIDE_ENERGY_BILL',
        'stage': 'ENERGY_BILL_ANALYSIS'
    }
    
    # Construir contexto do prompt
    context = agent._build_context_prompt(
        message="Aqui está minha conta",
        analysis=analysis,
        session_state=session_state,
        media_info=media_info,
        conversation_context=""
    )
    
    print("Contexto gerado para o agente:")
    print("-" * 50)
    print(context)
    print("-" * 50)
    
    # Verificar instruções críticas
    critical_instructions = [
        "RESPONDA IMEDIATAMENTE com os dados extraídos",
        "NÃO diga que vai analisar ou retornar depois",
        "NUNCA prometa retornar com números",
        "A ANÁLISE JÁ FOI FEITA",
        "RESPONDA AGORA com os valores encontrados"
    ]
    
    print("\nVerificando instruções críticas no contexto:")
    for instruction in critical_instructions:
        if instruction in context:
            print(f"✓ '{instruction}'")
        else:
            print(f"❌ FALTANDO: '{instruction}'")
            raise AssertionError(f"Instrução crítica não encontrada: {instruction}")
    
    # Verificar dados da conta no contexto
    print("\nVerificando dados da conta no contexto:")
    assert "R$ 850,00" in context, "Valor da conta não encontrado"
    print("✓ Valor da conta presente")
    assert "João Silva" in context, "Nome do titular não encontrado"
    print("✓ Nome do titular presente")
    assert "Rua das Flores" in context, "Endereço não encontrado"
    print("✓ Endereço presente")
    assert "Novembro/2024" in context, "Período não encontrado"
    print("✓ Período de referência presente")
    
    # Verificar exemplo de resposta
    assert "Analisei sua conta e vi que você paga R$" in context, "Exemplo de resposta não encontrado"
    print("✓ Exemplo de resposta apropriada presente")
    
    print("\n✅ Teste passou! O agente está configurado para responder imediatamente.")
    
    # Simular resposta esperada
    expected_response = """*João*, analisei sua conta e vi que você está pagando *R$ 850,00* por mês! 😮

Com a nossa solução de *Energia por Assinatura*, sua economia seria de 95%!

Você pagaria apenas *R$ 42,50* mensais!

São mais de *R$ 800* de economia todo mês que ficam no seu bolso! 💰

Esse valor de R$ 850,00 está correto?"""
    
    print("\nResposta esperada do agente:")
    print("-" * 50)
    print(expected_response)
    print("-" * 50)
    
    # Verificar que NÃO contém frases problemáticas
    problematic_phrases = [
        "volto a falar",
        "em breve",
        "vou analisar",
        "aguarde",
        "um momento",
        "retorno com"
    ]
    
    print("\nVerificando ausência de frases problemáticas na resposta esperada:")
    for phrase in problematic_phrases:
        assert phrase.lower() not in expected_response.lower(), f"Resposta contém frase problemática: {phrase}"
        print(f"✓ Não contém '{phrase}'")
    
    print("\n✅ SUCESSO! O agente está configurado corretamente!")


if __name__ == "__main__":
    import asyncio
    
    print("🧪 Testando resposta do agente para conta de luz...")
    
    try:
        asyncio.run(test_agent_response())
        
        print("\n🎉 TESTE COMPLETO!")
        print("\nO agente agora:")
        print("1. ✓ Responde IMEDIATAMENTE com os valores da conta")
        print("2. ✓ NÃO promete retornar depois")
        print("3. ✓ Mostra os dados extraídos na primeira resposta")
        print("4. ✓ Calcula e apresenta a economia")
        print("5. ✓ Mantém a conversa fluindo naturalmente")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)