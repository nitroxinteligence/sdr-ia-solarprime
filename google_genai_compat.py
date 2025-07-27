"""
Google GenAI Compatibility Layer
================================
Este arquivo cria um redirecionamento para resolver o problema de importação
do módulo google.genai que o AGnO Framework está tentando usar.
"""

import sys
from types import ModuleType

# Criar módulo fake google.genai que redireciona para google.generativeai
google_module = ModuleType('google')
genai_module = ModuleType('google.genai')

# Importar o módulo real
try:
    import google.generativeai as real_genai
    
    # Criar redirecionamentos para os tipos esperados
    class FakeTypes:
        # Adicionar os tipos que o AGnO espera encontrar
        pass
    
    genai_module.types = FakeTypes()
    
    # Copiar atributos do módulo real
    for attr in dir(real_genai):
        if not attr.startswith('_'):
            setattr(genai_module, attr, getattr(real_genai, attr))
    
except ImportError:
    pass

# Registrar os módulos no sistema
sys.modules['google'] = google_module
sys.modules['google.genai'] = genai_module
google_module.genai = genai_module

print("Google GenAI compatibility layer loaded successfully")