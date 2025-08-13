#!/usr/bin/env python3
"""
Verificação rápida se a movimentação está funcionando
"""

import asyncio
from datetime import datetime
from app.services.crm_service_100_real import CRMServiceReal

async def test_movement():
    print("=" * 60)
    print("🎯 TESTE FINAL: VERIFICAÇÃO DE MOVIMENTAÇÃO")
    print("=" * 60)
    
    crm = CRMServiceReal()
    await crm.initialize()
    
    # Criar lead de teste
    test_name = f"TESTE FINAL NAO INTERESSADO {datetime.now().strftime('%H:%M:%S')}"
    lead_data = {
        "phone": f"5511999{datetime.now().strftime('%H%M%S')}",
        "name": test_name,
        "source": "teste_final"
    }
    
    result = await crm.create_or_update_lead(lead_data)
    if not result.get("success"):
        print(f"❌ Erro ao criar lead")
        return
    
    lead_id = str(result["lead_id"])
    print(f"✅ Lead criado: {test_name} (ID={lead_id})")
    
    # Mover para NÃO INTERESSADO
    print(f"\n🔄 Movendo para NÃO INTERESSADO...")
    stage_result = await crm.update_lead_stage(
        lead_id=lead_id,
        stage="nao_interessado",
        notes="Teste final de movimentação"
    )
    
    if stage_result.get("success"):
        print(f"✅ Comando executado com sucesso")
    else:
        print(f"❌ Erro: {stage_result}")
        return
    
    # Aguardar e verificar
    await asyncio.sleep(2)
    
    # Verificar posição
    info = await crm.get_lead_info(lead_id)
    if info.get("success"):
        status_id = info["lead"]["status"]
        
        if status_id == 89709599:
            print(f"\n🎉 SUCESSO TOTAL!")
            print(f"✅ Lead '{test_name}' está em NÃO INTERESSADO")
            print(f"✅ Sistema 100% FUNCIONAL para movimentação de cards!")
        else:
            print(f"\n❌ FALHA!")
            print(f"Lead está no status {status_id}, esperado 89709599")
    
    await crm.close()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_movement())