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
from app.utils.safe_conversions import safe_int_conversion


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Converte valor para float de forma segura
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se a conversão falhar
        
    Returns:
        float: Valor convertido ou default
    """
    if value is None:
        return default
    
    # Se já for float, retorna direto
    if isinstance(value, (int, float)):
        return float(value)
    
    # Se for string, tenta converter
    if isinstance(value, str):
        # Remove espaços e verifica casos especiais
        value = value.strip()
        
        # Casos especiais de strings vazias ou "None"
        if not value or value.lower() in ['none', 'null', 'nan']:
            return default
        
        # Tenta converter removendo símbolos de moeda comuns
        value = value.replace('R$', '').replace('$', '').replace(',', '.')
        
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Não foi possível converter '{value}' para float. Usando valor padrão {default}")
            return default
    
    # Para qualquer outro tipo, retorna default
    return default


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
            # Valores que o agente REALMENTE retorna para nomes em português no Kommo
            "INITIAL_CONTACT": "Novo Lead",
            "EM_QUALIFICACAO": "Em Qualificação",
            "QUALIFICADO": "Qualificado",
            "REUNIAO_AGENDADA": "Reunião Agendada",
            "NAO_INTERESSADO": "Não Interessado",
            "EM_NEGOCIACAO": "Em Negociação",
            # Manter valores antigos para compatibilidade
            "IDENTIFYING_NEED": "Em Negociação",
            "QUALIFYING": "Em Qualificação",
            "QUALIFIED": "Qualificado",
            "SCHEDULING": "Reunião Agendada",
            "MEETING_DONE": "Reunião Finalizada",
            "NOT_INTERESTED": "Não Interessado",
            # Adicionar mapeamento para valores em snake_case também
            "novo_lead": "Novo Lead",
            "em_qualificacao": "Em Qualificação",
            "qualificado": "Qualificado",
            "reuniao_agendada": "Reunião Agendada",
            "nao_interessado": "Não Interessado"
        }
        
        # Tags automáticas baseadas em condições (tags oficiais do sistema)
        self.auto_tags = {
            "new_lead": ["whatsapp-lead"],
            "qualified": ["qualificado-ia"],
            "scheduled": ["agendamento-pendente"],
            "follow_up": ["follow-up-automatico"],
            "hot": ["lead-quente"],
            "warm": ["lead-morno"],
            "cold": ["lead-frio"],
            "no_response": ["sem-resposta"],
            "invalid_number": ["numero-invalido"]
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
        # asyncio.create_task(self._sync_meetings_loop())  # DESABILITADO - Sem Google Calendar
    
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
            # Preparar dados do lead com todos os campos necessários
            lead_data = {
                "name": lead.get("name") or f"Lead {lead.get('phone_number')}",
                "phone": lead.get("phone_number"),
                "email": lead.get("email"),
                "bill_value": lead.get("bill_value"),
                "qualification_score": lead.get("qualification_score"),
                "price": safe_float_conversion(lead.get("bill_value")) * 12  # Valor anual
            }
            
            # Determinar tags baseadas no lead
            tags = self._determine_tags(lead)
            
            # Criar lead no CRM usando método direto (sem @tool decorator)
            if hasattr(self.crm, 'create_or_update_lead_direct'):
                result = await self.crm.create_or_update_lead_direct(
                    lead_data=lead_data,
                    tags=tags
                )
            else:
                logger.error("Método create_or_update_lead_direct não encontrado no CRM")
                result = {"success": False, "error": "Método não disponível"}
            
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
                
                # Retornar o resultado com o kommo_id
                return {
                    "success": True,
                    "kommo_id": kommo_id,
                    "lead_id": lead['id']
                }
            else:
                logger.error(f"❌ Falha ao criar/atualizar lead no Kommo: {result}")
                return {"success": False, "error": result.get("error", "Erro desconhecido")}
            
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar lead {lead.get('id')}: {e}")
            return {"success": False, "error": str(e)}
    
    def _determine_tags(self, lead: Dict[str, Any]) -> list:
        """Determina tags automáticas baseadas no lead"""
        tags = []
        
        # Tag base para todos os leads do WhatsApp
        tags.extend(self.auto_tags["new_lead"])
        
        # Tag de temperatura baseada no score (CORREÇÃO: uso seguro para evitar NoneType error)
        qualification_score = safe_int_conversion(lead.get("qualification_score"), 0)
        if qualification_score >= 70:
            tags.extend(self.auto_tags["hot"])  # lead-quente
        elif qualification_score >= 40:
            tags.extend(self.auto_tags["warm"])  # lead-morno
        else:
            tags.extend(self.auto_tags["cold"])  # lead-frio
        
        # Tag de qualificação
        if lead.get("qualification_status") == "QUALIFIED":
            tags.extend(self.auto_tags["qualified"])  # qualificado-ia
        
        # Tag de agendamento
        if lead.get("meeting_scheduled_at"):
            tags.extend(self.auto_tags["scheduled"])  # agendamento-pendente
        
        # Tag de follow-up
        if lead.get("follow_up_scheduled"):
            tags.extend(self.auto_tags["follow_up"])  # follow-up-automatico
        
        # Tag de sem resposta (baseado no último contato)
        last_contact = lead.get("last_contact_at")
        if last_contact:
            from datetime import datetime
            last_contact_date = datetime.fromisoformat(last_contact.replace('Z', '+00:00'))
            if (datetime.now() - last_contact_date).days > 3:
                tags.extend(self.auto_tags["no_response"])  # sem-resposta
        
        # Tag de número inválido
        if lead.get("phone_invalid") or lead.get("whatsapp_invalid"):
            tags.extend(self.auto_tags["invalid_number"])  # numero-invalido
        
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
                fields["valor_conta_energia"] = safe_float_conversion(lead.get("bill_value"))
            
            if lead.get("qualification_score"):
                fields["score_qualificacao"] = safe_int_conversion(lead.get("qualification_score"))
            
            if lead.get("address"):
                fields["endereco"] = lead["address"]
            
            if lead.get("property_type"):
                fields["tipo_imovel"] = lead["property_type"]
            
            if lead.get("consumption_kwh"):
                fields["consumo_kwh"] = safe_int_conversion(lead.get("consumption_kwh"))
            
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
            # Como não temos campo kommo_deal_id, vamos usar outro critério
            # Por exemplo, leads qualificados sem kommo_lead_id ainda
            result = self.db.client.table('leads').select("*").eq(
                'qualification_status', 'QUALIFIED'
            ).not_.is_(
                'kommo_lead_id', 'null'  # Só criar deal para leads já sincronizados
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
            # VALIDAÇÃO: Verificar se o lead tem score válido antes de prosseguir
            score = lead.get('qualification_score')
            if score is None:
                logger.warning(f"🚨 Lead {lead.get('id')} está qualificado mas não tem score. Pulando criação do deal por agora.")
                return  # Sai da função se o score não existir
            
            kommo_id = lead.get("kommo_lead_id")
            if not kommo_id:
                # Primeiro sincronizar o lead
                await self._sync_single_lead(lead)
                kommo_id = lead.get("kommo_lead_id")
            
            if kommo_id and self.crm:
                # Criar deal
                result = await self.crm.create_deal(
                    lead_id=kommo_id,
                    value=safe_float_conversion(lead.get("bill_value")) * 12,
                    name=f"Solar - {lead.get('name', 'Cliente')}"
                )
                
                if result.get("success"):
                    # Marcar que tem deal - usar algum campo existente ou apenas logar
                    # Como não temos kommo_deal_id, vamos apenas logar o sucesso
                    logger.info(f"✅ Deal criado para lead {lead['id']} - Deal ID: {result.get('deal_id')}")
                    
                    # Adicionar tags de qualificado
                    qualified_tags = ["qualificado-ia"]
                    
                    # Adicionar tag de temperatura baseada no score (CORREÇÃO: uso seguro)
                    score = safe_int_conversion(lead.get('qualification_score'), 0)
                    if score >= 70:
                        qualified_tags.append("lead-quente")
                    elif score >= 40:
                        qualified_tags.append("lead-morno")
                    
                    await self.crm.add_tags_to_lead(kommo_id, qualified_tags)
                    
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
            # Como não temos campo kommo_meeting_id, vamos usar apenas meeting_scheduled_at
            result = self.db.client.table('leads').select("*").not_.is_(
                'meeting_scheduled_at', 'null'
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
            
            # Se não tem kommo_id, tentar sincronizar primeiro
            if not kommo_id:
                logger.info(f"🔄 Lead {lead.get('id')} não tem kommo_id, sincronizando primeiro...")
                sync_result = await self._sync_single_lead(lead)
                if sync_result and isinstance(sync_result, dict):
                    kommo_id = sync_result.get("kommo_id")
                    # Atualizar o lead local com o novo kommo_id
                    lead["kommo_lead_id"] = kommo_id
                else:
                    logger.error(f"❌ Falha ao sincronizar lead {lead.get('id')} com Kommo")
                    return
            
            # Validar que temos um kommo_id válido
            if not kommo_id or kommo_id == "None" or kommo_id == 0:
                logger.error(f"❌ kommo_id inválido para lead {lead.get('id')}: {kommo_id}")
                return
            
            # Log para debug
            logger.info(f"✅ Sincronizando reunião para lead {lead.get('id')} com kommo_id {kommo_id}")
            
            if self.crm:
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
                meeting_tags = ["agendamento-pendente"]
                
                # Se já está qualificado, manter tag
                if lead.get("qualification_status") == "QUALIFIED":
                    meeting_tags.append("qualificado-ia")
                
                await self.crm.add_tags_to_lead(kommo_id, meeting_tags)
                
                # Criar tarefa de follow-up
                meeting_time = lead.get("meeting_scheduled_at")
                if meeting_time:
                    # Garantir que temos um nome válido
                    lead_name = lead.get('name')
                    if not lead_name or lead_name == "None":
                        lead_name = f"Cliente {lead.get('phone_number', '')}"
                    
                    await self.crm.add_task(
                        entity_id=kommo_id,
                        entity_type="leads",
                        text=f"Reunião agendada - {lead_name}",
                        complete_till=meeting_time
                    )
                
                # Marcar como sincronizado salvando algum identificador
                # Como não temos o campo meeting_synced_to_crm, vamos apenas logar
                # self.db.client.table('leads').update({
                #     'kommo_meeting_id': 'synced'
                # }).eq('id', lead['id']).execute()
                
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