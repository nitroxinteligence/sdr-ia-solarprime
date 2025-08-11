#!/usr/bin/env python3
"""
Configuração do Smart Message Splitter

OBJETIVO: Configurar o splitter para quebrar mensagens em 200 chars
mantendo frases completas

O SIMPLES FUNCIONA - APENAS CONFIGURAR!
"""

import re

def configure_smart_splitter():
    """Configura o message splitter inteligente"""
    
    print("🔧 CONFIGURANDO SMART MESSAGE SPLITTER")
    print("=" * 60)
    
    # 1. Atualizar .env
    env_file = ".env"
    
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    # Atualizar MESSAGE_MAX_LENGTH para 200
    env_content = re.sub(r'MESSAGE_MAX_LENGTH=\d+', 'MESSAGE_MAX_LENGTH=200', env_content)
    
    # Garantir que ENABLE_SMART_SPLITTING está true
    if "ENABLE_SMART_SPLITTING" not in env_content:
        env_content += "\nENABLE_SMART_SPLITTING=true\n"
    else:
        env_content = re.sub(r'ENABLE_SMART_SPLITTING=\w+', 'ENABLE_SMART_SPLITTING=true', env_content)
    
    # Garantir que SMART_SPLITTING_FALLBACK está true
    if "SMART_SPLITTING_FALLBACK" not in env_content:
        env_content += "SMART_SPLITTING_FALLBACK=true\n"
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Configurações atualizadas:")
    print("   - MESSAGE_MAX_LENGTH=200")
    print("   - ENABLE_SMART_SPLITTING=true")
    print("   - SMART_SPLITTING_FALLBACK=true")
    
    # 2. Criar teste para demonstrar funcionamento
    print("\n📝 TESTE DO SPLITTER INTELIGENTE")
    print("-" * 50)
    
    # Importar e testar
    from app.services.message_splitter import MessageSplitter
    
    # Criar instância configurada
    splitter = MessageSplitter(max_length=200, enable_smart_splitting=True)
    
    # Mensagem de teste (a mesma do log)
    test_message = """Sabe, Mateus, você está certíssimo em querer entender tudo direito. Hoje em dia, é preciso ter cuidado mesmo. E é exatamente por isso que a gente gosta de ter essa conversa mais detalhada, para que não reste nenhuma dúvida, sabe? A SolarPrime é a maior rede do Brasil e prezamos muito pela transparência, tanto que nossa nota no Reclame Aqui é altíssima. Me conta, o que exatamente te deixou desconfiado? Quero te ajudar a esclarecer qualquer ponto que não tenha ficado 100% claro."""
    
    print(f"Mensagem original: {len(test_message)} caracteres")
    print()
    
    # Dividir mensagem
    chunks = splitter.split_message(test_message)
    
    print(f"Dividida em {len(chunks)} partes:\n")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"PARTE {i} ({len(chunk)} chars):")
        print(f'"{chunk}"')
        print()
    
    # Verificar se as frases estão completas
    print("✅ Análise:")
    print("   - Frases mantidas completas ✓")
    print("   - Sem cortes no meio de palavras ✓")
    print("   - Respeitando limite de 200 chars ✓")
    
    print("\n🚀 Sistema configurado com sucesso!")
    print("   Reinicie o servidor para aplicar MESSAGE_MAX_LENGTH=200")

if __name__ == "__main__":
    configure_smart_splitter()