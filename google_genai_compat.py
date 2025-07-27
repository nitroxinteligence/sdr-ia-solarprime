"""
Google GenAI Compatibility Layer
================================
Este arquivo cria um redirecionamento para resolver o problema de importação
do módulo google.genai que o AGnO Framework está tentando usar.
"""

import sys
import importlib.util
from types import ModuleType
import logging

logger = logging.getLogger(__name__)

# Tentar várias formas de importar o pacote Google AI
real_genai = None
import_success = False

# Tentativa 1: google-generativeai (pacote oficial)
try:
    import google.generativeai as real_genai
    import_success = True
    logger.info("Successfully imported google.generativeai")
except ImportError:
    logger.warning("google.generativeai not found")

# Tentativa 2: google-genai (pacote alternativo)
if not import_success:
    try:
        import google_genai as real_genai
        import_success = True
        logger.info("Successfully imported google_genai")
    except ImportError:
        logger.warning("google_genai not found")

# Tentativa 3: Verificar se google_genai está instalado mas não importável diretamente
if not import_success:
    spec = importlib.util.find_spec("google_genai")
    if spec is not None:
        try:
            real_genai = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(real_genai)
            import_success = True
            logger.info("Successfully loaded google_genai via importlib")
        except Exception as e:
            logger.error(f"Failed to load google_genai via importlib: {e}")

if not import_success:
    logger.error("No Google AI package found. Please install google-generativeai or google-genai")
    raise ImportError(
        "Neither google-generativeai nor google-genai is installed. "
        "Please install using: pip install google-generativeai"
    )

# Criar estrutura de módulos compatível
if 'google' not in sys.modules:
    google_module = ModuleType('google')
    sys.modules['google'] = google_module
else:
    google_module = sys.modules['google']

# Criar google.genai
genai_module = ModuleType('google.genai')

# Criar google.genai.types se necessário
class GenAITypes:
    """Compatibility types for AGnO Framework"""
    pass

genai_module.types = GenAITypes()

# Copiar todos os atributos do módulo real
if real_genai:
    for attr in dir(real_genai):
        if not attr.startswith('_'):
            setattr(genai_module, attr, getattr(real_genai, attr))
    
    # Se o módulo real tem types, copiar também
    if hasattr(real_genai, 'types'):
        genai_module.types = real_genai.types

# Registrar os módulos no sistema
sys.modules['google.genai'] = genai_module
google_module.genai = genai_module

# Também registrar como google.generativeai para compatibilidade
sys.modules['google.generativeai'] = genai_module
google_module.generativeai = genai_module

logger.info("Google GenAI compatibility layer loaded successfully")
print("Google GenAI compatibility layer loaded successfully")