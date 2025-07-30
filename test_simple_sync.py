#!/usr/bin/env python
"""
Test Script Simplificado - Testa apenas salvamento do link no Kommo
===================================================================
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger

# Carregar variáveis de ambiente
load_dotenv()

# Imports necessários
from services.kommo_service import kommo_service


async def test_update_custom_field():
    """Testa apenas a atualização de campo customizado"""
    
    print("\n=== TESTE DE ATUALIZAÇÃO DE CAMPO CUSTOMIZADO NO KOMMO ===\n")
    
    # 1. Criar lead simples no Kommo
    print("📊 Criando lead de teste no Kommo...")
    
    lead_payload = [{
        "name": "Teste Campo Calendar",
        "price": 1000,
        "pipeline_id": int(os.getenv("KOMMO_PIPELINE_ID", 11672895))
    }]
    
    try:
        result = await kommo_service._make_request("POST", "/leads", lead_payload)
        
        if result and "_embedded" in result:
            lead_id = result["_embedded"]["leads"][0]["id"]
            print(f"✅ Lead criado: ID {lead_id}")
            
            # 2. Tentar atualizar campo google_calendar_link
            print("\n🔗 Tentando salvar link do Calendar...")
            
            test_link = "https://calendar.google.com/calendar/event?id=test123"
            
            success = await kommo_service.update_lead_custom_field(
                lead_id=lead_id,
                field_name='google_calendar_link',
                value=test_link
            )
            
            if success:
                print("✅ Link salvo com sucesso!")
            else:
                print("❌ Falha ao salvar link")
                print("   Verifique se o campo 'google_calendar_link' existe no Kommo")
                print("   e se o ID está configurado corretamente no .env")
            
            # 3. Buscar lead para verificar
            print("\n🔍 Verificando se o link foi salvo...")
            
            lead_data = await kommo_service.get_lead(lead_id)
            if lead_data:
                custom_fields = lead_data.get("custom_fields_values", [])
                
                print(f"\nCampos customizados encontrados:")
                for field in custom_fields:
                    field_id = field.get("field_id")
                    field_name = field.get("field_name", "Unknown")
                    values = field.get("values", [])
                    value = values[0].get("value") if values else "N/A"
                    
                    print(f"  - {field_name} (ID: {field_id}): {value}")
                    
                    # Verificar se é nosso campo
                    configured_id = os.getenv("KOMMO_FIELD_GOOGLE_CALENDAR_LINK", "0")
                    if str(field_id) == configured_id:
                        print(f"    ✅ Este é o campo google_calendar_link!")
            
            # 4. Limpar
            print("\n🧹 Removendo lead de teste...")
            await kommo_service._make_request("DELETE", f"/leads/{lead_id}")
            print("✅ Lead removido")
            
        else:
            print("❌ Erro ao criar lead no Kommo")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n✅ Teste concluído!")


async def list_custom_fields():
    """Lista todos os campos customizados disponíveis"""
    
    print("\n=== LISTANDO CAMPOS CUSTOMIZADOS DO KOMMO ===\n")
    
    try:
        # Buscar campos customizados
        response = await kommo_service._make_request("GET", "/leads/custom_fields")
        
        if response and "_embedded" in response:
            fields = response["_embedded"].get("custom_fields", [])
            
            print(f"Encontrados {len(fields)} campos customizados:\n")
            
            for field in fields:
                field_id = field.get("id")
                field_name = field.get("name")
                field_type = field.get("type")
                
                print(f"ID: {field_id}")
                print(f"Nome: {field_name}")
                print(f"Tipo: {field_type}")
                print("-" * 40)
                
                # Se for tipo select, mostrar opções
                if field_type == "select" and "enums" in field:
                    print("Opções:")
                    for enum in field["enums"]:
                        print(f"  - {enum.get('value')} (ID: {enum.get('id')})")
                    print("-" * 40)
            
            print("\n💡 DICA: Procure por campos relacionados a 'calendar' ou 'link'")
            print("   Se não encontrar, crie um novo campo do tipo 'link' ou 'url' no Kommo")
            
    except Exception as e:
        print(f"❌ Erro ao listar campos: {e}")


if __name__ == "__main__":
    print("🚀 Iniciando testes simplificados...")
    
    # Listar campos disponíveis primeiro
    asyncio.run(list_custom_fields())
    
    # Depois testar atualização
    asyncio.run(test_update_custom_field())
    
    print("\n🎉 Todos os testes concluídos!")