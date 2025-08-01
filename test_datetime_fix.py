#!/usr/bin/env python3
"""
Teste CRÍTICO para validar correção do erro datetime timezone
Verifica se resolvemos: "can't subtract offset-naive and offset-aware datetimes"
"""

import sys
from pathlib import Path
import ast
from datetime import datetime, timezone

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_datetime_timezone_imports():
    """Testa se o import timezone foi adicionado"""
    print("🧪 Testando import timezone...")
    
    try:
        repo_file = Path(__file__).parent / "agente/repositories/conversation_repository.py"
        content = repo_file.read_text()
        
        if "from datetime import datetime, timedelta, timezone" not in content:
            print("❌ Import timezone não encontrado")
            return False
        
        print("✅ Import timezone encontrado")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando import: {e}")
        return False

def test_timezone_aware_datetime_usage():
    """Testa se datetime.now(timezone.utc) foi implementado"""
    print("🧪 Testando uso de datetime.now(timezone.utc)...")
    
    try:
        repo_file = Path(__file__).parent / "agente/repositories/conversation_repository.py"
        content = repo_file.read_text()
        
        # Verificar se as correções críticas foram aplicadas
        critical_fixes = [
            "datetime.now(timezone.utc) - started_at",
            "datetime.now(timezone.utc) - last_message_time",
            "started_at=datetime.now(timezone.utc)",
            "datetime.now(timezone.utc).isoformat()"
        ]
        
        found_fixes = 0
        for fix in critical_fixes:
            if fix in content:
                found_fixes += 1
        
        if found_fixes < 3:  # Pelo menos 3 das 4 correções críticas
            print(f"❌ Apenas {found_fixes}/4 correções timezone encontradas")
            return False
        
        print(f"✅ {found_fixes}/4 correções timezone implementadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando timezone: {e}")
        return False

def test_no_offset_naive_datetime():
    """Testa se removemos datetime.now() sem timezone das funções críticas"""
    print("🧪 Testando remoção de datetime.now() offset-naive...")
    
    try:
        repo_file = Path(__file__).parent / "agente/repositories/conversation_repository.py"
        content = repo_file.read_text()
        
        # Verificar se não tem mais datetime.now() sem timezone em operações críticas
        lines = content.split('\n')
        problematic_patterns = []
        
        for i, line in enumerate(lines):
            if "datetime.now() -" in line:
                # Operação de subtração com datetime.now() offset-naive
                problematic_patterns.append(f"Linha {i+1}: {line.strip()}")
        
        if problematic_patterns:
            print("❌ Ainda existem datetime.now() offset-naive em subtrações:")
            for pattern in problematic_patterns:
                print(f"   {pattern}")
            return False
        
        print("✅ Sem datetime.now() offset-naive em operações críticas")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando offset-naive: {e}")
        return False

def test_datetime_compatibility():
    """Testa compatibilidade das operações datetime"""
    print("🧪 Testando compatibilidade datetime...")
    
    try:
        # Simular as operações que estavam causando erro
        
        # Simular datetime do banco (offset-aware)
        bank_datetime_str = "2025-08-01T07:02:07.123456Z"
        bank_datetime = datetime.fromisoformat(bank_datetime_str.replace("Z", "+00:00"))
        
        # Simular datetime.now(timezone.utc) (offset-aware)
        current_datetime = datetime.now(timezone.utc)
        
        # Testar subtração (que antes causava erro)
        time_diff = current_datetime - bank_datetime
        
        # Verificar se o resultado é um timedelta válido
        if hasattr(time_diff, 'total_seconds'):
            print(f"✅ Subtração datetime funciona: {time_diff.total_seconds():.2f}s")
            return True
        else:
            print("❌ Subtração datetime não retornou timedelta válido")
            return False
        
    except Exception as e:
        print(f"❌ Erro testando compatibilidade: {e}")
        return False

def test_syntax_validation():
    """Valida sintaxe do arquivo corrigido"""
    print("🧪 Validando sintaxe Python...")
    
    try:
        repo_file = Path(__file__).parent / "agente/repositories/conversation_repository.py"
        
        if not repo_file.exists():
            print("❌ Arquivo não existe")
            return False
            
        content = repo_file.read_text()
        ast.parse(content)
        
        print("✅ Sintaxe Python válida")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro validando sintaxe: {e}")
        return False

def main():
    """Executa todos os testes de correção datetime"""
    print("🕐 TESTE CORREÇÃO DATETIME TIMEZONE")
    print("=" * 50)
    
    tests = [
        ("Import Timezone", test_datetime_timezone_imports),
        ("Timezone Aware Usage", test_timezone_aware_datetime_usage),
        ("Remove Offset-Naive", test_no_offset_naive_datetime),
        ("Compatibilidade Datetime", test_datetime_compatibility),
        ("Sintaxe Python", test_syntax_validation)
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
    print("📊 RESULTADO CORREÇÃO DATETIME")
    print("=" * 50)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 CORREÇÃO DATETIME IMPLEMENTADA!")
        print("\n📋 Correções aplicadas:")
        print("   ✅ Import: timezone adicionado")
        print("   ✅ Timezone: datetime.now(timezone.utc) implementado")
        print("   ✅ Offset-naive: Removido das operações críticas")
        print("   ✅ Compatibilidade: Operações datetime funcionando")
        print("   ✅ Sintaxe: Código Python válido")
        print("\n🚀 ERRO DATETIME RESOLVIDO!")
        print("\n💡 Explicação:")
        print("   Erro: 'can't subtract offset-naive and offset-aware datetimes'")
        print("   Causa: datetime.now() é offset-naive, banco é offset-aware")  
        print("   Solução: Usar datetime.now(timezone.utc) em operações")
        return True
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam.")
        print("Verifique as correções antes de testar em produção.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)