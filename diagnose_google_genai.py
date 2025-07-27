#!/usr/bin/env python3
"""
Diagnóstico de instalação do google-genai
"""

import subprocess
import sys
import importlib.util

print("🔍 Diagnóstico de instalação do google-genai\n")

# 1. Verificar se está no requirements.txt
print("1. Verificando requirements.txt...")
try:
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
        if 'google-genai' in requirements:
            print("✅ google-genai está no requirements.txt")
        else:
            print("❌ google-genai NÃO está no requirements.txt")
except Exception as e:
    print(f"❌ Erro ao ler requirements.txt: {e}")

# 2. Verificar instalação via pip
print("\n2. Verificando instalação via pip...")
result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
if 'google-genai' in result.stdout:
    print("✅ google-genai está instalado via pip")
else:
    print("❌ google-genai NÃO está instalado via pip")

# 3. Verificar instalação do google-generativeai
if 'google-generativeai' in result.stdout:
    print("✅ google-generativeai está instalado via pip")
else:
    print("❌ google-generativeai NÃO está instalado via pip")

# 4. Tentar importar os módulos
print("\n3. Tentando importar os módulos...")

# google-generativeai
try:
    import google.generativeai
    print("✅ google.generativeai importado com sucesso")
except ImportError as e:
    print(f"❌ Falha ao importar google.generativeai: {e}")

# google_genai
try:
    import google_genai
    print("✅ google_genai importado com sucesso")
except ImportError as e:
    print(f"❌ Falha ao importar google_genai: {e}")

# 5. Verificar com importlib
print("\n4. Verificando com importlib...")
specs = [
    'google.generativeai',
    'google_genai',
    'google.genai',
    'genai'
]

for spec_name in specs:
    spec = importlib.util.find_spec(spec_name)
    if spec:
        print(f"✅ {spec_name} encontrado via importlib")
    else:
        print(f"❌ {spec_name} NÃO encontrado via importlib")

# 6. Verificar o arquivo de compatibilidade
print("\n5. Verificando arquivo de compatibilidade...")
try:
    import google_genai_compat
    print("✅ google_genai_compat importado com sucesso")
    
    # Verificar se google.genai está disponível
    try:
        import google.genai
        print("✅ google.genai disponível após importar compatibilidade")
    except ImportError:
        print("❌ google.genai NÃO disponível mesmo após importar compatibilidade")
        
except ImportError as e:
    print(f"❌ Falha ao importar google_genai_compat: {e}")

print("\n🏁 Diagnóstico concluído!")