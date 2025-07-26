#!/usr/bin/env python3
"""
Script para atualizar todos os usos de 'async with evolution_client'
"""

import os
import re

files_to_update = [
    "scripts/quick-webhook-setup.py",
    "api/routes/webhook_admin.py",
    "services/whatsapp_service.py",
    "api/routes/instance.py",
    "scripts/test_whatsapp_integration.py",
    "scripts/setup_webhooks.py",
    "api/routes/health.py"
]

def update_file(filepath):
    """Atualiza um arquivo para não usar context manager"""
    
    full_path = f"/Users/adm/Downloads/SDR IA SolarPrime - Python/{filepath}"
    
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Padrões para substituir
        patterns = [
            # Padrão com 'as client'
            (r'async with evolution_client as client:\s*\n(\s+)(.*?)await client\.', 
             r'\1\2await evolution_client.'),
            # Padrão sem uso de client após
            (r'async with evolution_client as client:\s*\n', ''),
            # Padrão inline
            (r'async with evolution_client as client:', '# Direct use of evolution_client'),
        ]
        
        original = content
        
        # Aplicar substituições
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        # Remover linhas que ficaram com apenas 'client.'
        content = re.sub(r'\bclient\.', 'evolution_client.', content)
        
        if content != original:
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"✅ Atualizado: {filepath}")
        else:
            print(f"⏭️  Sem mudanças: {filepath}")
            
    except Exception as e:
        print(f"❌ Erro ao processar {filepath}: {e}")

if __name__ == "__main__":
    print("Atualizando arquivos para não usar context manager...")
    
    for file in files_to_update:
        update_file(file)
    
    print("\n✅ Concluído!")