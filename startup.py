#!/usr/bin/env python3
"""
Startup script para garantir carregamento correto do módulo de compatibilidade
"""

# Carregar módulo de compatibilidade ANTES de qualquer import
import google_genai_compat

# Agora importar e executar a aplicação
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, workers=2, access_log=True)