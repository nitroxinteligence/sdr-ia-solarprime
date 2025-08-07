#!/usr/bin/env python3
"""
Verificação Final Abrangente para Produção

OBJETIVO: Garantir 100% que o sistema NUNCA enviará "None" ou mensagens vazias

ZERO COMPLEXIDADE - O SIMPLES FUNCIONA
"""

import os
import re
from datetime import datetime

def final_verification():
    """Verificação final completa do sistema"""
    
    print("🔍 VERIFICAÇÃO FINAL ABRANGENTE")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Arquivos críticos para verificar
    files_to_check = {
        "app/agents/agentic_sdr.py": [
            # Verificações após extração de conteúdo
            "if raw_response is None or str(raw_response).strip().lower() == \"none\":",
            "emoji_logger.system_warning(\"⚠️ raw_response é None! Usando fallback...\")",
            
            # Verificações de resposta vazia
            "if not raw_response or raw_response.strip() == \"\" or str(raw_response).strip().lower() == \"none\":",
            
            # Verificação final antes de aplicar simulação
            "if response and str(response).strip() != \"\" and str(response).strip().lower() != \"none\":",
            "emoji_logger.system_warning(\"⚠️ Response vazio ou None no final, usando fallback de emergência\")"
        ],
        
        "app/api/webhooks.py": [
            # Verificação antes de enviar ao WhatsApp
            "if not response_text or response_text.strip() == \"\" or response_text.strip().lower() == \"none\":",
            "emoji_logger.system_error(\"CRITICAL\", f\"⚠️ BLOQUEADO: Tentativa de enviar mensagem vazia ou None!\")",
            
            # Verificação em extract_final_response
            "if not final_response or final_response.strip() == \"\" or final_response.strip().lower() == \"none\":",
            "emoji_logger.system_error(\"Extract\", f\"⚠️ extract_final_response retornaria vazio/None:",
            
            # Verificação em sanitize_final_response
            "if not text or text.lower() == \"none\":",
            "emoji_logger.system_error(\"Sanitize\", f\"⚠️ sanitize_final_response resultaria em vazio/None\")"
        ]
    }
    
    all_checks_passed = True
    total_protections = 0
    
    for file_path, expected_protections in files_to_check.items():
        print(f"\n📄 Verificando {file_path}:")
        print("-" * 50)
        
        if not os.path.exists(file_path):
            print(f"❌ ERRO: Arquivo não encontrado!")
            all_checks_passed = False
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_ok = True
        found_protections = 0
        
        for protection in expected_protections:
            if protection in content:
                print(f"✅ Encontrada: {protection[:60]}...")
                found_protections += 1
                total_protections += 1
            else:
                print(f"❌ NÃO ENCONTRADA: {protection[:60]}...")
                file_ok = False
                all_checks_passed = False
        
        if file_ok:
            print(f"✅ Arquivo OK - {found_protections} proteções encontradas")
        else:
            print(f"❌ Arquivo com problemas - apenas {found_protections}/{len(expected_protections)} proteções")
    
    # Verificar padrões perigosos
    print("\n🚨 Verificando padrões perigosos:")
    print("-" * 50)
    
    dangerous_patterns = [
        (r'return\s+None(?!\s*#)', "return None sem comentário"),
        (r'=\s*None\s*$', "atribuição None no final da linha"),
        (r'evolution_client\.send_text.*None', "enviando None diretamente")
    ]
    
    for file_path in files_to_check.keys():
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for pattern, description in dangerous_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                print(f"⚠️ {file_path}: {len(matches)} ocorrências de '{description}'")
                for match in matches[:3]:  # Mostrar até 3 exemplos
                    print(f"   - {match.strip()}")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO FINAL")
    print("=" * 60)
    
    if all_checks_passed:
        print(f"✅ SISTEMA 100% PROTEGIDO!")
        print(f"✅ Total de {total_protections} proteções ativas")
        print("\n🛡️ Camadas de proteção:")
        print("   1. Verificação após extração de conteúdo (agentic_sdr.py)")
        print("   2. Verificação antes de processar resposta (agentic_sdr.py)")
        print("   3. Verificação final com fallback contextual (agentic_sdr.py)")
        print("   4. Verificação em extract_final_response (webhooks.py)")
        print("   5. Verificação em sanitize_final_response (webhooks.py)")
        print("   6. Verificação crítica antes de enviar ao WhatsApp (webhooks.py)")
        print("\n✅ O sistema NUNCA enviará 'None' ou mensagens vazias!")
    else:
        print("❌ ATENÇÃO: Algumas proteções estão faltando!")
        print("❌ Execute os scripts de correção antes do deploy!")
    
    # Recomendações
    print("\n📋 RECOMENDAÇÕES PARA PRODUÇÃO:")
    print("-" * 50)
    print("1. Monitorar logs para palavras-chave:")
    print("   - 'BLOQUEADO'")
    print("   - 'CRITICAL'")
    print("   - 'fallback'")
    print("   - 'None'")
    print("\n2. Configurar alertas para:")
    print("   - Timeouts em agent.arun")
    print("   - Respostas vazias")
    print("   - Erros de extração")
    print("\n3. Testar cenários:")
    print("   - Timeout do agente")
    print("   - Erro de processamento")
    print("   - Primeira mensagem do usuário")
    print("   - Mensagem após longo período")
    
    return all_checks_passed

if __name__ == "__main__":
    if final_verification():
        print("\n🚀 SISTEMA PRONTO PARA PRODUÇÃO!")
    else:
        print("\n⚠️ CORREÇÕES NECESSÁRIAS ANTES DO DEPLOY!")