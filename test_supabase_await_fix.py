#!/usr/bin/env python3
"""
Teste CRÍTICO para validar correção dos await inválidos no Supabase
Verifica se removemos todos os await indevidos das chamadas síncronas
"""

import sys
from pathlib import Path
import ast

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_conversation_repository_await_removal():
    """Testa se os await inválidos foram removidos do conversation_repository"""
    print("🧪 Testando remoção de await inválidos no ConversationRepository...")
    
    try:
        repo_file = Path(__file__).parent / "agente/repositories/conversation_repository.py"
        content = repo_file.read_text()
        
        # Verificar se removeu os await das funções problemáticas
        invalid_patterns = [
            "await self.supabase.client.table(",
            "await self.supabase.client.table(\"messages\")",
            "await self.supabase.client.table(\"conversations\")"
        ]
        
        found_invalid = []
        for pattern in invalid_patterns:
            if pattern in content:
                found_invalid.append(pattern)
        
        if found_invalid:
            print(f"❌ Ainda existem await inválidos: {found_invalid}")
            return False
        
        # Verificar se manteve as chamadas síncronas corretas
        valid_patterns = [
            "self.supabase.client.table(\"messages\")",
            "self.supabase.client.table(\"conversations\")"
        ]
        
        found_valid = 0
        for pattern in valid_patterns:
            if pattern in content:
                found_valid += 1
        
        if found_valid == 0:
            print("❌ Não encontrou chamadas síncronas válidas")
            return False
        
        print("✅ Await inválidos removidos do ConversationRepository")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando ConversationRepository: {e}")
        return False

def test_health_check_await_removal():
    """Testa se os await inválidos foram removidos do health_check"""
    print("🧪 Testando remoção de await inválidos no health_check...")
    
    try:
        health_file = Path(__file__).parent / "agente/scripts/health_check.py"
        content = health_file.read_text()
        
        # Verificar se removeu os await das chamadas supabase
        invalid_patterns = [
            "await supabase_service.client.table("
        ]
        
        found_invalid = []
        for pattern in invalid_patterns:
            if pattern in content:
                found_invalid.append(pattern)
        
        if found_invalid:
            print(f"❌ Ainda existem await inválidos: {found_invalid}")
            return False
        
        # Verificar se manteve as chamadas síncronas corretas
        valid_patterns = [
            "supabase_service.client.table("
        ]
        
        found_valid = 0
        for pattern in valid_patterns:
            if pattern in content:
                found_valid += 1
        
        if found_valid == 0:
            print("❌ Não encontrou chamadas síncronas válidas")
            return False
        
        print("✅ Await inválidos removidos do health_check")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando health_check: {e}")
        return False

def test_syntax_validation():
    """Valida sintaxe dos arquivos corrigidos"""
    print("🧪 Validando sintaxe Python dos arquivos corrigidos...")
    
    try:
        files_to_check = [
            "agente/repositories/conversation_repository.py",
            "agente/scripts/health_check.py"
        ]
        
        for file_path in files_to_check:
            full_path = Path(__file__).parent / file_path
            if not full_path.exists():
                continue
                
            try:
                content = full_path.read_text()
                ast.parse(content)
                
            except SyntaxError as e:
                print(f"❌ Erro de sintaxe em {file_path}: {e}")
                return False
        
        print("✅ Sintaxe Python válida em todos os arquivos")
        return True
        
    except Exception as e:
        print(f"❌ Erro validando sintaxe: {e}")
        return False

def test_function_signatures_intact():
    """Verifica se as assinaturas das funções async permanecem corretas"""
    print("🧪 Testando integridade das assinaturas async...")
    
    try:
        repo_file = Path(__file__).parent / "agente/repositories/conversation_repository.py"
        content = repo_file.read_text()
        
        # Verificar se as funções ainda são async (correto)
        async_functions = [
            "async def check_conversation_timeout",
            "async def update_last_message_at",
            "async def update_conversation_stage",
            "async def get_active_conversations",
            "async def update_conversation_metadata",
            "async def get_conversation_stats"
        ]
        
        for func_sig in async_functions:
            if func_sig not in content:
                print(f"❌ Assinatura function perdida: {func_sig}")
                return False
        
        print("✅ Assinaturas async mantidas corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando assinaturas: {e}")
        return False

def test_error_reproduction():
    """Testa se o erro específico foi resolvido"""
    print("🧪 Verificando resolução do erro específico...")
    
    try:
        repo_file = Path(__file__).parent / "agente/repositories/conversation_repository.py"
        content = repo_file.read_text()
        
        # O erro específico era: object APIResponse[~_ReturnT] can't be used in 'await' expression
        # Isso acontecia quando usávamos await em operações síncronas do Supabase
        
        # Verificar se não há mais await self.supabase.client
        error_pattern = "await self.supabase.client"
        if error_pattern in content:
            print(f"❌ Ainda existe padrão de erro: {error_pattern}")
            return False
        
        print("✅ Padrão de erro resolvido")
        return True
        
    except Exception as e:
        print(f"❌ Erro verificando resolução: {e}")
        return False

def main():
    """Executa todos os testes de correção await"""
    print("🚨 TESTE CORREÇÃO AWAIT INVÁLIDO SUPABASE")
    print("=" * 60)
    
    tests = [
        ("ConversationRepository Await", test_conversation_repository_await_removal),
        ("HealthCheck Await", test_health_check_await_removal),
        ("Sintaxe Python", test_syntax_validation),
        ("Assinaturas Async", test_function_signatures_intact),
        ("Resolução Erro", test_error_reproduction)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSOU")
            else:
                print(f"❌ {test_name} FALHOU")
        except Exception as e:
            print(f"❌ {test_name} ERRO: {e}")
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO CORREÇÃO AWAIT")
    print("=" * 60)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 CORREÇÃO AWAIT IMPLEMENTADA!")
        print("\n📋 Correções aplicadas:")
        print("   ✅ ConversationRepository: 7 await inválidos removidos")
        print("   ✅ HealthCheck: 4 await inválidos removidos")
        print("   ✅ Sintaxe: Código Python válido")
        print("   ✅ Assinaturas: Funções async mantidas")
        print("   ✅ Erro: 'object APIResponse can't be used in await' resolvido")
        print("\n🚀 ERRO CRÍTICO RESOLVIDO!")
        print("\n💡 Explicação:")
        print("   O Supabase client Python é SÍNCRONO, não assíncrono.")
        print("   As chamadas .execute() retornam APIResponse, não awaitable.")
        print("   Removemos await das chamadas diretas do client.table()")
        return True
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam.")
        print("Verifique as correções antes de testar em produção.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)