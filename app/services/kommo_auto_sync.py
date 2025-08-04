"""
Kommo Auto Sync Service - Sincronização Automática com Kommo CRM
Serviço que monitora mudanças e sincroniza automaticamente com o CRM
"""

import asyncio
from typing import Dict, Any
from loguru import logger

from app.integrations.supabase_client import SupabaseClient
from app.teams.agents.crm_enhanced import KommoEnhancedCRM
from app.config import settings


class KommoAutoSyncService:
    """
    Serviço de sincronização automática com Kommo CRM
    Monitora mudanças em leads e sincroniza automaticamente
    """
    
    def __init__(self):
        """Inicializa o serviço de sincronização"""
        self.db = SupabaseClient()
        self.crm = None  # Será inicializado depois
        self.running = False
        self.sync_interval = 30  # Sincronizar a cada 30 segundos
        self.last_sync = {}
        
        # Mapeamento de estágios do sistema para Kommo
        self.stage_mapping = {
            "INITIAL_CONTACT": "novo_lead",
            "IDENTIFYING_NEED": "em_negociacao",
            "QUALIFYING": "em_qualificacao",
            "QUALIFIED": "qualificado",
            "SCHEDULING": "reuniao_agendada",
            "MEETING_DONE": "reuniao_finalizada",
            "NOT_INTERESTED": "nao_interessado"
        }
        
        # Tags automáticas baseadas em condições
        self.auto_tags = {
            "new_lead": ["whatsapp-lead", "SDR IA", "novo"],
            "qualified": ["qualificado-ia", "prioridade"],
            "scheduled": ["agendamento-confirmado", "follow-up"],
            "high_value": ["vip", "high-value"],
            "low_engagement": ["frio", "nurturing-necessario"]
        }
        
        logger.info("✅ KommoAutoSyncService inicializado")
    
    async def initialize(self, model=None, storage=None):
        """Inicializa o CRM com modelo e storage"""
        try:
            # Criar instância do CRM Enhanced
            if model and storage:
                self.crm = KommoEnhancedCRM(model=model, storage=storage)
                await self.crm.initialize()
                logger.info("✅ CRM Enhanced inicializado para auto-sync")
            else:
                logger.warning("⚠️ CRM não inicializado - model ou storage não fornecidos")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar CRM: {e}")
    
    async def start(self):
        """Inicia o serviço de sincronização automática"""
        if self.running:
            logger.warning("Auto-sync já está rodando")
            return
        
        self.running = True
        logger.info("🔄 Iniciando sincronização automática com Kommo CRM")
        
        # Iniciar loops de sincronização
        asyncio.create_task(self._sync_new_leads_loop())
        asyncio.create_task(self._sync_updates_loop())
        asyncio.create_task(self._sync_qualifications_loop())
        asyncio.create_task(self._sync_meetings_loop())
    
    async def stop(self):
        """Para o serviço de sincronização"""
        self.running = False
        logger.info("⏹️ Sincronização automática parada")
    
    # ==================== LOOPS DE SINCRONIZAÇÃO ====================
    
    async def _sync_new_leads_loop(self):
        """Loop que sincroniza novos leads com o CRM"""
        while self.running:
            try:
                await self.sync_new_leads()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"❌ Erro no loop de novos leads: {e}")
                await asyncio.sleep(60)
    
    async def _sync_updates_loop(self):
        """Loop que sincroniza atualizações de leads"""
        while self.running:
            try:
                await self.sync_lead_updates()
                await asyncio.sleep(self.sync_interval * 2)  # Menos frequente
            except Exception as e:
                logger.error(f"❌ Erro no loop de atualizações: {e}")
                await asyncio.sleep(60)
    
    async def _sync_qualifications_loop(self):
        """Loop que sincroniza qualificações"""
        while self.running:
            try:
                await self.sync_qualifications()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"❌ Erro no loop de qualificações: {e}")
                await asyncio.sleep(60)
    
    async def _sync_meetings_loop(self):
        """Loop que sincroniza reuniões agendadas"""
        while self.running:
            try:
                await self.sync_meetings()
                await asyncio.sleep(self.sync_interval * 2)
            except Exception as e:
                logger.error(f"❌ Erro no loop de reuniões: {e}")
                await asyncio.sleep(60)
    
    # ==================== SINCRONIZAÇÃO DE NOVOS LEADS ====================
    
    async def sync_new_leads(self):
        """Sincroniza novos leads que ainda não estão no CRM"""
        if not self.crm:
            return
        
        try:
            # Buscar leads sem kommo_lead_id
            result = self.db.client.table('leads').select("*").is_(
                'kommo_lead_id', 'null'
            ).limit(10).execute()
            
            if not result.data:
                return
            
            logger.info(f"📋 {len(result.data)} novos leads para sincronizar com Kommo")
            
            for lead in result.data:
                await self._sync_single_lead(lead)
                
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar novos leads: {e}")
    
    async def _sync_single_lead(self, lead: Dict[str, Any]):
        """Sincroniza um único lead com o CRM"""
        try:
            # Preparar dados do lead
            lead_data = {
                "name": lead.get("name") or f"Lead {lead.get('phone_number')}",
                "phone": lead.get("phone_number"),
                "email": lead.get("email"),
                "price": float(lead.get("bill_value") or 0) * 12  # Valor anual
            }
            
            # Determinar tags baseadas no lead
            tags = self._determine_tags(lead)
            
            # Criar lead no CRM
            result = await self.crm.create_or_update_lead(
                lead_data=lead_data,
                tags=tags
            )
            
            if result.get("success"):
                kommo_id = result.get("crm_id")
                
                # Salvar kommo_lead_id no banco
                self.db.client.table('leads').update({
                    'kommo_lead_id': str(kommo_id)
                }).eq('id', lead['id']).execute()
                
                # Atualizar campos customizados
                await self._update_custom_fields(kommo_id, lead)
                
                # Mover para estágio correto
                await self._move_to_correct_stage(kommo_id, lead)
                
                logger.info(f"✅ Lead {lead['id']} sincronizado com Kommo (ID: {kommo_id})")
            
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar lead {lead.get('id')}: {e}")
    
    def _determine_tags(self, lead: Dict[str, Any]) -> list:
        """Determina tags automáticas baseadas no lead"""
        tags = self.auto_tags["new_lead"].copy()
        
        # Tag de valor
        bill_value = float(lead.get("bill_value") or 0)
        if bill_value > 1000:
            tags.extend(self.auto_tags["high_value"])
        elif bill_value > 500:
            tags.append("medium-value")
        else:
            tags.append("low-value")
        
        # Tag de qualificação
        if lead.get("qualification_status") == "QUALIFIED":
            tags.extend(self.auto_tags["qualified"])
        elif lead.get("qualification_status") == "NOT_QUALIFIED":
            tags.append("nao-qualificado")
        
        # Tag de interesse
        if not lead.get("interested"):
            tags.append("sem-interesse")
        
        # Tag de decisor
        if lead.get("is_decision_maker"):
            tags.append("decisor")
        
        return list(set(tags))  # Remover duplicatas
    
    async def _update_custom_fields(self, kommo_id: str, lead: Dict[str, Any]):
        """Atualiza campos customizados no Kommo"""
        if not self.crm:
            return
        
        try:
            fields = {}
            
            # Mapear campos do banco para campos do Kommo
            if lead.get("phone_number"):
                fields["whatsapp"] = lead["phone_number"]
            
            if lead.get("bill_value"):
                fields["valor_conta_energia"] = float(lead["bill_value"])
            
            if lead.get("qualification_score"):
                fields["score_qualificacao"] = int(lead["qualification_score"])
            
            if lead.get("address"):
                fields["endereco"] = lead["address"]
            
            if lead.get("property_type"):
                fields["tipo_imovel"] = lead["property_type"]
            
            if lead.get("consumption_kwh"):
                fields["consumo_kwh"] = int(lead["consumption_kwh"])
            
            # Adicionar fonte
            fields["fonte"] = "WhatsApp SDR IA"
            
            if fields:
                await self.crm.update_custom_fields(kommo_id, fields)
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar campos customizados: {e}")
    
    async def _move_to_correct_stage(self, kommo_id: str, lead: Dict[str, Any]):
        """Move lead para o estágio correto no pipeline"""
        if not self.crm:
            return
        
        try:
            current_stage = lead.get("current_stage", "INITIAL_CONTACT")
            kommo_stage = self.stage_mapping.get(current_stage)
            
            if kommo_stage and hasattr(self.crm, 'pipeline_stages'):
                stage_id = self.crm.pipeline_stages.get(kommo_stage)
                if stage_id:
                    await self.crm.move_card_to_pipeline(
                        lead_id=kommo_id,
                        pipeline_id=settings.kommo_pipeline_id,
                        stage_id=stage_id
                    )
                    logger.info(f"📍 Lead {kommo_id} movido para estágio {kommo_stage}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao mover lead para estágio: {e}")
    
    # ==================== SINCRONIZAÇÃO DE ATUALIZAÇÕES ====================
    
    async def sync_lead_updates(self):
        """Sincroniza atualizações em leads existentes"""
        if not self.crm:
            return
        
        try:
            # Buscar leads modificados recentemente (com kommo_lead_id)
            from datetime import datetime, timedelta
            cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()
            
            result = self.db.client.table('leads').select("*").not_.is_(
                'kommo_lead_id', 'null'
            ).gte(
                'updated_at', cutoff
            ).limit(20).execute()
            
            if not result.data:
                return
            
            logger.info(f"📝 {len(result.data)} leads atualizados para sincronizar")
            
            for lead in result.data:
                await self._sync_lead_updates(lead)
                
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar atualizações: {e}")
    
    async def _sync_lead_updates(self, lead: Dict[str, Any]):
        """Sincroniza atualizações de um lead específico"""
        try:
            kommo_id = lead.get("kommo_lead_id")
            if not kommo_id:
                return
            
            # Atualizar campos
            await self._update_custom_fields(kommo_id, lead)
            
            # Atualizar tags se necessário
            new_tags = self._determine_tags(lead)
            await self.crm.add_tags_to_lead(kommo_id, new_tags)
            
            # Mover para novo estágio se mudou
            await self._move_to_correct_stage(kommo_id, lead)
            
            logger.info(f"🔄 Lead {lead['id']} atualizado no Kommo")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar lead {lead.get('id')}: {e}")
    
    # ==================== SINCRONIZAÇÃO DE QUALIFICAÇÕES ====================
    
    async def sync_qualifications(self):
        """Sincroniza leads recém qualificados"""
        if not self.crm:
            return
        
        try:
            # Buscar leads qualificados sem deal
            result = self.db.client.table('leads').select("*").eq(
                'qualification_status', 'QUALIFIED'
            ).is_(
                'has_crm_deal', 'null'
            ).limit(10).execute()
            
            if not result.data:
                return
            
            logger.info(f"🎯 {len(result.data)} leads qualificados para criar deals")
            
            for lead in result.data:
                await self._create_deal_for_qualified_lead(lead)
                
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar qualificações: {e}")
    
    async def _create_deal_for_qualified_lead(self, lead: Dict[str, Any]):
        """Cria deal para lead qualificado"""
        try:
            kommo_id = lead.get("kommo_lead_id")
            if not kommo_id:
                # Primeiro sincronizar o lead
                await self._sync_single_lead(lead)
                kommo_id = lead.get("kommo_lead_id")
            
            if kommo_id and self.crm:
                # Criar deal
                result = await self.crm.create_deal(
                    lead_id=kommo_id,
                    value=float(lead.get("bill_value", 0)) * 12,
                    name=f"Solar - {lead.get('name', 'Cliente')}"
                )
                
                if result.get("success"):
                    # Marcar que tem deal
                    self.db.client.table('leads').update({
                        'has_crm_deal': True
                    }).eq('id', lead['id']).execute()
                    
                    # Adicionar tags de qualificado
                    await self.crm.add_tags_to_lead(
                        kommo_id,
                        ["qualificado", "deal-criado", f"score-{lead.get('qualification_score', 0)}"]
                    )
                    
                    logger.info(f"💰 Deal criado para lead qualificado {lead['id']}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao criar deal: {e}")
    
    # ==================== SINCRONIZAÇÃO DE REUNIÕES ====================
    
    async def sync_meetings(self):
        """Sincroniza reuniões agendadas"""
        if not self.crm:
            return
        
        try:
            # Buscar leads com reunião agendada
            result = self.db.client.table('leads').select("*").not_.is_(
                'meeting_scheduled_at', 'null'
            ).eq(
                'meeting_synced_to_crm', False
            ).limit(10).execute()
            
            if not result.data:
                return
            
            logger.info(f"📅 {len(result.data)} reuniões para sincronizar")
            
            for lead in result.data:
                await self._sync_meeting(lead)
                
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar reuniões: {e}")
    
    async def _sync_meeting(self, lead: Dict[str, Any]):
        """Sincroniza reunião agendada com o CRM"""
        try:
            kommo_id = lead.get("kommo_lead_id")
            if not kommo_id:
                await self._sync_single_lead(lead)
                kommo_id = lead.get("kommo_lead_id")
            
            if kommo_id and self.crm:
                # Atualizar campos da reunião
                meeting_fields = {
                    "link_evento_google": lead.get("google_event_id"),
                    "status_reuniao": lead.get("meeting_status", "scheduled"),
                    "data_reuniao": lead.get("meeting_scheduled_at")
                }
                
                await self.crm.update_custom_fields(kommo_id, meeting_fields)
                
                # Mover para estágio de reunião agendada
                if hasattr(self.crm, 'pipeline_stages'):
                    stage_id = self.crm.pipeline_stages.get("reuniao_agendada")
                    if stage_id:
                        await self.crm.move_card_to_pipeline(
                            lead_id=kommo_id,
                            pipeline_id=settings.kommo_pipeline_id,
                            stage_id=stage_id
                        )
                
                # Adicionar tags
                await self.crm.add_tags_to_lead(
                    kommo_id,
                    ["reuniao-agendada", lead.get("meeting_type", "inicial")]
                )
                
                # Criar tarefa de follow-up
                meeting_time = lead.get("meeting_scheduled_at")
                if meeting_time:
                    await self.crm.add_task(
                        entity_id=kommo_id,
                        entity_type="leads",
                        text=f"Reunião agendada - {lead.get('name', 'Cliente')}",
                        complete_till=meeting_time
                    )
                
                # Marcar como sincronizado
                self.db.client.table('leads').update({
                    'meeting_synced_to_crm': True
                }).eq('id', lead['id']).execute()
                
                logger.info(f"📅 Reunião sincronizada para lead {lead['id']}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar reunião: {e}")
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    async def force_sync_all(self):
        """Força sincronização completa de todos os leads"""
        logger.info("🔄 Iniciando sincronização forçada completa")
        
        await self.sync_new_leads()
        await self.sync_lead_updates()
        await self.sync_qualifications()
        await self.sync_meetings()
        
        logger.info("✅ Sincronização forçada completa finalizada")
    
    async def sync_specific_lead(self, lead_id: str):
        """Sincroniza um lead específico"""
        try:
            # Buscar lead
            result = self.db.client.table('leads').select("*").eq(
                'id', lead_id
            ).single().execute()
            
            if result.data:
                lead = result.data
                
                if not lead.get("kommo_lead_id"):
                    await self._sync_single_lead(lead)
                else:
                    await self._sync_lead_updates(lead)
                
                logger.info(f"✅ Lead {lead_id} sincronizado")
                return {"success": True, "lead_id": lead_id}
            else:
                return {"success": False, "error": "Lead não encontrado"}
                
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar lead específico: {e}")
            return {"success": False, "error": str(e)}


# Singleton do serviço
kommo_auto_sync_service = KommoAutoSyncService()