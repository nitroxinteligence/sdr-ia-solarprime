"""
Kommo CRM Service - Versão Simplificada com Long-Lived Token
============================================================
Substitui completamente o KommoService para usar Long-Lived Token
"""

import httpx
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from config.config import get_config
from models.kommo_models import (
    KommoLead, KommoContact, KommoTask, KommoNote,
    LeadStatus, SolutionType, TaskType, NoteType,
    KommoCustomField, KommoResponse
)


class KommoService:
    """Serviço de integração com Kommo CRM usando Long-Lived Token"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = f"https://{self.config.kommo.subdomain}.kommo.com/api/v4"
        self.subdomain = self.config.kommo.subdomain
        
        # Long-Lived Token direto do ambiente
        self.token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
        
        # Cache de configurações
        self._pipeline_id = None
        self._stage_ids = None
        self._custom_fields = None
        
        if self.token:
            logger.info(f"✅ KommoService inicializado com Long-Lived Token para: {self.subdomain}")
        else:
            logger.error("❌ Long-Lived Token não encontrado! Configure KOMMO_LONG_LIVED_TOKEN no .env")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retry_on_401: bool = True
    ) -> Dict:
        """Faz requisição para API do Kommo"""
        try:
            if not self.token:
                raise Exception("Long-Lived Token não configurado!")
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=f"{self.base_url}{endpoint}",
                    headers=headers,
                    json=data,
                    params=params
                )
                
                if response.status_code == 401:
                    logger.error("Token inválido ou expirado! Verifique seu Long-Lived Token.")
                    raise Exception("Token inválido")
                
                response.raise_for_status()
                return response.json() if response.text else {}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            raise
    
    # Resto do código do KommoService original, mas sem dependência de KommoAuth
    
    async def _get_pipeline_config(self) -> int:
        """Obtém ID do pipeline configurado"""
        if self._pipeline_id is None:
            self._pipeline_id = self.config.kommo.pipeline_id
            if self._pipeline_id == 0:
                # Tentar obter o pipeline principal
                pipelines = await self.get_pipelines()
                for pipeline in pipelines:
                    if pipeline.get("is_main"):
                        self._pipeline_id = pipeline["id"]
                        break
            
            # Após obter o pipeline, buscar e cachear os estágios
            if self._pipeline_id:
                await self._load_pipeline_stages()
                
        return self._pipeline_id
    
    async def _load_pipeline_stages(self) -> None:
        """Carrega e cacheia os estágios do pipeline"""
        try:
            # Buscar detalhes do pipeline específico
            response = await self._make_request(
                "GET",
                f"/leads/pipelines/{self._pipeline_id}",
                params={"with": "statuses"}
            )
            
            if not response:
                logger.warning(f"Pipeline {self._pipeline_id} não encontrado")
                return
                
            # Mapear estágios por nome
            self._stage_ids = {}
            statuses = response.get("_embedded", {}).get("statuses", [])
            
            for status in statuses:
                status_name = status["name"].lower()
                status_id = status["id"]
                
                # Mapeamento inteligente baseado em palavras-chave
                if any(word in status_name for word in ["novo", "new", "inicial", "primeiro"]):
                    self._stage_ids["new"] = status_id
                elif any(word in status_name for word in ["qualifica", "analisa", "avalia"]):
                    self._stage_ids["in_qualification"] = status_id
                elif "qualificado" in status_name and "não" not in status_name:
                    self._stage_ids["qualified"] = status_id
                elif any(word in status_name for word in ["reuni", "agend", "meeting", "encontro"]):
                    self._stage_ids["meeting_scheduled"] = status_id
                elif any(word in status_name for word in ["negocia", "proposta", "orçamento"]):
                    self._stage_ids["in_negotiation"] = status_id
                elif any(word in status_name for word in ["ganho", "won", "fechado", "vendido"]):
                    self._stage_ids["won"] = status_id
                elif any(word in status_name for word in ["perdido", "lost", "cancelado"]):
                    self._stage_ids["lost"] = status_id
                elif any(word in status_name for word in ["não interessado", "desistiu", "recusou"]):
                    self._stage_ids["not_interested"] = status_id
                
                # Log do mapeamento
                logger.info(f"Estágio mapeado: '{status['name']}' (ID: {status_id})")
            
            # Se houver IDs configurados no .env, sobrescrever com eles
            env_stage_ids = self.config.kommo.stage_ids
            for key, value in env_stage_ids.items():
                if value > 0:  # Se foi configurado no .env
                    self._stage_ids[key] = value
                    logger.info(f"Estágio '{key}' sobrescrito pelo .env: {value}")
                    
            logger.info(f"Estágios do pipeline carregados: {self._stage_ids}")
            
            # Também carregar campos personalizados
            await self._load_custom_fields()
            
        except Exception as e:
            logger.error(f"Erro ao carregar estágios do pipeline: {str(e)}")
            # Usar valores do .env como fallback
            self._stage_ids = self.config.kommo.stage_ids
    
    async def _load_custom_fields(self) -> None:
        """Carrega e cacheia os campos personalizados"""
        try:
            # Buscar campos personalizados de leads
            response = await self._make_request("GET", "/leads/custom_fields")
            
            if not response:
                logger.warning("Não foi possível obter campos personalizados")
                return
                
            # Mapear campos por nome
            temp_custom_fields = {}
            custom_fields = response.get("_embedded", {}).get("custom_fields", [])
            
            for field in custom_fields:
                field_name = field["name"].lower()
                field_id = field["id"]
                field_type = field.get("type", "")
                
                # Mapeamento inteligente baseado em palavras-chave
                if any(word in field_name for word in ["whatsapp", "whats", "telefone"]):
                    temp_custom_fields["whatsapp_number"] = field_id
                elif any(word in field_name for word in ["energia", "conta", "valor"]):
                    temp_custom_fields["energy_bill_value"] = field_id
                elif any(word in field_name for word in ["score", "qualifica", "pontua"]):
                    temp_custom_fields["qualification_score"] = field_id
                elif any(word in field_name for word in ["solução", "tipo", "plano"]):
                    temp_custom_fields["solution_type"] = field_id
                elif any(word in field_name for word in ["origem", "fonte", "source"]):
                    temp_custom_fields["lead_source"] = field_id
                elif any(word in field_name for word in ["primeira", "mensagem", "inicial"]):
                    temp_custom_fields["first_message"] = field_id
                elif any(word in field_name for word in ["conversa", "chat", "id"]):
                    temp_custom_fields["conversation_id"] = field_id
                
                # Log do mapeamento
                logger.info(f"Campo mapeado: '{field['name']}' (ID: {field_id}, Tipo: {field_type})")
                
                # Se for campo select, mapear também os valores
                if field_type == "select" and "enums" in field:
                    self._map_select_values(field_name, field["enums"])
            
            # Mesclar com configurações do .env (prioridade para .env)
            self._custom_fields = self.config.kommo.custom_fields.copy()
            for key, value in temp_custom_fields.items():
                if key not in self._custom_fields or self._custom_fields[key] == 0:
                    self._custom_fields[key] = value
                    
            logger.info(f"Campos personalizados carregados: {self._custom_fields}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar campos personalizados: {str(e)}")
            # Usar valores do .env como fallback
            self._custom_fields = self.config.kommo.custom_fields
    
    def _map_select_values(self, field_name: str, enums: List[Dict]) -> None:
        """Mapeia valores de campos select"""
        if "solução" in field_name or "solution" in field_name:
            # Mapear valores de tipo de solução
            for enum in enums:
                enum_value = enum["value"].lower()
                enum_id = enum["id"]
                
                if "própria" in enum_value or "residencial" in enum_value:
                    self.config.kommo.solution_type_values["usina_propria"] = enum_id
                elif "parceira" in enum_value or "fazenda" in enum_value:
                    self.config.kommo.solution_type_values["usina_parceira"] = enum_id
                elif "consórcio" in enum_value:
                    self.config.kommo.solution_type_values["consorcio"] = enum_id
                
                logger.info(f"  - Valor select mapeado: '{enum['value']}' = {enum_id}")
    
    async def _get_stage_id(self, status: LeadStatus) -> int:
        """Obtém ID do estágio baseado no status"""
        # Garantir que o pipeline e estágios foram carregados
        if self._pipeline_id is None:
            await self._get_pipeline_config()
            
        if self._stage_ids is None:
            self._stage_ids = self.config.kommo.stage_ids
        
        status_key = status.value
        stage_id = self._stage_ids.get(status_key, 0)
        
        if stage_id == 0:
            logger.warning(f"Stage ID não encontrado para status: {status_key}")
            logger.warning(f"Estágios disponíveis: {self._stage_ids}")
            
            # Tentar mapear por similaridade se não encontrou exato
            status_map = {
                "new": ["novo", "inicial", "primeiro"],
                "in_qualification": ["qualificação", "análise", "avaliação"],
                "qualified": ["qualificado", "aprovado"],
                "meeting_scheduled": ["reunião", "agendado"],
                "not_interested": ["não interessado", "desistiu"]
            }
            
            # Buscar mapeamento alternativo
            for key, alternatives in status_map.items():
                if status_key == key and key in self._stage_ids:
                    return self._stage_ids[key]
        
        return stage_id
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def create_or_update_lead(self, lead_data: KommoLead) -> Dict:
        """Cria ou atualiza lead no Kommo"""
        try:
            # Buscar lead existente pelo WhatsApp
            existing_lead = await self.find_lead_by_whatsapp(lead_data.whatsapp)
            
            if existing_lead:
                # Atualizar lead existente
                logger.info(f"Lead encontrado: {existing_lead['id']} - Atualizando...")
                return await self.update_lead(existing_lead["id"], lead_data)
            else:
                # Criar novo lead
                logger.info("Criando novo lead...")
                return await self.create_lead(lead_data)
                
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar lead: {str(e)}")
            raise
    
    async def create_lead(self, lead_data: KommoLead) -> Dict:
        """Cria novo lead no Kommo"""
        try:
            # Obter configurações
            pipeline_id = await self._get_pipeline_config()
            stage_id = await self._get_stage_id(LeadStatus.NEW)
            
            # Preparar campos customizados
            custom_fields_values = await self._prepare_custom_fields(lead_data)
            
            # Determinar responsável
            responsible_user_id = self._determine_responsible_user(lead_data)
            
            # Adicionar tag padrão
            if "WhatsApp Lead" not in lead_data.tags:
                lead_data.tags.append("WhatsApp Lead")
            
            # Dados do lead
            lead_payload = {
                "name": lead_data.name,
                "pipeline_id": pipeline_id,
                "status_id": stage_id,
                "responsible_user_id": responsible_user_id,
                "custom_fields_values": custom_fields_values,
                "_embedded": {
                    "tags": [{"name": tag} for tag in lead_data.tags]
                }
            }
            
            # Criar lead
            response = await self._make_request("POST", "/leads", [lead_payload])
            
            if "_embedded" in response and "leads" in response["_embedded"]:
                lead = response["_embedded"]["leads"][0]
                
                # Criar contato e associar
                contact = await self.create_contact({
                    "name": lead_data.name,
                    "phone": lead_data.phone,
                    "whatsapp": lead_data.whatsapp,
                    "email": lead_data.email
                })
                
                if contact:
                    await self.link_contact_to_lead(contact["id"], lead["id"])
                
                # Adicionar nota inicial
                await self.add_note(
                    lead["id"],
                    f"Lead criado via WhatsApp AI\n\n{lead_data.ai_notes}"
                )
                
                logger.info(f"Lead criado com sucesso: {lead['id']} - {lead_data.name}")
                return lead
            else:
                logger.error("Resposta inesperada ao criar lead")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar lead: {str(e)}")
            raise
    
    async def update_lead(self, lead_id: int, lead_data: KommoLead) -> Dict:
        """Atualiza lead existente"""
        try:
            # Preparar campos customizados
            custom_fields_values = await self._prepare_custom_fields(lead_data)
            
            # Dados de atualização
            update_payload = {
                "id": lead_id,
                "name": lead_data.name,
                "custom_fields_values": custom_fields_values
            }
            
            # Adicionar tags se houver
            if lead_data.tags:
                update_payload["_embedded"] = {
                    "tags": [{"name": tag} for tag in lead_data.tags]
                }
            
            response = await self._make_request("PATCH", f"/leads/{lead_id}", update_payload)
            
            # Adicionar nota sobre atualização
            await self.add_note(
                lead_id,
                f"Lead atualizado via WhatsApp AI\n\nScore: {lead_data.qualification_score}\n{lead_data.ai_notes}"
            )
            
            logger.info(f"Lead atualizado: {lead_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao atualizar lead: {str(e)}")
            raise
    
    async def move_lead_stage(self, lead_id: int, status: LeadStatus) -> bool:
        """Move lead para novo estágio do pipeline"""
        try:
            stage_id = await self._get_stage_id(status)
            
            if not stage_id:
                logger.error(f"Stage ID não encontrado para status: {status}")
                return False
            
            update_payload = {
                "id": lead_id,
                "status_id": stage_id
            }
            
            await self._make_request("PATCH", f"/leads/{lead_id}", update_payload)
            logger.info(f"Lead {lead_id} movido para estágio: {status.value}")
            
            # Adicionar tag baseada no estágio
            tag_map = {
                LeadStatus.QUALIFIED: "Lead Qualificado",
                LeadStatus.MEETING_SCHEDULED: "Reunião Agendada",
                LeadStatus.WON: "Cliente Fechado",
                LeadStatus.LOST: "Lead Perdido"
            }
            
            if status in tag_map:
                await self.add_tags_to_lead(lead_id, [tag_map[status]])
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao mover lead: {str(e)}")
            return False
    
    async def find_lead_by_whatsapp(self, whatsapp: str) -> Optional[Dict]:
        """Busca lead pelo número do WhatsApp"""
        try:
            # Buscar usando query
            response = await self._make_request(
                "GET",
                "/leads",
                params={"query": whatsapp}
            )
            
            leads = response.get("_embedded", {}).get("leads", [])
            
            # Filtrar pelo WhatsApp exato nos campos customizados
            whatsapp_field_id = self.config.kommo.custom_fields.get("whatsapp_number", 0)
            
            for lead in leads:
                custom_fields = lead.get("custom_fields_values", [])
                for field in custom_fields:
                    if (field.get("field_id") == whatsapp_field_id and
                        field.get("values", [{}])[0].get("value") == whatsapp):
                        return lead
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar lead por WhatsApp: {str(e)}")
            return None
    
    async def get_lead(self, lead_id: int) -> Optional[Dict]:
        """Obtém detalhes completos de um lead"""
        try:
            response = await self._make_request(
                "GET",
                f"/leads/{lead_id}",
                params={"with": "contacts"}
            )
            return response
            
        except Exception as e:
            logger.error(f"Erro ao obter lead: {str(e)}")
            return None
    
    async def create_contact(self, contact_data: Dict) -> Optional[Dict]:
        """Cria contato no Kommo"""
        try:
            contact_payload = {
                "name": contact_data["name"],
                "custom_fields_values": [
                    {
                        "field_code": "PHONE",
                        "values": [{"value": contact_data["phone"], "enum_code": "WORK"}]
                    }
                ]
            }
            
            if contact_data.get("email"):
                contact_payload["custom_fields_values"].append({
                    "field_code": "EMAIL",
                    "values": [{"value": contact_data["email"], "enum_code": "WORK"}]
                })
            
            response = await self._make_request("POST", "/contacts", [contact_payload])
            
            if "_embedded" in response and "contacts" in response["_embedded"]:
                return response["_embedded"]["contacts"][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar contato: {str(e)}")
            return None
    
    async def link_contact_to_lead(self, contact_id: int, lead_id: int) -> bool:
        """Associa contato a um lead"""
        try:
            link_payload = {
                "entity_id": lead_id,
                "entity_type": "leads"
            }
            
            await self._make_request(
                "POST",
                f"/contacts/{contact_id}/link",
                [link_payload]
            )
            
            logger.info(f"Contato {contact_id} associado ao lead {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao associar contato: {str(e)}")
            return False
    
    async def create_task(self, task_data: KommoTask) -> Optional[Dict]:
        """Cria tarefa no Kommo"""
        try:
            task_payload = {
                "text": task_data.text,
                "complete_till": int(task_data.complete_till.timestamp()),
                "task_type_id": self._get_task_type_id(task_data.task_type),
                "entity_type": task_data.entity_type,
                "entity_id": task_data.entity_id
            }
            
            if task_data.responsible_user_id:
                task_payload["responsible_user_id"] = task_data.responsible_user_id
            
            response = await self._make_request("POST", "/tasks", [task_payload])
            
            if "_embedded" in response and "tasks" in response["_embedded"]:
                return response["_embedded"]["tasks"][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar tarefa: {str(e)}")
            return None
    
    async def add_note(self, lead_id: int, text: str, note_type: NoteType = NoteType.COMMON) -> bool:
        """Adiciona nota a um lead"""
        try:
            note_payload = {
                "entity_type": "leads",
                "entity_id": lead_id,
                "note_type": note_type.value,
                "params": {
                    "text": text
                }
            }
            
            await self._make_request("POST", "/leads/notes", [note_payload])
            logger.info(f"Nota adicionada ao lead {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar nota: {str(e)}")
            return False
    
    async def add_tags_to_lead(self, lead_id: int, tags: List[str]) -> bool:
        """Adiciona tags a um lead"""
        try:
            update_payload = {
                "id": lead_id,
                "_embedded": {
                    "tags": [{"name": tag} for tag in tags]
                }
            }
            
            await self._make_request("PATCH", f"/leads/{lead_id}", update_payload)
            logger.info(f"Tags adicionadas ao lead {lead_id}: {tags}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar tags: {str(e)}")
            return False
    
    async def get_pipelines(self) -> List[Dict]:
        """Obtém lista de pipelines"""
        try:
            response = await self._make_request(
                "GET",
                "/leads/pipelines",
                params={"with": "statuses"}
            )
            
            return response.get("_embedded", {}).get("pipelines", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter pipelines: {str(e)}")
            return []
    
    async def get_pipeline_configuration(self) -> Dict:
        """Obtém a configuração completa do pipeline"""
        try:
            # Garantir que configurações foram carregadas
            pipeline_id = await self._get_pipeline_config()
            
            return {
                "pipeline_id": pipeline_id,
                "stages": self._stage_ids or {},
                "custom_fields": self._custom_fields or {},
                "info": "Usando Long-Lived Token - Sem necessidade de renovação!"
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter configuração: {str(e)}")
            return {
                "error": str(e),
                "pipeline_id": self.config.kommo.pipeline_id,
                "info": "Configure KOMMO_LONG_LIVED_TOKEN no .env"
            }
    
    async def search_available_slots(self, date: datetime) -> List[Dict]:
        """Busca horários disponíveis para agendamento"""
        # TODO: Implementar integração com calendário do Kommo
        # Por enquanto, retorna slots padrão
        
        available_slots = []
        business_hours = [
            "09:00", "10:00", "11:00", "14:00",
            "15:00", "16:00", "17:00"
        ]
        
        for hour in business_hours:
            slot_time = datetime.strptime(f"{date.date()} {hour}", "%Y-%m-%d %H:%M")
            available_slots.append({
                "datetime": slot_time,
                "available": True
            })
        
        return available_slots
    
    async def update_lead_custom_field(
        self, 
        lead_id: int, 
        field_name: str, 
        value: Any
    ) -> bool:
        """
        Atualiza um campo customizado específico do lead
        
        Args:
            lead_id: ID do lead no Kommo
            field_name: Nome do campo (ex: 'google_calendar_link')
            value: Valor a ser definido
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            # Buscar ID do campo
            field_id = self.config.kommo.custom_fields.get(field_name)
            if not field_id:
                logger.warning(f"Campo '{field_name}' não configurado")
                return False
            
            # Preparar payload
            payload = [{
                "id": lead_id,
                "custom_fields_values": [{
                    "field_id": field_id,
                    "values": [{
                        "value": str(value)
                    }]
                }]
            }]
            
            # Atualizar lead
            response = await self._make_request("PATCH", "/leads", data=payload)
            
            if response and "_embedded" in response:
                logger.info(f"Campo '{field_name}' atualizado para lead {lead_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao atualizar campo customizado: {str(e)}")
            return False
    
    async def get_lead_by_google_event_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca lead pelo ID do evento do Google Calendar
        
        Args:
            event_id: ID do evento no Google Calendar
            
        Returns:
            Lead se encontrado, None caso contrário
        """
        try:
            # Buscar campo google_calendar_link
            field_id = self.config.kommo.custom_fields.get("google_calendar_link")
            if not field_id:
                logger.warning("Campo 'google_calendar_link' não configurado")
                return None
            
            # Buscar leads com filtro
            # Nota: Kommo não suporta busca direta por campo customizado
            # Precisamos buscar todos e filtrar localmente
            params = {
                "limit": 250,
                "with": "contacts"
            }
            
            response = await self._make_request("GET", "/leads", params=params)
            
            if not response or "_embedded" not in response:
                return None
            
            leads = response["_embedded"].get("leads", [])
            
            # Filtrar pelo event_id
            for lead in leads:
                custom_fields = lead.get("custom_fields_values", [])
                for field in custom_fields:
                    if field.get("field_id") == field_id:
                        values = field.get("values", [])
                        if values and event_id in str(values[0].get("value", "")):
                            return lead
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar lead por event_id: {str(e)}")
            return None
    
    async def schedule_meeting(self, lead_id: int, meeting_datetime: datetime, notes: str = "") -> bool:
        """Agenda reunião para um lead"""
        try:
            # Criar tarefa de reunião
            task = KommoTask(
                text=f"Reunião agendada via WhatsApp - {notes}",
                task_type=TaskType.MEET,
                complete_till=meeting_datetime,
                entity_type="leads",
                entity_id=lead_id
            )
            
            task_result = await self.create_task(task)
            
            if task_result:
                # Atualizar campo de data da reunião
                meeting_field_id = self.config.kommo.custom_fields.get("meeting_datetime", 0)
                if meeting_field_id:
                    update_payload = {
                        "id": lead_id,
                        "custom_fields_values": [
                            {
                                "field_id": meeting_field_id,
                                "values": [{"value": meeting_datetime.isoformat()}]
                            }
                        ]
                    }
                    await self._make_request("PATCH", f"/leads/{lead_id}", update_payload)
                
                # Mover para estágio de reunião agendada
                await self.move_lead_stage(lead_id, LeadStatus.MEETING_SCHEDULED)
                
                logger.info(f"Reunião agendada para lead {lead_id} em {meeting_datetime}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao agendar reunião: {str(e)}")
            return False
    
    # Métodos auxiliares privados
    
    async def _prepare_custom_fields(self, lead_data: KommoLead) -> List[Dict]:
        """Prepara campos customizados para envio"""
        custom_fields_values = []
        
        # Garantir que os campos foram carregados
        if self._custom_fields is None:
            await self._get_pipeline_config()  # Isso carregará campos também
            if self._custom_fields is None:
                self._custom_fields = self.config.kommo.custom_fields
        
        field_config = self._custom_fields
        
        # Mapear campos do modelo para IDs do Kommo
        field_mapping = {
            "whatsapp": ("whatsapp_number", lambda x: x),
            "energy_bill_value": ("energy_bill_value", lambda x: str(x)),
            "solution_type": ("solution_type", self._get_solution_type_value),
            "current_discount": ("current_discount", lambda x: x),
            "competitor": ("competitor", lambda x: x),
            "qualification_score": ("qualification_score", lambda x: str(x)),
            "ai_notes": ("ai_notes", lambda x: x)
        }
        
        # Adicionar origem do lead
        lead_source_id = field_config.get("lead_source", 0)
        if lead_source_id:
            custom_fields_values.append({
                "field_id": lead_source_id,
                "values": [{"value": "WhatsApp"}]
            })
        
        # Processar campos mapeados
        for attr_name, (field_key, transform) in field_mapping.items():
            value = getattr(lead_data, attr_name, None)
            if value is not None:
                field_id = field_config.get(field_key, 0)
                if field_id:
                    transformed_value = transform(value)
                    if transformed_value is not None:
                        custom_fields_values.append({
                            "field_id": field_id,
                            "values": [{"value": transformed_value}]
                        })
        
        return custom_fields_values
    
    def _determine_responsible_user(self, lead_data: KommoLead) -> int:
        """Determina usuário responsável baseado nas regras"""
        if lead_data.responsible_user_id:
            return lead_data.responsible_user_id
        
        users = self.config.kommo.responsible_users
        
        # Regras de atribuição
        if lead_data.energy_bill_value > 4000:
            return users.get("high_value", users.get("default", 0))
        elif lead_data.solution_type == SolutionType.INVESTMENT:
            return users.get("investment", users.get("default", 0))
        else:
            return users.get("default", 0)
    
    def _get_solution_type_value(self, solution_type: Optional[SolutionType]) -> Optional[str]:
        """Obtém valor do campo select de tipo de solução"""
        if not solution_type:
            return None
        
        value_id = self.config.kommo.solution_type_values.get(solution_type.value, 0)
        return str(value_id) if value_id else None
    
    def _get_task_type_id(self, task_type: TaskType) -> int:
        """Obtém ID do tipo de tarefa"""
        type_map = {
            TaskType.CALL: 1,
            TaskType.MEET: 2,
            TaskType.EMAIL: 3
        }
        return type_map.get(task_type, 1)


# Criar instância global usando configuração
try:
    kommo_service = KommoService()
except Exception as e:
    logger.warning(f"Não foi possível inicializar KommoService: {e}")
    kommo_service = None