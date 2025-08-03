"""
CRMAgent - Agente Especializado em Integração com Kommo CRM
Responsável por sincronização de leads, deals e contatos com o CRM
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from agno import Agent
from agno.tools import tool
from loguru import logger
import aiohttp

from app.integrations.supabase_client import supabase_client
from app.config import settings


class DealStage(Enum):
    """Estágios do pipeline no Kommo"""
    NOVO_LEAD = "novo_lead"                         # Novo lead
    EM_NEGOCIACAO = "em_negociacao"                 # Em negociação
    EM_QUALIFICACAO = "em_qualificacao"             # Em qualificação
    QUALIFICADO = "qualificado"                     # Qualificado
    REUNIAO_AGENDADA = "reuniao_agendada"           # Reunião agendada
    REUNIAO_FINALIZADA = "reuniao_finalizada"       # Reunião finalizada
    NAO_INTERESSADO = "nao_interessado"             # Não interessado


class CRMAgent:
    """
    Agente especializado em integração com Kommo CRM
    Gerencia sincronização de dados e automações do CRM
    """
    
    def __init__(self, model, storage):
        """
        Inicializa o agente CRM
        
        Args:
            model: Modelo LLM a ser usado
            storage: Storage para persistência
        """
        self.model = model
        self.storage = storage
        
        # Configuração do Kommo
        self.kommo_config = {
            "base_url": settings.kommo_base_url,
            "subdomain": settings.kommo_subdomain,
            "pipeline_id": settings.kommo_pipeline_id,
            "headers": {
                "Authorization": f"Bearer {settings.kommo_long_lived_token}",
                "Content-Type": "application/json"
            }
        }
        
        # Campos personalizados do Kommo (serão buscados automaticamente)
        self.custom_fields = {
            "whatsapp": None,
            "valor_conta_energia": None,
            "score_qualificacao": None,
            "solucao_solar": None,
            "fonte": None,
            "id_conversa": None,
            "link_evento_google": None,
            "status_reuniao": None
        }
        
        # Tags disponíveis no Kommo
        self.available_tags = [
            "agendamento-pendente",
            "follow-up-automatico",
            "lead-frio",
            "lead-morno",
            "lead-quente",
            "numero-invalido",
            "qualificado-ia",
            "sem-resposta",
            "whatsapp-lead"
        ]
        
        # IDs dos estágios do pipeline (serão buscados automaticamente)
        self.pipeline_stages = {}
        
        # Cache de IDs do Kommo
        self.id_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Tools do agente
        self.tools = [
            self.create_or_update_lead,
            self.create_contact,
            self.create_deal,
            self.update_deal_stage,
            self.add_note,
            self.add_task,
            self.search_entity,
            self.sync_lead_to_crm,
            self.get_deal_history
        ]
        
        # Criar o agente
        self.agent = Agent(
            name="CRM Manager",
            model=self.model,
            role="""Você é um especialista em gestão de CRM (Kommo).
            
            Suas responsabilidades:
            1. Sincronizar leads entre o sistema e o Kommo CRM
            2. Criar e atualizar deals no pipeline de vendas
            3. Gerenciar contatos e empresas
            4. Adicionar notas e tarefas relevantes
            5. Manter histórico completo de interações
            
            Regras de sincronização:
            - Todo lead qualificado deve ter um deal no CRM
            - Atualizar stage do deal conforme progresso
            - Adicionar notas importantes das conversas
            - Criar tarefas para follow-ups agendados
            - Manter dados sempre atualizados
            
            Pipeline de vendas:
            1. Novo Lead → Qualificação inicial
            2. Qualificação → Lead qualificado
            3. Proposta → Proposta enviada
            4. Negociação → Em discussão
            5. Fechamento → Ganho ou Perdido""",
            
            tools=self.tools,
            instructions=[
                "Mantenha dados sincronizados entre sistemas",
                "Crie deals apenas para leads qualificados",
                "Adicione contexto relevante nas notas",
                "Atualize stages conforme progresso real",
                "Configure tarefas para garantir follow-up",
                "Use tags para categorização"
            ]
        )
        
        # Inicializar campos e stages automaticamente
        self._initialized = False
        
        logger.info("✅ CRMAgent inicializado")
    
    async def initialize(self):
        """Inicializa campos personalizados e stages do pipeline automaticamente"""
        if self._initialized:
            return
        
        try:
            # Buscar campos personalizados
            await self._fetch_custom_fields()
            
            # Buscar stages do pipeline
            await self._fetch_pipeline_stages()
            
            self._initialized = True
            logger.info("✅ Campos e stages do Kommo carregados automaticamente")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Kommo: {e}")
    
    async def _fetch_custom_fields(self):
        """Busca IDs dos campos personalizados automaticamente"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/leads/custom_fields"
                
                async with session.get(
                    url,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        fields = data.get("_embedded", {}).get("custom_fields", [])
                        
                        # Mapear campos por nome
                        field_mapping = {
                            "WhatsApp": "whatsapp",
                            "Valor Conta Energia": "valor_conta_energia",
                            "Score Qualificação": "score_qualificacao",
                            "Solução Solar": "solucao_solar",
                            "Fonte": "fonte",
                            "ID Conversa": "id_conversa",
                            "Link do evento no Google Calendar": "link_evento_google",
                            "Status atual da reunião": "status_reuniao"
                        }
                        
                        for field in fields:
                            field_name = field.get("name")
                            if field_name in field_mapping:
                                key = field_mapping[field_name]
                                self.custom_fields[key] = field.get("id")
                                logger.info(f"Campo '{field_name}' mapeado: ID {field.get('id')}")
                        
        except Exception as e:
            logger.error(f"Erro ao buscar campos personalizados: {e}")
    
    async def _fetch_pipeline_stages(self):
        """Busca IDs dos stages do pipeline automaticamente"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/leads/pipelines/{self.kommo_config['pipeline_id']}"
                
                async with session.get(
                    url,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        statuses = data.get("_embedded", {}).get("statuses", [])
                        
                        # Mapear stages por nome
                        stage_mapping = {
                            "Novo Lead": "novo_lead",
                            "Em Negociação": "em_negociacao",
                            "Em Qualificação": "em_qualificacao",
                            "Qualificado": "qualificado",
                            "Reunião Agendada": "reuniao_agendada",
                            "Reunião Finalizada": "reuniao_finalizada",
                            "Não Interessado": "nao_interessado"
                        }
                        
                        for status in statuses:
                            status_name = status.get("name")
                            if status_name in stage_mapping:
                                key = stage_mapping[status_name]
                                self.pipeline_stages[key] = status.get("id")
                                logger.info(f"Stage '{status_name}' mapeado: ID {status.get('id')}")
                        
        except Exception as e:
            logger.error(f"Erro ao buscar stages do pipeline: {e}")
    
    async def ensure_initialized(self):
        """Garante que o agente está inicializado antes de executar operações"""
        if not self._initialized:
            await self.initialize()
    
    @tool
    async def create_or_update_lead(
        self,
        lead_data: Dict[str, Any],
        update_if_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Cria ou atualiza lead no Kommo
        
        Args:
            lead_data: Dados do lead
            update_if_exists: Se deve atualizar caso já exista
            
        Returns:
            Detalhes do lead no CRM
        """
        try:
            # Verificar se lead já existe
            existing = await self.search_entity(
                entity_type="leads",
                query=lead_data.get("phone", lead_data.get("email"))
            )
            
            if existing and existing.get("leads"):
                if update_if_exists:
                    # Atualizar lead existente
                    lead_id = existing["leads"][0]["id"]
                    return await self._update_lead(lead_id, lead_data)
                else:
                    return {
                        "success": False,
                        "error": "Lead já existe",
                        "existing_id": existing["leads"][0]["id"]
                    }
            
            # Criar novo lead
            kommo_data = {
                "name": lead_data.get("name", "Sem nome"),
                "pipeline_id": int(self.kommo_config["pipeline_id"]),
                "custom_fields_values": self._prepare_custom_fields(lead_data),
                "tags": self._generate_tags(lead_data),
                "_embedded": {
                    "tags": self._generate_tags(lead_data)
                }
            }
            
            # Adicionar responsável se configurado
            if hasattr(settings, "kommo_responsible_user_id"):
                kommo_data["responsible_user_id"] = settings.kommo_responsible_user_id
            
            # Fazer requisição
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/leads"
                
                async with session.post(
                    url,
                    json=[kommo_data],  # API espera array
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        lead_id = result["_embedded"]["leads"][0]["id"]
                        
                        # Salvar ID no cache e banco
                        await self._save_crm_mapping(
                            lead_data.get("id"),
                            lead_id,
                            "lead"
                        )
                        
                        logger.info(f"✅ Lead criado no Kommo: {lead_id}")
                        
                        return {
                            "success": True,
                            "crm_id": lead_id,
                            "message": "Lead criado no CRM"
                        }
                    else:
                        error = await response.text()
                        logger.error(f"Erro ao criar lead: {error}")
                        return {
                            "success": False,
                            "error": f"Erro {response.status}: {error}"
                        }
                        
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar lead: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def create_contact(
        self,
        contact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria contato no Kommo
        
        Args:
            contact_data: Dados do contato
            
        Returns:
            Detalhes do contato criado
        """
        try:
            kommo_data = {
                "name": contact_data.get("name", "Sem nome"),
                "custom_fields_values": [
                    {
                        "field_code": "PHONE",
                        "values": [{"value": contact_data.get("phone")}]
                    },
                    {
                        "field_code": "EMAIL",
                        "values": [{"value": contact_data.get("email")}]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/contacts"
                
                async with session.post(
                    url,
                    json=[kommo_data],
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        contact_id = result["_embedded"]["contacts"][0]["id"]
                        
                        logger.info(f"✅ Contato criado: {contact_id}")
                        
                        return {
                            "success": True,
                            "contact_id": contact_id
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": error
                        }
                        
        except Exception as e:
            logger.error(f"Erro ao criar contato: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def create_deal(
        self,
        lead_id: str,
        deal_name: str,
        deal_value: float,
        stage: str = "new_lead"
    ) -> Dict[str, Any]:
        """
        Cria deal (negócio) no pipeline
        
        Args:
            lead_id: ID do lead local
            deal_name: Nome do deal
            deal_value: Valor do negócio
            stage: Estágio inicial
            
        Returns:
            Detalhes do deal criado
        """
        try:
            # Buscar ID do lead no Kommo
            crm_lead_id = await self._get_crm_id(lead_id, "lead")
            if not crm_lead_id:
                # Se não existe, criar primeiro
                lead_data = await supabase_client.get_lead(lead_id)
                if lead_data:
                    result = await self.create_or_update_lead(lead_data)
                    if result.get("success"):
                        crm_lead_id = result["crm_id"]
                    else:
                        return result
            
            # Mapear stage
            stage_id = self._get_stage_id(stage)
            
            kommo_data = {
                "name": deal_name,
                "price": int(deal_value),
                "pipeline_id": int(self.kommo_config["pipeline_id"]),
                "status_id": stage_id,
                "leads_id": [crm_lead_id] if crm_lead_id else []
            }
            
            async with aiohttp.ClientSession() as session:
                # Kommo usa "leads" endpoint mesmo para deals
                url = f"{self.kommo_config['base_url']}/api/v4/leads"
                
                async with session.post(
                    url,
                    json=[kommo_data],
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        deal_id = result["_embedded"]["leads"][0]["id"]
                        
                        logger.info(f"💰 Deal criado: {deal_name} - R$ {deal_value}")
                        
                        return {
                            "success": True,
                            "deal_id": deal_id,
                            "value": deal_value,
                            "stage": stage
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": error
                        }
                        
        except Exception as e:
            logger.error(f"Erro ao criar deal: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def update_deal_stage(
        self,
        deal_id: str,
        new_stage: str,
        add_note: bool = True
    ) -> Dict[str, Any]:
        """
        Atualiza estágio do deal no pipeline
        
        Args:
            deal_id: ID do deal
            new_stage: Novo estágio
            add_note: Se deve adicionar nota sobre mudança
            
        Returns:
            Status da atualização
        """
        try:
            stage_id = self._get_stage_id(new_stage)
            
            kommo_data = {
                "status_id": stage_id
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/leads/{deal_id}"
                
                async with session.patch(
                    url,
                    json=kommo_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        # Adicionar nota se solicitado
                        if add_note:
                            await self.add_note(
                                entity_type="leads",
                                entity_id=deal_id,
                                text=f"Deal movido para estágio: {new_stage}"
                            )
                        
                        logger.info(f"📊 Deal {deal_id} movido para {new_stage}")
                        
                        return {
                            "success": True,
                            "deal_id": deal_id,
                            "new_stage": new_stage
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": error
                        }
                        
        except Exception as e:
            logger.error(f"Erro ao atualizar stage: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def add_note(
        self,
        entity_type: str,  # leads/contacts/companies
        entity_id: str,
        text: str,
        note_type: str = "common"
    ) -> Dict[str, Any]:
        """
        Adiciona nota a uma entidade
        
        Args:
            entity_type: Tipo da entidade
            entity_id: ID da entidade
            text: Texto da nota
            note_type: Tipo da nota
            
        Returns:
            Status da operação
        """
        try:
            kommo_data = {
                "entity_id": int(entity_id),
                "note_type": note_type,
                "params": {
                    "text": text
                }
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/{entity_type}/notes"
                
                async with session.post(
                    url,
                    json=[kommo_data],
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        logger.info(f"📝 Nota adicionada à entidade {entity_id}")
                        
                        return {
                            "success": True,
                            "entity_id": entity_id,
                            "note_added": True
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": error
                        }
                        
        except Exception as e:
            logger.error(f"Erro ao adicionar nota: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def add_task(
        self,
        entity_type: str,
        entity_id: str,
        text: str,
        complete_till: datetime,
        task_type: int = 1  # 1 = Call
    ) -> Dict[str, Any]:
        """
        Adiciona tarefa a uma entidade
        
        Args:
            entity_type: Tipo da entidade
            entity_id: ID da entidade
            text: Descrição da tarefa
            complete_till: Prazo da tarefa
            task_type: Tipo da tarefa
            
        Returns:
            Detalhes da tarefa criada
        """
        try:
            kommo_data = {
                "text": text,
                "complete_till": int(complete_till.timestamp()),
                "entity_id": int(entity_id),
                "entity_type": entity_type,
                "task_type_id": task_type
            }
            
            # Adicionar responsável se configurado
            if hasattr(settings, "kommo_responsible_user_id"):
                kommo_data["responsible_user_id"] = settings.kommo_responsible_user_id
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/tasks"
                
                async with session.post(
                    url,
                    json=[kommo_data],
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        task_id = result["_embedded"]["tasks"][0]["id"]
                        
                        logger.info(f"📋 Tarefa criada: {text}")
                        
                        return {
                            "success": True,
                            "task_id": task_id,
                            "due_date": complete_till.isoformat()
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": error
                        }
                        
        except Exception as e:
            logger.error(f"Erro ao adicionar tarefa: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def search_entity(
        self,
        entity_type: str,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Busca entidades no CRM
        
        Args:
            entity_type: Tipo (leads/contacts/companies)
            query: Termo de busca
            limit: Limite de resultados
            
        Returns:
            Entidades encontradas
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/{entity_type}"
                params = {
                    "query": query,
                    "limit": limit
                }
                
                async with session.get(
                    url,
                    params=params,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        entities = result.get("_embedded", {}).get(entity_type, [])
                        
                        return {
                            "success": True,
                            entity_type: entities,
                            "count": len(entities)
                        }
                    elif response.status == 204:
                        # Nenhum resultado encontrado
                        return {
                            "success": True,
                            entity_type: [],
                            "count": 0
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": error
                        }
                        
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def sync_lead_to_crm(
        self,
        lead_id: str,
        create_deal: bool = False
    ) -> Dict[str, Any]:
        """
        Sincroniza lead completo para o CRM
        
        Args:
            lead_id: ID do lead local
            create_deal: Se deve criar deal também
            
        Returns:
            Status da sincronização
        """
        try:
            # Buscar dados do lead
            lead = await supabase_client.get_lead(lead_id)
            if not lead:
                return {
                    "success": False,
                    "error": "Lead não encontrado"
                }
            
            # Criar/atualizar lead no CRM
            lead_result = await self.create_or_update_lead(lead)
            
            if not lead_result.get("success"):
                return lead_result
            
            crm_lead_id = lead_result["crm_id"]
            
            # Adicionar nota com contexto
            qualification = await supabase_client.client.table("leads_qualifications")\
                .select("*")\
                .eq("lead_id", lead_id)\
                .single()\
                .execute()
            
            if qualification.data:
                note_text = f"""
                Lead sincronizado do SDR IA
                
                Score: {qualification.data.get('score', 0)}
                Classificação: {qualification.data.get('classification', 'N/A')}
                Estágio: {qualification.data.get('stage', 'N/A')}
                Conta de luz: R$ {lead.get('bill_value', 0):.2f}
                """
                
                await self.add_note(
                    entity_type="leads",
                    entity_id=crm_lead_id,
                    text=note_text
                )
            
            # Criar deal se qualificado
            if create_deal and lead.get("is_qualified"):
                deal_result = await self.create_deal(
                    lead_id=lead_id,
                    deal_name=f"Solar - {lead.get('name', 'Cliente')}",
                    deal_value=lead.get('bill_value', 0) * 12 * 0.2,  # Economia anual
                    stage="qualification"
                )
                
                if deal_result.get("success"):
                    logger.info(f"✅ Lead {lead_id} sincronizado com deal")
                    
                    return {
                        "success": True,
                        "crm_lead_id": crm_lead_id,
                        "crm_deal_id": deal_result["deal_id"],
                        "message": "Lead e deal sincronizados"
                    }
            
            return {
                "success": True,
                "crm_lead_id": crm_lead_id,
                "message": "Lead sincronizado"
            }
            
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def get_deal_history(
        self,
        deal_id: str
    ) -> Dict[str, Any]:
        """
        Obtém histórico completo do deal
        
        Args:
            deal_id: ID do deal
            
        Returns:
            Histórico do deal
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Buscar deal
                url = f"{self.kommo_config['base_url']}/api/v4/leads/{deal_id}"
                params = {"with": "contacts"}
                
                async with session.get(
                    url,
                    params=params,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status != 200:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": error
                        }
                    
                    deal = await response.json()
                
                # Buscar notas
                url = f"{self.kommo_config['base_url']}/api/v4/leads/notes"
                params = {"filter[entity_id]": deal_id}
                
                async with session.get(
                    url,
                    params=params,
                    headers=self.kommo_config["headers"]
                ) as response:
                    notes = []
                    if response.status == 200:
                        result = await response.json()
                        notes = result.get("_embedded", {}).get("notes", [])
                
                # Buscar tarefas
                url = f"{self.kommo_config['base_url']}/api/v4/tasks"
                params = {
                    "filter[entity_type]": "leads",
                    "filter[entity_id]": deal_id
                }
                
                async with session.get(
                    url,
                    params=params,
                    headers=self.kommo_config["headers"]
                ) as response:
                    tasks = []
                    if response.status == 200:
                        result = await response.json()
                        tasks = result.get("_embedded", {}).get("tasks", [])
                
                return {
                    "success": True,
                    "deal": {
                        "id": deal.get("id"),
                        "name": deal.get("name"),
                        "price": deal.get("price"),
                        "status": deal.get("status_id"),
                        "created_at": deal.get("created_at"),
                        "updated_at": deal.get("updated_at")
                    },
                    "notes": notes,
                    "tasks": tasks,
                    "total_notes": len(notes),
                    "total_tasks": len(tasks)
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Métodos auxiliares privados
    
    def _prepare_custom_fields(self, lead_data: Dict[str, Any]) -> List[Dict]:
        """Prepara campos customizados para o Kommo"""
        custom_fields = []
        
        # Mapear campos específicos
        # Você precisa configurar os IDs dos campos customizados no Kommo
        field_mappings = {
            "bill_value": 123456,  # Substituir pelo ID real
            "qualification_score": 123457,  # Substituir pelo ID real
            "classification": 123458,  # Substituir pelo ID real
        }
        
        for field, field_id in field_mappings.items():
            if field in lead_data:
                custom_fields.append({
                    "field_id": field_id,
                    "values": [{"value": str(lead_data[field])}]
                })
        
        return custom_fields
    
    def _generate_tags(self, lead_data: Dict[str, Any]) -> List[str]:
        """Gera tags baseadas nos dados do lead"""
        tags = ["SDR IA"]
        
        # Classificação
        classification = lead_data.get("classification", "").lower()
        if classification:
            tags.append(f"lead_{classification}")
        
        # Qualificação
        if lead_data.get("is_qualified"):
            tags.append("qualificado")
        
        # Valor da conta
        bill_value = lead_data.get("bill_value", 0)
        if bill_value > 6000:
            tags.append("high_value")
        elif bill_value > 4000:
            tags.append("medium_value")
        
        return tags
    
    def _get_stage_id(self, stage: str) -> int:
        """Mapeia nome do stage para ID no Kommo"""
        # Você precisa configurar os IDs reais do seu pipeline
        stage_mapping = {
            "novo_lead": 12345678,              # Substituir pelo ID real
            "em_negociacao": 12345679,          # Substituir pelo ID real  
            "em_qualificacao": 12345680,        # Substituir pelo ID real
            "qualificado": 12345681,            # Substituir pelo ID real
            "reuniao_agendada": 12345682,       # Substituir pelo ID real
            "reuniao_finalizada": 12345683,     # Substituir pelo ID real
            "nao_interessado": 143              # ID padrão do Kommo para LOST
        }
        
        return stage_mapping.get(stage, 12345678)
    
    async def _get_crm_id(self, local_id: str, entity_type: str) -> Optional[str]:
        """Busca ID do CRM para entidade local"""
        # Verificar cache
        cache_key = f"{entity_type}_{local_id}"
        if cache_key in self.id_cache:
            return self.id_cache[cache_key]
        
        # Buscar no banco
        try:
            result = await supabase_client.client.table("crm_mappings")\
                .select("crm_id")\
                .eq("local_id", local_id)\
                .eq("entity_type", entity_type)\
                .single()\
                .execute()
            
            if result.data:
                crm_id = result.data["crm_id"]
                self.id_cache[cache_key] = crm_id
                return crm_id
                
        except Exception as e:
            logger.error(f"Erro ao buscar CRM ID: {e}")
        
        return None
    
    async def _save_crm_mapping(
        self,
        local_id: str,
        crm_id: str,
        entity_type: str
    ):
        """Salva mapeamento entre IDs local e CRM"""
        try:
            await supabase_client.client.table("crm_mappings").upsert({
                "local_id": local_id,
                "crm_id": crm_id,
                "entity_type": entity_type,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            # Atualizar cache
            cache_key = f"{entity_type}_{local_id}"
            self.id_cache[cache_key] = crm_id
            
        except Exception as e:
            logger.error(f"Erro ao salvar mapping: {e}")
    
    async def _update_lead(
        self,
        lead_id: str,
        lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza lead existente no Kommo"""
        try:
            kommo_data = {
                "name": lead_data.get("name"),
                "custom_fields_values": self._prepare_custom_fields(lead_data)
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kommo_config['base_url']}/api/v4/leads/{lead_id}"
                
                async with session.patch(
                    url,
                    json=kommo_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Lead {lead_id} atualizado no Kommo")
                        
                        return {
                            "success": True,
                            "crm_id": lead_id,
                            "message": "Lead atualizado no CRM"
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": error
                        }
                        
        except Exception as e:
            logger.error(f"Erro ao atualizar lead: {e}")
            return {
                "success": False,
                "error": str(e)
            }