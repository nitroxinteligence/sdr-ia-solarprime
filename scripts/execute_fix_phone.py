#!/usr/bin/env python3
"""
Executa correção do campo phone_number
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()


def fix_phone_field():
    """Corrige o tamanho do campo phone_number"""
    
    # Conectar ao Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Credenciais do Supabase não encontradas!")
        return False
    
    try:
        client = create_client(url, key)
        
        # Executar alteração
        print("🔧 Alterando tamanho do campo phone_number...")
        
        # Nota: Supabase Python client não suporta DDL diretamente
        # Você precisa executar isso no SQL Editor do Supabase
        
        print("\n📋 Por favor, execute o seguinte SQL no Supabase Dashboard:")
        print("=" * 60)
        print("""
ALTER TABLE leads 
ALTER COLUMN phone_number TYPE VARCHAR(20);
        """)
        print("=" * 60)
        print("\n1. Acesse: https://app.supabase.com")
        print("2. Vá para: SQL Editor")
        print("3. Cole o SQL acima")
        print("4. Clique em 'Run'")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


if __name__ == "__main__":
    fix_phone_field()