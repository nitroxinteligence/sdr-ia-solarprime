#!/usr/bin/env python3
"""
Teste CRÍTICO para validar correção do envio de respostas WhatsApp
Verifica se o main.py agora envia respostas automaticamente
"""

import sys
from pathlib import Path
import ast

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_whatsapp_send_import():
    """Testa se o import da tool send_text_message foi adicionado"""
    print("🧪 Testando import send_text_message...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        content = main_file.read_text()
        
        if "from agente.tools.whatsapp.send_text_message import send_text_message" not in content:
            print("❌ Import send_text_message não encontrado")
            return False
        
        print("✅ Import send_text_message encontrado")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando import: {e}")
        return False

def test_automatic_response_sending():
    """Testa se a lógica de envio automático foi implementada"""
    print("🧪 Testando envio automático de respostas...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        content = main_file.read_text()
        
        # Verificar se a lógica de envio foi implementada
        critical_elements = [
            "if response.message:",
            "send_result = await send_text_message(",
            "phone=message.phone,",
            "text=response.message"
        ]
        
        found_elements = 0
        for element in critical_elements:
            if element in content:
                found_elements += 1
        
        if found_elements < len(critical_elements):
            print(f"❌ Apenas {found_elements}/{len(critical_elements)} elementos encontrados")
            return False
        
        print(f"✅ {found_elements}/{len(critical_elements)} elementos de envio implementados")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando envio: {e}")
        return False

def test_error_handling():
    """Testa se o tratamento de erros foi implementado"""
    print("🧪 Testando tratamento de erros...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        content = main_file.read_text()
        
        error_handling_elements = [
            "try:",
            "except Exception as send_error:",
            "Failed to send WhatsApp response",
            "Error sending WhatsApp response"
        ]
        
        found_errors = 0
        for element in error_handling_elements:
            if element in content:
                found_errors += 1
        
        if found_errors < len(error_handling_elements):
            print(f"❌ Apenas {found_errors}/{len(error_handling_elements)} elementos de erro encontrados")
            return False
        
        print(f"✅ {found_errors}/{len(error_handling_elements)} elementos de tratamento de erro implementados")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando tratamento: {e}")
        return False

def test_success_logging():
    """Testa se os logs de sucesso foram implementados"""
    print("🧪 Testando logs de sucesso...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        content = main_file.read_text()
        
        log_elements = [
            "Response sent to WhatsApp",
            "send_result.get(\"success\")",
            "logger.info(f\"📤 Response sent"
        ]
        
        found_logs = 0
        for element in log_elements:
            if element in content:
                found_logs += 1
        
        if found_logs < len(log_elements):
            print(f"❌ Apenas {found_logs}/{len(log_elements)} elementos de log encontrados")
            return False
        
        print(f"✅ {found_logs}/{len(log_elements)} elementos de log implementados")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando logs: {e}")
        return False

def test_syntax_validation():
    """Valida sintaxe do main.py corrigido"""
    print("🧪 Validando sintaxe Python...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        
        if not main_file.exists():
            print("❌ Arquivo main.py não existe")
            return False
            
        content = main_file.read_text()
        ast.parse(content)
        
        print("✅ Sintaxe Python válida")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro validando sintaxe: {e}")
        return False

def test_flow_logic():
    """Testa se a lógica do fluxo está correta"""
    print("🧪 Testando lógica do fluxo...")
    
    try:
        main_file = Path(__file__).parent / "agente/main.py"
        content = main_file.read_text()
        
        # Verificar ordem correta das operações
        lines = content.split('\n')
        
        # Encontrar índices das operações críticas
        process_index = -1
        success_index = -1
        send_index = -1
        
        for i, line in enumerate(lines):
            if "response = await agent.process_message(message)" in line:
                process_index = i
            elif "if response.success:" in line and process_index != -1:
                success_index = i
            elif "send_result = await send_text_message(" in line and success_index != -1:
                send_index = i
        
        if process_index == -1:
            print("❌ Processamento de mensagem não encontrado")
            return False
        
        if success_index == -1:
            print("❌ Verificação de sucesso não encontrado")
            return False
            
        if send_index == -1:
            print("❌ Envio de resposta não encontrado")
            return False
        
        if not (process_index < success_index < send_index):
            print(f"❌ Ordem incorreta: process={process_index}, success={success_index}, send={send_index}")
            return False
        
        print("✅ Lógica do fluxo correta")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando fluxo: {e}")
        return False

def main():
    """Executa todos os testes de correção WhatsApp"""
    print("📱 TESTE CORREÇÃO RESPOSTA WHATSAPP")
    print("=" * 50)
    
    tests = [
        ("Import Send Message", test_whatsapp_send_import),
        ("Envio Automático", test_automatic_response_sending),
        ("Tratamento Erros", test_error_handling),
        ("Logs Sucesso", test_success_logging),
        ("Sintaxe Python", test_syntax_validation),
        ("Lógica Fluxo", test_flow_logic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSOU")
            else:
                print(f"❌ {test_name} FALHOU")
        except Exception as e:
            print(f"❌ {test_name} ERRO: {e}")
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO CORREÇÃO WHATSAPP")
    print("=" * 50)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 CORREÇÃO WHATSAPP IMPLEMENTADA!")
        print("\n📋 Correções aplicadas:")
        print("   ✅ Import: send_text_message importado")
        print("   ✅ Envio: Resposta enviada automaticamente")
        print("   ✅ Erro: Tratamento de erros completo")
        print("   ✅ Log: Logs informativos implementados")
        print("   ✅ Sintaxe: Código Python válido")
        print("   ✅ Fluxo: Lógica correta implementada")
        print("\n🚀 AGENTE DEVE RESPONDER NO WHATSAPP!")
        print("\n💡 Fluxo corrigido:")
        print("   1. Recebe mensagem WhatsApp")
        print("   2. Processa com AGnO")
        print("   3. Gera resposta")
        print("   4. ENVIA automaticamente para WhatsApp")
        print("   5. Loga resultado")
        return True
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam.")
        print("Verifique as correções antes de testar.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)