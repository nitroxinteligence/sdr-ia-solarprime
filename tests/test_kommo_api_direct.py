#!/usr/bin/env python3
"""
Teste direto da API do Kommo para verificar stages e movimentação
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Token do Kommo
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImJjMTYyOWZiNjA3YWZlZGI3MmI4OTRiNDFmY2EyMjRlN2E5OGViYmMzYTFkNjU3N2M5YzgxNTBkMDlkZmQ5NjViMDdhZTIyNWZkZDIzODFjIn0.eyJhdWQiOiJlNGQ5MTJhOS1jZGFlLTRlZjItOWZlOS03ZTg1M2YwMzBiMDAiLCJqdGkiOiJiYzE2MjlmYjYwN2FmZWRiNzJiODk0YjQxZmNhMjI0ZTdhOThlYmJjM2ExZDY1NzdjOWM4MTUwZDA5ZGZkOTY1YjA3YWUyMjVmZGQyMzgxYyIsImlhdCI6MTc1NDMyNTY5MywibmJmIjoxNzU0MzI1NjkzLCJleHAiOjE3NzgxMTIwMDAsInN1YiI6IjEzNTc3MjcyIiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjM0OTMyNzc2LCJiYXNlX2RvbWFpbiI6ImtvbW1vLmNvbSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwidXNlcl9mbGFncyI6MCwiaGFzaF91dWlkIjoiYzE4ODAyOWMtNjNjZC00MDBlLWIyOTctY2Y1NDZjOTdkMTE5IiwiYXBpX2RvbWFpbiI6ImFwaS1jLmtvbW1vLmNvbSJ9.NZOArG_oEDKplqMlCYowfg1x2V-bxYOztHoPr7LVmHuP3tWNk7nsjsx6qP6HaLj92nE2C4I6T5cifq9HDI5rBPOTngbr6GzkIhhrRMRBH366OlqOO4ln1jRpOmGF4HRRFERDIr6MExNmx9PVIAFVbu-33NmB15g5Yj7KqZHQUltiCFhnUIzcMfORV2CDQVZqiiT82E_JFFKubQLgQjRn-T4SnMIWxahXHptWincaID7rGHNTHYiQ1-84RuiOLUOGpXT_jC593bWQCZ6funncrFRp0_NIBoQuUtwz1EXn4F4PVVmx8hfhRJURuFQpwQxfeP7M6W0jKRDRByYqL8JMuQ"
BASE_URL = "https://leonardofvieira00.kommo.com"
PIPELINE_ID = 11672895

async def test_kommo_api():
    """Testa API do Kommo diretamente"""
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("🔍 TESTE DIRETO DA API DO KOMMO")
        print("=" * 60)
        
        # 1. Buscar informações do pipeline
        print("\n📊 1. BUSCANDO INFORMAÇÕES DO PIPELINE...")
        print("-" * 40)
        
        try:
            async with session.get(
                f"{BASE_URL}/api/v4/leads/pipelines/{PIPELINE_ID}",
                headers=headers
            ) as response:
                if response.status == 200:
                    pipeline = await response.json()
                    print(f"✅ Pipeline encontrado: {pipeline.get('name')}")
                    
                    # Listar todos os stages
                    print("\n📈 STAGES DISPONÍVEIS:")
                    stages = pipeline.get("_embedded", {}).get("statuses", [])
                    
                    stage_map = {}
                    for status in stages:
                        stage_id = status.get("id")
                        stage_name = status.get("name")
                        stage_map[stage_name] = stage_id
                        print(f"  • {stage_name}: ID={stage_id}")
                    
                    # Salvar mapeamento
                    with open("../kommo_stages_real.json", "w") as f:
                        json.dump(stage_map, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n💾 Mapeamento salvo em kommo_stages_real.json")
                    
                else:
                    error = await response.text()
                    print(f"❌ Erro ao buscar pipeline: {response.status}")
                    print(f"   {error}")
                    return
                    
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return
        
        # 2. Criar lead de teste
        print("\n📝 2. CRIANDO LEAD DE TESTE...")
        print("-" * 40)
        
        test_name = f"TESTE API DIRETO {datetime.now().strftime('%H:%M:%S')}"
        
        lead_data = {
            "name": test_name,
            "pipeline_id": PIPELINE_ID,
            "price": 1000
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v4/leads",
                headers=headers,
                json=[lead_data]
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    lead_id = result["_embedded"]["leads"][0]["id"]
                    print(f"✅ Lead criado: ID={lead_id}, Nome={test_name}")
                    
                    # 3. Buscar ID correto do stage NAO INTERESSADO
                    nao_interessado_id = None
                    for name, sid in stage_map.items():
                        if "interessado" in name.lower() and "não" in name.lower():
                            nao_interessado_id = sid
                            break
                    
                    if not nao_interessado_id:
                        # Procurar alternativas
                        for name, sid in stage_map.items():
                            if "interessado" in name.lower():
                                nao_interessado_id = sid
                                break
                    
                    if nao_interessado_id:
                        print(f"\n🎯 3. MOVENDO PARA NÃO INTERESSADO (ID={nao_interessado_id})...")
                        print("-" * 40)
                        
                        # Mover para NÃO INTERESSADO
                        update_data = {
                            "status_id": nao_interessado_id
                        }
                        
                        async with session.patch(
                            f"{BASE_URL}/api/v4/leads/{lead_id}",
                            headers=headers,
                            json=update_data
                        ) as response:
                            if response.status in [200, 202]:
                                print(f"✅ Lead movido para NÃO INTERESSADO!")
                                
                                # 4. Verificar posição atual
                                print("\n🔍 4. VERIFICANDO POSIÇÃO ATUAL...")
                                async with session.get(
                                    f"{BASE_URL}/api/v4/leads/{lead_id}",
                                    headers=headers
                                ) as response:
                                    if response.status == 200:
                                        lead = await response.json()
                                        current_status = lead.get("status_id")
                                        
                                        # Encontrar nome do stage atual
                                        current_stage_name = "DESCONHECIDO"
                                        for name, sid in stage_map.items():
                                            if sid == current_status:
                                                current_stage_name = name
                                                break
                                        
                                        print(f"📍 Status atual: {current_stage_name} (ID={current_status})")
                                        
                                        if current_status == nao_interessado_id:
                                            print("🎉 SUCESSO! Lead está em NÃO INTERESSADO!")
                                        else:
                                            print("❌ ERRO! Lead NÃO está em NÃO INTERESSADO!")
                            else:
                                error = await response.text()
                                print(f"❌ Erro ao mover lead: {response.status}")
                                print(f"   {error}")
                    else:
                        print("❌ Stage NÃO INTERESSADO não encontrado no pipeline!")
                        
                else:
                    error = await response.text()
                    print(f"❌ Erro ao criar lead: {response.status}")
                    print(f"   {error}")
                    
        except Exception as e:
            print(f"❌ Erro na operação: {e}")

async def main():
    await test_kommo_api()

if __name__ == "__main__":
    asyncio.run(main())