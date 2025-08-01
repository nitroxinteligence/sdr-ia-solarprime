"""
Exemplo de uso do KommoService
Este arquivo demonstra como usar as principais funcionalidades do serviço
"""

import asyncio
from datetime import datetime, timedelta
from kommo_service import get_kommo_service

async def example_usage():
    """Demonstra o uso das principais funcionalidades do KommoService"""
    
    # Obter instância do serviço
    kommo = get_kommo_service()
    
    try:
        # 1. Listar pipelines e stages disponíveis
        print("=== PIPELINES E STAGES ===")
        pipelines = await kommo.get_pipelines()
        for pipeline in pipelines:
            print(f"\nPipeline: {pipeline.get('name')} (ID: {pipeline.get('id')})")
            statuses = pipeline.get('_embedded', {}).get('statuses', [])
            for status in statuses:
                print(f"  - {status.get('name')} (ID: {status.get('id')})")
        
        # 2. Listar campos customizados
        print("\n\n=== CAMPOS CUSTOMIZADOS ===")
        fields = await kommo.get_custom_fields()
        for field in fields[:5]:  # Mostrar apenas os 5 primeiros
            print(f"- {field.get('name')} (ID: {field.get('id')}, Code: {field.get('code')})")
        
        # 3. Criar um novo lead
        print("\n\n=== CRIAR LEAD ===")
        new_lead = await kommo.create_lead(
            name="João Silva - Teste API",
            phone="+5511999887766",
            custom_fields={
                # Adicionar campos customizados se necessário
                # field_id: "valor"
            }
        )
        lead_id = new_lead.get('id')
        print(f"Lead criado com sucesso! ID: {lead_id}")
        
        # 4. Adicionar nota ao lead
        print("\n=== ADICIONAR NOTA ===")
        note = await kommo.add_note(
            lead_id=lead_id,
            text="Lead criado via API de teste. Cliente interessado em energia solar."
        )
        print(f"Nota adicionada! ID: {note.get('id')}")
        
        # 5. Adicionar tag
        print("\n=== ADICIONAR TAG ===")
        await kommo.add_tag(lead_id, "teste-api")
        await kommo.add_tag(lead_id, "energia-solar")
        print("Tags adicionadas com sucesso!")
        
        # 6. Atualizar stage do lead
        print("\n=== MOVER LEAD NO PIPELINE ===")
        # Mover para "em qualificação"
        await kommo.update_lead_stage(lead_id, "em qualificação")
        print("Lead movido para 'Em Qualificação'")
        
        # Aguardar um pouco
        await asyncio.sleep(2)
        
        # Mover para "qualificado"
        await kommo.update_lead_stage(lead_id, "qualificado")
        print("Lead movido para 'Qualificado'")
        
        # 7. Criar tarefa
        print("\n=== CRIAR TAREFA ===")
        task_date = datetime.now() + timedelta(days=1)
        task = await kommo.create_task(
            lead_id=lead_id,
            text="Entrar em contato para agendar visita técnica",
            complete_till=task_date
        )
        print(f"Tarefa criada! ID: {task.get('id')}")
        
        # 8. Buscar lead por telefone
        print("\n=== BUSCAR LEAD POR TELEFONE ===")
        found_lead = await kommo.get_lead_by_phone("+5511999887766")
        if found_lead:
            print(f"Lead encontrado: {found_lead.get('name')} (ID: {found_lead.get('id')})")
        
        # 9. Buscar lead por ID
        print("\n=== BUSCAR LEAD POR ID ===")
        lead_details = await kommo.get_lead(lead_id)
        print(f"Lead: {lead_details.get('name')}")
        print(f"Status: {lead_details.get('status_id')}")
        print(f"Pipeline: {lead_details.get('pipeline_id')}")
        
        # 10. Atualizar dados do lead
        print("\n=== ATUALIZAR LEAD ===")
        updated_lead = await kommo.update_lead(
            lead_id=lead_id,
            name="João Silva - Atualizado via API",
            price=15000  # Valor estimado do negócio
        )
        print(f"Lead atualizado! Novo nome: {updated_lead.get('name')}")
        
    except Exception as e:
        print(f"\nErro durante exemplo: {type(e).__name__}: {str(e)}")
    
    finally:
        # Fechar conexão
        await kommo.close()


async def example_error_handling():
    """Demonstra o tratamento de erros"""
    kommo = get_kommo_service()
    
    try:
        # Tentar buscar lead inexistente
        await kommo.get_lead(999999999)
    except Exception as e:
        print(f"Erro esperado ao buscar lead inexistente: {e}")
    
    try:
        # Tentar mover lead para stage inexistente
        await kommo.update_lead_stage(123, "stage_que_nao_existe")
    except Exception as e:
        print(f"Erro esperado ao usar stage inválido: {e}")
    
    await kommo.close()


if __name__ == "__main__":
    print("Iniciando exemplo de uso do KommoService...\n")
    
    # Executar exemplo principal
    asyncio.run(example_usage())
    
    print("\n\n=== TRATAMENTO DE ERROS ===")
    # Executar exemplo de tratamento de erros
    asyncio.run(example_error_handling())
    
    print("\n\nExemplo concluído!")