"""
Google GenAI Compatibility Layer
================================
Este arquivo intercepta imports do AGnO Framework e cria a estrutura esperada.
"""

import sys
import importlib
import importlib.util
from types import ModuleType

# IMPORTANTE: Este módulo deve ser carregado ANTES do AGnO Framework
# Por isso, deve ser importado no início de api/main.py

# Importar google.generativeai primeiro
try:
    import google.generativeai as real_genai
except ImportError:
    raise ImportError(
        "google-generativeai não está instalado. "
        "Por favor, instale com: pip install google-generativeai==0.7.2"
    )

# Criar estrutura de módulos que o AGnO espera
class MockTypes:
    """Mock dos tipos que o AGnO Framework espera encontrar"""
    
    # Mapear tipos do google.generativeai para o que o AGnO espera
    def __init__(self):
        # Se google.generativeai tem types, usar; senão criar classes vazias
        if hasattr(real_genai, 'types'):
            self.Content = getattr(real_genai.types, 'Content', type('Content', (), {}))
            self.Part = getattr(real_genai.types, 'Part', type('Part', (), {}))
            self.FunctionCall = getattr(real_genai.types, 'FunctionCall', type('FunctionCall', (), {}))
            self.FunctionResponse = getattr(real_genai.types, 'FunctionResponse', type('FunctionResponse', (), {}))
            self.FunctionDeclaration = getattr(real_genai.types, 'FunctionDeclaration', type('FunctionDeclaration', (), {}))
            self.Tool = getattr(real_genai.types, 'Tool', type('Tool', (), {}))
        else:
            # Criar classes vazias se não existirem
            self.Content = type('Content', (), {})
            self.Part = type('Part', (), {})
            self.FunctionCall = type('FunctionCall', (), {})
            self.FunctionResponse = type('FunctionResponse', (), {})
            self.FunctionDeclaration = type('FunctionDeclaration', (), {})
            self.Tool = type('Tool', (), {})

# Criar módulo mock completo
class MockGenAI:
    """Mock do módulo google.genai para compatibilidade com AGnO"""
    
    def __init__(self):
        self.types = MockTypes()
        # Copiar outros atributos do módulo real
        for attr in dir(real_genai):
            if not attr.startswith('_') and attr != 'types':
                setattr(self, attr, getattr(real_genai, attr))
    
    def __getattr__(self, name):
        # Fallback para atributos não encontrados
        return getattr(real_genai, name)

# Instalar o mock ANTES que o AGnO tente importar
mock_genai = MockGenAI()

# Garantir que o módulo 'google' existe
if 'google' not in sys.modules:
    sys.modules['google'] = ModuleType('google')

# Registrar todos os módulos necessários
sys.modules['google.genai'] = mock_genai
sys.modules['google.genai.types'] = mock_genai.types

# Adicionar ao módulo google
google_module = sys.modules['google']
google_module.genai = mock_genai

# Hook de importação para interceptar imports futuros
class GenAIImportHook:
    def find_spec(self, fullname, path, target=None):
        if fullname == 'google.genai' or fullname.startswith('google.genai.'):
            return importlib.util.spec_from_loader(fullname, self)
        return None
    
    def create_module(self, spec):
        if spec.name == 'google.genai':
            return mock_genai
        elif spec.name == 'google.genai.types':
            return mock_genai.types
        return None
    
    def exec_module(self, module):
        pass

# Instalar o hook no início da lista para ter prioridade
sys.meta_path.insert(0, GenAIImportHook())

print("Google GenAI compatibility layer loaded successfully")