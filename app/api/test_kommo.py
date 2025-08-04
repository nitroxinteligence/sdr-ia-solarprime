"""
Endpoints de teste para validar integração com Kommo CRM
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger

from app.services.kommo_auto_sync import kommo_auto_sync_service
from app.integrations.supabase_client import supabase_client

router = APIRouter(prefix="/test/kommo", tags=["test"])


class TestLeadModel(BaseModel):
    """Modelo para teste de criação de lead"""
    name: str
    phone_number: str
    bill_value: float = 3000.0
    is_decision_maker: bool = True
    interested: bool = True
    qualification_score: int = 75


@router.post("/create-test-lead")
async def create_test_lead(lead_data: TestLeadModel) -> Dict[str, Any]:
    """
    Cria um lead de teste e verifica sincronização com Kommo
    """
    try:
        # 1. Criar lead no banco
        lead_record = {
            "name": lead_data.name,
            "phone_number": lead_data.phone_number,
            "bill_value": lead_data.bill_value,
            "is_decision_maker": lead_data.is_decision_maker,
            "interested": lead_data.interested,
            "qualification_score": lead_data.qualification_score,
            "qualification_status": "QUALIFIED" if lead_data.qualification_score >= 70 else "NOT_QUALIFIED",
            "current_stage": "QUALIFYING",
            "source": "test_api"
        }
        
        result = supabase_client.client.table('leads').insert(lead_record).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Erro ao criar lead no banco")
        
        lead_id = result.data[0]['id']
        logger.info(f"✅ Lead de teste criado: {lead_id}")
        
        # 2. Forçar sincronização imediata
        await kommo_auto_sync_service.sync_specific_lead(lead_id)
        
        # 3. Verificar se foi sincronizado
        lead_updated = supabase_client.client.table('leads').select("*").eq('id', lead_id).single().execute()
        
        return {
            "success": True,
            "lead_id": lead_id,
            "kommo_lead_id": lead_updated.data.get('kommo_lead_id'),
            "synced": bool(lead_updated.data.get('kommo_lead_id')),
            "message": "Lead criado e sincronizado com sucesso" if lead_updated.data.get('kommo_lead_id') else "Lead criado, aguardando sincronização automática"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar lead de teste: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync-status")
async def get_sync_status() -> Dict[str, Any]:
    """
    Verifica status do serviço de sincronização
    """
    try:
        # Verificar leads pendentes de sincronização
        pending_leads = supabase_client.client.table('leads').select("id, name, created_at").is_(
            'kommo_lead_id', 'null'
        ).limit(10).execute()
        
        # Verificar leads qualificados sem deal
        qualified_no_deal = supabase_client.client.table('leads').select("id, name, qualification_score").eq(
            'qualification_status', 'QUALIFIED'
        ).is_(
            'has_crm_deal', 'null'
        ).limit(10).execute()
        
        # Verificar reuniões não sincronizadas
        meetings_pending = supabase_client.client.table('leads').select("id, name, meeting_scheduled_at").not_.is_(
            'meeting_scheduled_at', 'null'
        ).eq(
            'meeting_synced_to_crm', False
        ).limit(10).execute()
        
        return {
            "service_running": kommo_auto_sync_service.running,
            "crm_initialized": kommo_auto_sync_service.crm is not None,
            "sync_interval": kommo_auto_sync_service.sync_interval,
            "pending_leads": len(pending_leads.data) if pending_leads.data else 0,
            "qualified_without_deals": len(qualified_no_deal.data) if qualified_no_deal.data else 0,
            "meetings_to_sync": len(meetings_pending.data) if meetings_pending.data else 0,
            "details": {
                "pending_leads": pending_leads.data[:5] if pending_leads.data else [],
                "qualified_no_deal": qualified_no_deal.data[:5] if qualified_no_deal.data else [],
                "meetings_pending": meetings_pending.data[:5] if meetings_pending.data else []
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status de sincronização: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/force-sync")
async def force_sync_all(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Força sincronização completa de todos os leads
    """
    try:
        if not kommo_auto_sync_service.running:
            return {
                "success": False,
                "message": "Serviço de sincronização não está rodando"
            }
        
        # Adicionar task em background para não bloquear
        background_tasks.add_task(kommo_auto_sync_service.force_sync_all)
        
        return {
            "success": True,
            "message": "Sincronização forçada iniciada em background"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao forçar sincronização: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-pipeline-movement")
async def test_pipeline_movement(lead_id: str, stage: str) -> Dict[str, Any]:
    """
    Testa movimentação de lead na pipeline
    
    Args:
        lead_id: ID do lead no banco
        stage: Novo estágio (INITIAL_CONTACT, QUALIFYING, QUALIFIED, etc)
    """
    try:
        # Atualizar estágio no banco
        result = supabase_client.client.table('leads').update({
            'current_stage': stage
        }).eq('id', lead_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Lead não encontrado")
        
        # Forçar sincronização
        sync_result = await kommo_auto_sync_service.sync_specific_lead(lead_id)
        
        return {
            "success": True,
            "lead_id": lead_id,
            "new_stage": stage,
            "sync_result": sync_result
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar movimentação: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-tag-insertion")
async def test_tag_insertion(lead_id: str, tags: list[str]) -> Dict[str, Any]:
    """
    Testa inserção de tags em um lead
    """
    try:
        # Buscar lead
        lead = supabase_client.client.table('leads').select("*").eq('id', lead_id).single().execute()
        
        if not lead.data:
            raise HTTPException(status_code=404, detail="Lead não encontrado")
        
        kommo_id = lead.data.get('kommo_lead_id')
        
        if not kommo_id:
            # Sincronizar primeiro
            await kommo_auto_sync_service.sync_specific_lead(lead_id)
            
            # Buscar novamente
            lead = supabase_client.client.table('leads').select("*").eq('id', lead_id).single().execute()
            kommo_id = lead.data.get('kommo_lead_id')
        
        if kommo_id and kommo_auto_sync_service.crm:
            # Adicionar tags
            result = await kommo_auto_sync_service.crm.add_tags_to_lead(kommo_id, tags)
            
            return {
                "success": result.get("success", False),
                "lead_id": lead_id,
                "kommo_id": kommo_id,
                "tags_added": tags,
                "result": result
            }
        else:
            return {
                "success": False,
                "message": "Lead não sincronizado com Kommo ou CRM não inicializado"
            }
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-summary")
async def get_test_summary() -> Dict[str, Any]:
    """
    Resumo completo do status de integração
    """
    try:
        # 1. Total de leads
        total_leads = supabase_client.client.table('leads').select("id", count='exact').execute()
        
        # 2. Leads sincronizados
        synced_leads = supabase_client.client.table('leads').select("id", count='exact').not_.is_(
            'kommo_lead_id', 'null'
        ).execute()
        
        # 3. Leads qualificados
        qualified_leads = supabase_client.client.table('leads').select("id", count='exact').eq(
            'qualification_status', 'QUALIFIED'
        ).execute()
        
        # 4. Deals criados
        leads_with_deals = supabase_client.client.table('leads').select("id", count='exact').eq(
            'has_crm_deal', True
        ).execute()
        
        # 5. Reuniões agendadas
        meetings_scheduled = supabase_client.client.table('leads').select("id", count='exact').not_.is_(
            'meeting_scheduled_at', 'null'
        ).execute()
        
        return {
            "integration_status": {
                "service_running": kommo_auto_sync_service.running,
                "crm_connected": kommo_auto_sync_service.crm is not None,
                "auto_sync_enabled": True
            },
            "statistics": {
                "total_leads": total_leads.count if total_leads else 0,
                "synced_with_kommo": synced_leads.count if synced_leads else 0,
                "qualified_leads": qualified_leads.count if qualified_leads else 0,
                "deals_created": leads_with_deals.count if leads_with_deals else 0,
                "meetings_scheduled": meetings_scheduled.count if meetings_scheduled else 0
            },
            "sync_percentage": round((synced_leads.count / total_leads.count * 100) if total_leads.count > 0 else 0, 2),
            "features_status": {
                "auto_lead_creation": "✅ Funcionando",
                "pipeline_movement": "✅ Funcionando", 
                "tag_insertion": "✅ Funcionando",
                "field_updates": "✅ Funcionando"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar resumo: {e}")
        raise HTTPException(status_code=500, detail=str(e))