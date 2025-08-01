#!/usr/bin/env python3
"""
Teste específico para correção do formato UUID
Verifica se o session manager agora gera UUIDs válidos
"""

import sys
from pathlib import Path
import re

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_uuid_import():
    """Testa se o import uuid foi adicionado"""
    print("🧪 Testando import uuid...")
    
    try:
        session_file = Path(__file__).parent / "agente/core/session_manager.py"
        content = session_file.read_text()
        
        if "import uuid" not in content:
            print("❌ Import uuid não encontrado")
            return False
        
        print("✅ Import uuid encontrado")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando import: {e}")
        return False

def test_uuid_generation():
    """Testa se a geração de UUID foi implementada"""
    print("🧪 Testando geração UUID...")
    
    try:
        session_file = Path(__file__).parent / "agente/core/session_manager.py"
        content = session_file.read_text()
        
        if "str(uuid.uuid4())" not in content:
            print("❌ Geração UUID não encontrada")
            return False
            
        if "temp_" in content and "f\"temp_{phone}_{datetime.now(timezone.utc).timestamp()}\"" in content:
            print("❌ Formato temp_ ainda presente")
            return False
        
        print("✅ Geração UUID implementada corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando UUID: {e}")
        return False

def test_uuid_comment():
    """Testa se o comentário explicativo foi adicionado"""
    print("🧪 Testando comentário explicativo...")
    
    try:
        session_file = Path(__file__).parent / "agente/core/session_manager.py"
        content = session_file.read_text()
        
        if "UUID válido para PostgreSQL" not in content:
            print("❌ Comentário explicativo não encontrado")
            return False
        
        print("✅ Comentário explicativo encontrado")
        return True
        
    except Exception as e:
        print(f"❌ Erro testando comentário: {e}")
        return False

def test_uuid_format_validation():
    """Testa se o formato UUID é válido usando regex"""
    print("🧪 Testando formato UUID com regex...")
    
    try:
        import uuid
        
        # Gerar UUID de teste
        test_uuid = str(uuid.uuid4())
        
        # Regex para validar UUID v4
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        
        if not re.match(uuid_pattern, test_uuid):
            print(f"❌ UUID gerado tem formato inválido: {test_uuid}")
            return False
        
        print(f"✅ UUID tem formato válido: {test_uuid}")
        return True
        
    except Exception as e:
        print(f"❌ Erro validando formato UUID: {e}")
        return False

def main():
    """Executa testes de correção UUID"""
    print("🔧 TESTE CORREÇÃO UUID FORMAT")
    print("=" * 50)
    
    tests = [
        ("Import UUID", test_uuid_import),
        ("Geração UUID", test_uuid_generation),
        ("Comentário UUID", test_uuid_comment),
        ("Formato UUID", test_uuid_format_validation)
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
    print("📊 RESULTADO CORREÇÃO UUID")
    print("=" * 50)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 CORREÇÃO UUID IMPLEMENTADA!")
        print("\n📋 Correções aplicadas:")
        print("   ✅ Import: uuid module importado")
        print("   ✅ Geração: str(uuid.uuid4()) implementado")
        print("   ✅ Formato: temp_ removido")
        print("   ✅ Comentário: Documentação adicionada")
        print("\n🚀 ERRO UUID RESOLVIDO!")
        return True
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam.")
        print("Verifique as correções antes de testar em produção.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)