"""
CRM Enhanced - Extensão completa do CRMAgent para controle total do Kommo
Adiciona funcionalidades avançadas de manipulação de cards, tags, campos e pipelines
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import aiohttp
from loguru import logger

from app.teams.agents.crm import CRMAgent


class KommoEnhancedCRM(CRMAgent):
    """
    Extensão do CRMAgent com funcionalidades completas para manipulação total do Kommo
    """
    
    def __init__(self, model, storage):
        """Inicializa o CRM Enhanced com todas as funcionalidades"""
        super().__init__(model, storage)
        
        # Adicionar novos endpoints
        self.endpoints = {
            "leads": f"{self.kommo_config['base_url']}/api/v4/leads",
            "contacts": f"{self.kommo_config['base_url']}/api/v4/contacts",
            "companies": f"{self.kommo_config['base_url']}/api/v4/companies",
            "pipelines": f"{self.kommo_config['base_url']}/api/v4/leads/pipelines",
            "tags": f"{self.kommo_config['base_url']}/api/v4/tags",
            "custom_fields": f"{self.kommo_config['base_url']}/api/v4/leads/custom_fields",
            "users": f"{self.kommo_config['base_url']}/api/v4/users",
            "webhooks": f"{self.kommo_config['base_url']}/api/v4/webhooks",
            "catalog": f"{self.kommo_config['base_url']}/api/v4/catalogs",
            "events": f"{self.kommo_config['base_url']}/api/v4/events"
        }
        
        # Cache expandido
        self.tags_cache = {}
        self.users_cache = {}
        self.pipelines_cache = {}
        
        logger.info("✅ KommoEnhancedCRM inicializado com funcionalidades completas")
    
    # ==================== MANIPULAÇÃO DE TAGS ====================
    
    async def add_tags_to_lead(
        self,
        lead_id: Union[str, int],
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        Adiciona múltiplas tags a um lead
        
        Args:
            lead_id: ID do lead no Kommo
            tags: Lista de tags para adicionar
            
        Returns:
            Resultado da operação
        """
        try:
            # Buscar lead atual
            async with aiohttp.ClientSession() as session:
                url = f"{self.endpoints['leads']}/{lead_id}"
                
                # Primeiro buscar o lead
                async with session.get(url, headers=self.kommo_config["headers"]) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"Lead {lead_id} não encontrado"}
                    
                    lead_data = await response.json()
                
                # Preparar tags
                existing_tags = lead_data.get("_embedded", {}).get("tags", [])
                existing_tag_names = [tag.get("name") for tag in existing_tags]
                
                # Adicionar novas tags
                new_tags = [tag for tag in tags if tag not in existing_tag_names]
                all_tags = existing_tag_names + new_tags
                
                # Atualizar lead com tags
                update_data = {
                    "_embedded": {
                        "tags": [{"name": tag} for tag in all_tags]
                    }
                }
                
                async with session.patch(
                    url,
                    json=update_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Tags adicionadas ao lead {lead_id}: {new_tags}")
                        return {
                            "success": True,
                            "lead_id": lead_id,
                            "tags_added": new_tags,
                            "all_tags": all_tags
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao adicionar tags: {e}")
            return {"success": False, "error": str(e)}
    
    async def remove_tags_from_lead(
        self,
        lead_id: Union[str, int],
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        Remove tags de um lead
        
        Args:
            lead_id: ID do lead no Kommo
            tags: Lista de tags para remover
            
        Returns:
            Resultado da operação
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.endpoints['leads']}/{lead_id}"
                
                # Buscar lead atual
                async with session.get(url, headers=self.kommo_config["headers"]) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"Lead {lead_id} não encontrado"}
                    
                    lead_data = await response.json()
                
                # Filtrar tags
                existing_tags = lead_data.get("_embedded", {}).get("tags", [])
                remaining_tags = [
                    tag for tag in existing_tags
                    if tag.get("name") not in tags
                ]
                
                # Atualizar lead
                update_data = {
                    "_embedded": {
                        "tags": remaining_tags
                    }
                }
                
                async with session.patch(
                    url,
                    json=update_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Tags removidas do lead {lead_id}: {tags}")
                        return {
                            "success": True,
                            "lead_id": lead_id,
                            "tags_removed": tags,
                            "remaining_tags": [tag.get("name") for tag in remaining_tags]
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao remover tags: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== MANIPULAÇÃO DE CAMPOS CUSTOMIZADOS ====================
    
    async def update_custom_fields(
        self,
        lead_id: Union[str, int],
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza campos customizados de um lead
        
        Args:
            lead_id: ID do lead no Kommo
            fields: Dicionário com campos e valores
            
        Returns:
            Resultado da operação
        """
        try:
            # Garantir que campos estão inicializados
            await self.ensure_initialized()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.endpoints['leads']}/{lead_id}"
                
                # Preparar campos customizados
                custom_fields_values = []
                
                for field_name, value in fields.items():
                    field_id = self.custom_fields.get(field_name)
                    if field_id:
                        custom_fields_values.append({
                            "field_id": field_id,
                            "values": [{"value": value}]
                        })
                
                # Atualizar lead
                update_data = {
                    "custom_fields_values": custom_fields_values
                }
                
                async with session.patch(
                    url,
                    json=update_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Campos customizados atualizados no lead {lead_id}")
                        return {
                            "success": True,
                            "lead_id": lead_id,
                            "fields_updated": list(fields.keys())
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao atualizar campos customizados: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== MOVIMENTAÇÃO AVANÇADA DE CARDS ====================
    
    async def move_card_to_pipeline(
        self,
        lead_id: Union[str, int],
        pipeline_id: int,
        stage_id: int,
        responsible_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Move um card para um pipeline e estágio específico
        
        Args:
            lead_id: ID do lead no Kommo
            pipeline_id: ID do pipeline de destino
            stage_id: ID do estágio de destino
            responsible_user_id: ID do usuário responsável (opcional)
            
        Returns:
            Resultado da operação
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.endpoints['leads']}/{lead_id}"
                
                # Preparar dados de atualização
                update_data = {
                    "pipeline_id": pipeline_id,
                    "status_id": stage_id
                }
                
                if responsible_user_id:
                    update_data["responsible_user_id"] = responsible_user_id
                
                async with session.patch(
                    url,
                    json=update_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Card {lead_id} movido para pipeline {pipeline_id}, estágio {stage_id}")
                        return {
                            "success": True,
                            "lead_id": lead_id,
                            "pipeline_id": pipeline_id,
                            "stage_id": stage_id
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao mover card: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== BUSCA AVANÇADA ====================
    
    async def search_leads_by_filter(
        self,
        filters: Dict[str, Any],
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Busca leads com filtros avançados
        
        Args:
            filters: Filtros de busca (tags, stages, responsible_user, etc)
            limit: Limite de resultados
            
        Returns:
            Lista de leads encontrados
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Construir query parameters
                params = {"limit": limit}
                
                if "tags" in filters:
                    params["filter[tags][]"] = filters["tags"]
                
                if "stage_id" in filters:
                    params["filter[statuses][]"] = filters["stage_id"]
                
                if "responsible_user_id" in filters:
                    params["filter[responsible_user_id]"] = filters["responsible_user_id"]
                
                if "created_at" in filters:
                    params["filter[created_at][from]"] = filters["created_at"].get("from")
                    params["filter[created_at][to]"] = filters["created_at"].get("to")
                
                if "updated_at" in filters:
                    params["filter[updated_at][from]"] = filters["updated_at"].get("from")
                    params["filter[updated_at][to]"] = filters["updated_at"].get("to")
                
                async with session.get(
                    self.endpoints["leads"],
                    params=params,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        leads = data.get("_embedded", {}).get("leads", [])
                        
                        logger.info(f"✅ Encontrados {len(leads)} leads com os filtros aplicados")
                        return {
                            "success": True,
                            "total": len(leads),
                            "leads": leads
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro na busca avançada: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== GESTÃO DE RESPONSÁVEIS ====================
    
    async def assign_responsible_user(
        self,
        lead_id: Union[str, int],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Atribui um usuário responsável ao lead
        
        Args:
            lead_id: ID do lead no Kommo
            user_id: ID do usuário responsável
            
        Returns:
            Resultado da operação
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.endpoints['leads']}/{lead_id}"
                
                update_data = {
                    "responsible_user_id": user_id
                }
                
                async with session.patch(
                    url,
                    json=update_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Usuário {user_id} atribuído ao lead {lead_id}")
                        return {
                            "success": True,
                            "lead_id": lead_id,
                            "responsible_user_id": user_id
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao atribuir responsável: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== GESTÃO DE EMPRESAS ====================
    
    async def link_lead_to_company(
        self,
        lead_id: Union[str, int],
        company_id: Union[str, int]
    ) -> Dict[str, Any]:
        """
        Vincula um lead a uma empresa
        
        Args:
            lead_id: ID do lead no Kommo
            company_id: ID da empresa no Kommo
            
        Returns:
            Resultado da operação
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.endpoints['leads']}/{lead_id}"
                
                update_data = {
                    "company_id": company_id
                }
                
                async with session.patch(
                    url,
                    json=update_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Lead {lead_id} vinculado à empresa {company_id}")
                        return {
                            "success": True,
                            "lead_id": lead_id,
                            "company_id": company_id
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao vincular empresa: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== AUTOMAÇÕES E WEBHOOKS ====================
    
    async def create_webhook(
        self,
        url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """
        Cria um webhook para eventos específicos
        
        Args:
            url: URL do webhook
            events: Lista de eventos para monitorar
            
        Returns:
            Resultado da operação
        """
        try:
            async with aiohttp.ClientSession() as session:
                webhook_data = {
                    "destination": url,
                    "settings": events
                }
                
                async with session.post(
                    self.endpoints["webhooks"],
                    json=webhook_data,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        logger.info(f"✅ Webhook criado: {url}")
                        return {
                            "success": True,
                            "webhook_id": data.get("id"),
                            "url": url,
                            "events": events
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao criar webhook: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== ANÁLISE E RELATÓRIOS ====================
    
    async def get_pipeline_statistics(
        self,
        pipeline_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtém estatísticas do pipeline
        
        Args:
            pipeline_id: ID do pipeline (opcional, usa padrão se não informado)
            
        Returns:
            Estatísticas do pipeline
        """
        try:
            pipeline_id = pipeline_id or self.kommo_config["pipeline_id"]
            
            async with aiohttp.ClientSession() as session:
                # Buscar todos os leads do pipeline
                params = {
                    "filter[pipeline_id]": pipeline_id,
                    "limit": 250
                }
                
                async with session.get(
                    self.endpoints["leads"],
                    params=params,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        leads = data.get("_embedded", {}).get("leads", [])
                        
                        # Calcular estatísticas
                        stats = {
                            "total_leads": len(leads),
                            "by_stage": {},
                            "total_value": 0,
                            "average_value": 0,
                            "by_responsible": {},
                            "by_tag": {}
                        }
                        
                        for lead in leads:
                            # Por estágio
                            stage_id = lead.get("status_id")
                            if stage_id not in stats["by_stage"]:
                                stats["by_stage"][stage_id] = 0
                            stats["by_stage"][stage_id] += 1
                            
                            # Valor total
                            price = lead.get("price", 0)
                            stats["total_value"] += price
                            
                            # Por responsável
                            responsible = lead.get("responsible_user_id")
                            if responsible:
                                if responsible not in stats["by_responsible"]:
                                    stats["by_responsible"][responsible] = 0
                                stats["by_responsible"][responsible] += 1
                            
                            # Por tag
                            tags = lead.get("_embedded", {}).get("tags", [])
                            for tag in tags:
                                tag_name = tag.get("name")
                                if tag_name not in stats["by_tag"]:
                                    stats["by_tag"][tag_name] = 0
                                stats["by_tag"][tag_name] += 1
                        
                        # Calcular média
                        if stats["total_leads"] > 0:
                            stats["average_value"] = stats["total_value"] / stats["total_leads"]
                        
                        logger.info(f"✅ Estatísticas do pipeline {pipeline_id} calculadas")
                        return {
                            "success": True,
                            "pipeline_id": pipeline_id,
                            "statistics": stats
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== EXPORTAÇÃO E IMPORTAÇÃO ====================
    
    async def export_leads_to_json(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Exporta leads para formato JSON
        
        Args:
            filters: Filtros opcionais para exportação
            
        Returns:
            Dados exportados em JSON
        """
        try:
            # Buscar leads com filtros
            if filters:
                result = await self.search_leads_by_filter(filters, limit=500)
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.endpoints["leads"],
                        params={"limit": 500},
                        headers=self.kommo_config["headers"]
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            result = {
                                "success": True,
                                "leads": data.get("_embedded", {}).get("leads", [])
                            }
                        else:
                            error = await response.text()
                            return {"success": False, "error": error}
            
            if result.get("success"):
                leads = result.get("leads", [])
                
                # Formatar dados para exportação
                export_data = {
                    "export_date": datetime.now().isoformat(),
                    "total_leads": len(leads),
                    "leads": []
                }
                
                for lead in leads:
                    export_lead = {
                        "id": lead.get("id"),
                        "name": lead.get("name"),
                        "price": lead.get("price"),
                        "status_id": lead.get("status_id"),
                        "pipeline_id": lead.get("pipeline_id"),
                        "created_at": lead.get("created_at"),
                        "updated_at": lead.get("updated_at"),
                        "tags": [tag.get("name") for tag in lead.get("_embedded", {}).get("tags", [])],
                        "custom_fields": {}
                    }
                    
                    # Adicionar campos customizados
                    for field in lead.get("custom_fields_values", []):
                        field_id = field.get("field_id")
                        values = field.get("values", [])
                        if values:
                            export_lead["custom_fields"][field_id] = values[0].get("value")
                    
                    export_data["leads"].append(export_lead)
                
                logger.info(f"✅ Exportados {len(leads)} leads para JSON")
                return {
                    "success": True,
                    "export": export_data
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Erro ao exportar leads: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== GESTÃO DE CAMPANHAS ====================
    
    async def create_campaign_leads(
        self,
        campaign_name: str,
        leads_data: List[Dict[str, Any]],
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        Cria múltiplos leads de uma campanha
        
        Args:
            campaign_name: Nome da campanha
            leads_data: Lista de dados dos leads
            tags: Tags da campanha
            
        Returns:
            Resultado da criação em lote
        """
        try:
            created_leads = []
            failed_leads = []
            
            # Adicionar tag da campanha
            campaign_tags = tags + [f"campanha-{campaign_name}"]
            
            for lead_data in leads_data:
                # Adicionar tags da campanha
                lead_data["tags"] = campaign_tags
                
                # Criar lead
                result = await self.create_or_update_lead(
                    name=lead_data.get("name"),
                    phone=lead_data.get("phone"),
                    email=lead_data.get("email"),
                    tags=campaign_tags,
                    custom_fields=lead_data.get("custom_fields", {})
                )
                
                if result.get("success"):
                    created_leads.append(result)
                else:
                    failed_leads.append({
                        "lead_data": lead_data,
                        "error": result.get("error")
                    })
            
            logger.info(f"✅ Campanha '{campaign_name}': {len(created_leads)} leads criados, {len(failed_leads)} falharam")
            
            return {
                "success": True,
                "campaign_name": campaign_name,
                "total_created": len(created_leads),
                "total_failed": len(failed_leads),
                "created_leads": created_leads,
                "failed_leads": failed_leads
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar campanha: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== DUPLICAÇÃO E MERGE ====================
    
    async def find_duplicate_leads(
        self,
        field: str = "phone"
    ) -> Dict[str, Any]:
        """
        Encontra leads duplicados por campo específico
        
        Args:
            field: Campo para verificar duplicação (phone, email, etc)
            
        Returns:
            Lista de duplicados encontrados
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Buscar todos os leads
                async with session.get(
                    self.endpoints["leads"],
                    params={"limit": 500},
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        leads = data.get("_embedded", {}).get("leads", [])
                        
                        # Mapear por campo
                        field_map = {}
                        duplicates = {}
                        
                        for lead in leads:
                            # Extrair valor do campo
                            field_value = None
                            
                            if field == "phone":
                                # Buscar nos campos customizados
                                for custom_field in lead.get("custom_fields_values", []):
                                    if custom_field.get("field_id") == self.custom_fields.get("whatsapp"):
                                        values = custom_field.get("values", [])
                                        if values:
                                            field_value = values[0].get("value")
                                            break
                            elif field == "email":
                                # Buscar email nos contatos vinculados
                                contacts = lead.get("_embedded", {}).get("contacts", [])
                                if contacts:
                                    # Aqui precisaríamos buscar o contato para pegar o email
                                    pass
                            
                            if field_value:
                                if field_value not in field_map:
                                    field_map[field_value] = []
                                field_map[field_value].append({
                                    "id": lead.get("id"),
                                    "name": lead.get("name"),
                                    "created_at": lead.get("created_at")
                                })
                        
                        # Identificar duplicados
                        for value, leads_list in field_map.items():
                            if len(leads_list) > 1:
                                duplicates[value] = leads_list
                        
                        logger.info(f"✅ Encontrados {len(duplicates)} grupos de duplicados")
                        return {
                            "success": True,
                            "total_duplicates": len(duplicates),
                            "duplicates": duplicates
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao buscar duplicados: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== HISTÓRICO COMPLETO ====================
    
    async def get_lead_complete_history(
        self,
        lead_id: Union[str, int]
    ) -> Dict[str, Any]:
        """
        Obtém histórico completo de um lead
        
        Args:
            lead_id: ID do lead no Kommo
            
        Returns:
            Histórico completo do lead
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Buscar lead com todos os embeds
                url = f"{self.endpoints['leads']}/{lead_id}"
                params = {
                    "with": "contacts,companies,leads,tags,notes,tasks"
                }
                
                async with session.get(
                    url,
                    params=params,
                    headers=self.kommo_config["headers"]
                ) as response:
                    if response.status == 200:
                        lead_data = await response.json()
                        
                        # Buscar eventos/notas
                        events_url = f"{self.endpoints['events']}"
                        events_params = {
                            "filter[entity]": "leads",
                            "filter[entity_id]": lead_id,
                            "limit": 100
                        }
                        
                        async with session.get(
                            events_url,
                            params=events_params,
                            headers=self.kommo_config["headers"]
                        ) as events_response:
                            events_data = {}
                            if events_response.status == 200:
                                events_data = await events_response.json()
                        
                        history = {
                            "lead": lead_data,
                            "events": events_data.get("_embedded", {}).get("events", []),
                            "timeline": []
                        }
                        
                        # Construir timeline
                        # Adicionar criação
                        history["timeline"].append({
                            "type": "created",
                            "date": lead_data.get("created_at"),
                            "details": "Lead criado"
                        })
                        
                        # Adicionar última atualização
                        history["timeline"].append({
                            "type": "updated",
                            "date": lead_data.get("updated_at"),
                            "details": "Lead atualizado"
                        })
                        
                        # Ordenar timeline
                        history["timeline"].sort(key=lambda x: x["date"] or 0)
                        
                        logger.info(f"✅ Histórico completo do lead {lead_id} obtido")
                        return {
                            "success": True,
                            "lead_id": lead_id,
                            "history": history
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
                        
        except Exception as e:
            logger.error(f"Erro ao obter histórico completo: {e}")
            return {"success": False, "error": str(e)}