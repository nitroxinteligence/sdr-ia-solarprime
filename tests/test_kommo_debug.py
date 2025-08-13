#!/usr/bin/env python3
"""
Teste de debug para identificar problema na movimentação de cards
"""

import asyncio
import json
from datetime import datetime
from app.services.crm_service_100_real import CRMServiceReal
from app.utils.logger import emoji_logger

async def test_movement_debug():
    """Teste detalhado de movimentação"""
    
    print("=" * 60)
    print("🔍 DEBUG: TESTE DE MOVIMENTAÇÃO DE CARDS")
    print("=" * 60)
    
    # Inicializar serviço
    crm = CRMServiceReal()
    await crm.initialize()
    
    # 1. Criar lead de teste
    print("\n📝 1. CRIANDO LEAD DE TESTE...")
    test_name = f"DEBUG MOVIMENTO {datetime.now().strftime('%H:%M:%S')}"
    
    lead_data = {
        "phone": f"5511999{datetime.now().strftime('%H%M%S')}",
        "name": test_name,
        "email": f"debug{datetime.now().strftime('%H%M%S')}@test.com",
        "source": "debug_test"
    }
    
    result = await crm.create_or_update_lead(lead_data)
    
    if not result.get("success"):
        print(f"❌ Erro ao criar lead: {result}")
        return
    
    lead_id = str(result["lead_id"])
    print(f"✅ Lead criado: ID={lead_id}")
    
    # 2. Verificar estágio inicial
    print("\n🔍 2. VERIFICANDO ESTÁGIO INICIAL...")
    info = await crm.get_lead_info(lead_id)
    if info.get("success"):
        status_id = info["lead"]["status"]
        print(f"📍 Status inicial: {status_id}")
    
    # 3. Tentar mover para NÃO INTERESSADO
    print("\n🎯 3. MOVENDO PARA NÃO INTERESSADO...")
    print("-" * 40)
    
    # Método 1: Via update_lead_stage com string
    print("Método 1: update_lead_stage('nao_interessado')")
    stage_result = await crm.update_lead_stage(
        lead_id=lead_id,
        stage="nao_interessado",
        notes="Teste de movimentação - DEBUG"
    )
    
    print(f"Resultado: {stage_result}")
    
    # Aguardar um pouco
    await asyncio.sleep(2)
    
    # 4. Verificar estágio após movimentação
    print("\n🔍 4. VERIFICANDO ESTÁGIO APÓS MOVIMENTAÇÃO...")
    info = await crm.get_lead_info(lead_id)
    if info.get("success"):
        status_id = info["lead"]["status"]
        print(f"📍 Status após movimentação: {status_id}")
        
        if status_id == 89709599:
            print("✅ SUCESSO! Lead está em NÃO INTERESSADO (89709599)")
        else:
            print(f"❌ FALHA! Lead está no status {status_id}, esperado 89709599")
            
            # Tentar método alternativo
            print("\n🔄 5. TENTANDO MÉTODO ALTERNATIVO...")
            print("Movendo diretamente com status_id=89709599")
            
            # Fazer chamada direta à API
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {crm.access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    f"{crm.base_url}/api/v4/leads/{lead_id}",
                    headers=headers,
                    json={"status_id": 89709599}
                ) as response:
                    if response.status in [200, 202]:
                        print("✅ Movimentação direta executada")
                        
                        # Verificar novamente
                        await asyncio.sleep(1)
                        info = await crm.get_lead_info(lead_id)
                        if info.get("success"):
                            status_id = info["lead"]["status"]
                            print(f"📍 Status final: {status_id}")
                            
                            if status_id == 89709599:
                                print("✅ SUCESSO com método direto!")
                            else:
                                print(f"❌ Ainda falhou, status: {status_id}")
                    else:
                        error = await response.text()
                        print(f"❌ Erro na chamada direta: {response.status}")
                        print(f"   {error}")
    
    # Fechar conexões
    await crm.close()
    print("\n" + "=" * 60)
    print("📊 TESTE CONCLUÍDO")
    print("=" * 60)

async def main():
    await test_movement_debug()

if __name__ == "__main__":
    asyncio.run(main())