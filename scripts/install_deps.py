#!/usr/bin/env python3
"""
Script para instalar/atualizar dependências
============================================
"""

import subprocess
import sys

def install_dependencies():
    """Instala as dependências do projeto"""
    print("🔧 Instalando/Atualizando dependências...")
    
    # Primeiro, atualizar pip
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Instalar dependências do requirements.txt
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("\n✅ Dependências instaladas com sucesso!")
    print("\n📌 Versões importantes:")
    
    # Verificar versão do AGnO
    try:
        import agno
        print(f"AGnO: {agno.__version__ if hasattr(agno, '__version__') else 'Versão não disponível'}")
        
        # Testar imports multimodais
        try:
            from agno.media import Image, Audio, Video
            print("✅ Módulos multimodais AGnO disponíveis!")
        except ImportError as e:
            print(f"❌ Erro ao importar módulos multimodais: {e}")
            
    except ImportError:
        print("❌ AGnO não está instalado!")
    
    # Verificar Gemini
    try:
        import google.generativeai as genai
        print(f"Google Generative AI: instalado")
    except ImportError:
        print("❌ Google Generative AI não está instalado!")

if __name__ == "__main__":
    install_dependencies()