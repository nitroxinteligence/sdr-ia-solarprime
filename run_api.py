#!/usr/bin/env python3
"""
Run API Server
==============
Script para rodar o servidor FastAPI
"""

import os
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Roda o servidor API"""
    
    # Configurações
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    workers = 1 if reload else int(os.getenv("API_WORKERS", "4"))
    
    print("🚀 SDR IA SolarPrime - API Server")
    print(f"📍 Rodando em: http://{host}:{port}")
    print(f"🔧 Ambiente: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"♻️  Auto-reload: {'Sim' if reload else 'Não'}")
    print(f"👷 Workers: {workers}")
    print("\nPressione CTRL+C para parar\n")
    
    # Configuração do uvicorn
    config = {
        "app": "api.main:app",
        "host": host,
        "port": port,
        "reload": reload,
        "access_log": True,
        "log_level": os.getenv("LOG_LEVEL", "info").lower()
    }
    
    # Adicionar workers apenas se não estiver em modo reload
    if not reload:
        config["workers"] = workers
    
    # Rodar servidor
    uvicorn.run(**config)


if __name__ == "__main__":
    main()