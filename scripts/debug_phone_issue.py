#!/usr/bin/env python3
"""
Debug do problema com phone_number
==================================
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from models.lead import LeadCreate
from repositories.lead_repository import lead_repository


async def debug_phone():
    """Debug do problema com phone_number"""
    
    print("🔍 Debug - Problema com phone_number\n")
    
    # Testar diferentes tamanhos de phone_number
    test_cases = [
        "11999999999",      # 11 caracteres
        "5511999999999",    # 13 caracteres  
        "551199999999",     # 12 caracteres
        "+5511999999999",   # 14 caracteres
        "11 99999-9999",    # 14 caracteres com formatação
        "5511888888888",    # 13 caracteres (caso do erro)
    ]
    
    for phone in test_cases:
        print(f"\nTestando: '{phone}' (tamanho: {len(phone)})")
        
        try:
            # Criar lead data
            lead_data = LeadCreate(phone_number=phone)
            print(f"  LeadCreate.phone_number: '{lead_data.phone_number}'")
            print(f"  Tamanho do valor: {len(lead_data.phone_number)}")
            
            # Tentar criar
            lead = await lead_repository.create_or_update(lead_data)
            
            if lead:
                print(f"  ✅ Sucesso! Lead ID: {lead.id}")
                
                # Deletar para poder testar novamente
                await lead_repository.delete(lead.id)
                print(f"  🗑️  Lead deletado para próximo teste")
            else:
                print(f"  ❌ Falha ao criar lead")
                
        except Exception as e:
            error_msg = str(e)
            if "22001" in error_msg:
                print(f"  ❌ ERRO: Campo muito longo!")
                print(f"  Detalhes: {error_msg}")
            else:
                print(f"  ❌ Outro erro: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Resumo:")
    print("- O campo phone_number no banco está configurado para VARCHAR(20)")
    print("- Números com mais de 20 caracteres causam erro")
    print("- Execute o SQL 'fix_phone_field_with_views.sql' para corrigir")
    print("=" * 60)


async def main():
    """Função principal"""
    await debug_phone()


if __name__ == "__main__":
    asyncio.run(main())