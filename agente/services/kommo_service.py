"""
Serviço de integração com Kommo CRM
Gerencia leads, pipelines e comunicação com o CRM
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import httpx

from ..core.config import (
    KOMMO_BASE_URL,
    KOMMO_LONG_LIVED_TOKEN,
    KOMMO_SUBDOMAIN,
    KOMMO_STAGES
)
from ..core.logger import get_logger

logger = get_logger(__name__)


class KommoAPIError(Exception):
    """Exceção específica para erros da API do Kommo"""
    def __init__(self, status_code: int, message: str, response_data: Dict = None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data or {}
        super().__init__(f"Kommo API Error ({status_code}): {message}")


class KommoService:
    """Serviço para integração com Kommo CRM"""
    
    def __init__(self):
        self.base_url = f"{KOMMO_BASE_URL}/api/v4"
        self.token = KOMMO_LONG_LIVED_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Cache
        self._pipelines_cache = None
        self._custom_fields_cache = None
        self._account_info_cache = None
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=1)  # Cache válido por 1 hora
        
        # OAuth2 token info
        self._access_token = KOMMO_LONG_LIVED_TOKEN
        self._refresh_token = None
        self._token_expires_at = None
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - fecha o cliente HTTP"""
        await self.client.aclose()
    
    def _is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido"""
        if not self._cache_timestamp:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_duration
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Faz uma requisição para a API do Kommo com tratamento de erros
        
        Args:
            method: Método HTTP (GET, POST, PATCH, etc)
            endpoint: Endpoint da API (sem a base URL)
            **kwargs: Argumentos adicionais para a requisição
            
        Returns:
            Dict com a resposta da API
            
        Raises:
            KommoAPIError: Em caso de erro na API
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        # Atualiza headers se fornecidos
        headers = self.headers.copy()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            # Tratamento de erros HTTP específicos do Kommo
            if response.status_code == 401:
                # Token expirado - tentar renovar
                if await self._refresh_access_token():
                    # Tentar novamente com novo token
                    headers['Authorization'] = f'Bearer {self._access_token}'
                    response = await self.client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        **kwargs
                    )
                else:
                    raise KommoAPIError(401, "Falha na autenticação - token inválido ou expirado")
            
            if response.status_code == 404:
                raise KommoAPIError(404, "Recurso não encontrado", response.json() if response.text else {})
            
            if response.status_code == 429:
                # Rate limit exceeded
                retry_after = response.headers.get('Retry-After', 60)
                raise KommoAPIError(429, f"Rate limit excedido. Tente novamente em {retry_after} segundos")
            
            if response.status_code >= 400:
                error_data = response.json() if response.text else {}
                error_message = error_data.get('message', response.text)
                raise KommoAPIError(response.status_code, error_message, error_data)
            
            # Retornar resposta parseada se houver conteúdo
            if response.text:
                return response.json()
            return {}
            
        except httpx.TimeoutException:
            raise KommoAPIError(0, "Timeout na requisição para o Kommo")
        except httpx.RequestError as e:
            raise KommoAPIError(0, f"Erro na requisição: {str(e)}")
        except json.JSONDecodeError:
            raise KommoAPIError(0, f"Resposta inválida do Kommo: {response.text}")
    
    async def _refresh_access_token(self) -> bool:
        """
        Renova o access token usando o refresh token
        
        Returns:
            True se o token foi renovado com sucesso, False caso contrário
        """
        # Por enquanto, retorna False pois estamos usando long-lived token
        # Implementar quando tivermos OAuth2 completo
        logger.warning("Renovação de token OAuth2 ainda não implementada")
        return False
    
    async def get_account_info(self) -> Dict:
        """
        Obtém informações da conta
        
        Returns:
            Dict com informações da conta
        """
        if self._account_info_cache and self._is_cache_valid():
            return self._account_info_cache
        
        try:
            response = await self._make_request('GET', '/account')
            self._account_info_cache = response
            return response
        except KommoAPIError as e:
            logger.error(f"Erro ao obter informações da conta: {e}")
            raise
    
    async def get_pipelines(self) -> List[Dict]:
        """
        Lista todos os pipelines e seus stages
        
        Returns:
            Lista de pipelines com seus stages
        """
        if self._pipelines_cache and self._is_cache_valid():
            return self._pipelines_cache
        
        try:
            response = await self._make_request('GET', '/leads/pipelines')
            pipelines = response.get('_embedded', {}).get('pipelines', [])
            
            # Atualizar cache
            self._pipelines_cache = pipelines
            self._cache_timestamp = datetime.now()
            
            return pipelines
        except KommoAPIError as e:
            logger.error(f"Erro ao buscar pipelines: {e}")
            raise
    
    async def get_custom_fields(self) -> List[Dict]:
        """
        Lista todos os campos customizados disponíveis
        
        Returns:
            Lista de campos customizados
        """
        if self._custom_fields_cache and self._is_cache_valid():
            return self._custom_fields_cache
        
        try:
            response = await self._make_request('GET', '/leads/custom_fields')
            fields = response.get('_embedded', {}).get('custom_fields', [])
            
            # Atualizar cache
            self._custom_fields_cache = fields
            self._cache_timestamp = datetime.now()
            
            return fields
        except KommoAPIError as e:
            logger.error(f"Erro ao buscar campos customizados: {e}")
            raise
    
    async def _get_phone_field_id(self) -> Optional[int]:
        """
        Obtém o ID do campo de telefone
        
        Returns:
            ID do campo de telefone ou None se não encontrado
        """
        fields = await self.get_custom_fields()
        for field in fields:
            if field.get('code') == 'PHONE' or field.get('name', '').lower() in ['telefone', 'phone', 'celular']:
                return field.get('id')
        return None
    
    async def _get_stage_id(self, stage_name: str) -> Optional[int]:
        """
        Obtém o ID de um stage pelo nome
        
        Args:
            stage_name: Nome do stage
            
        Returns:
            ID do stage ou None se não encontrado
        """
        pipelines = await self.get_pipelines()
        
        # Procurar em todos os pipelines
        for pipeline in pipelines:
            statuses = pipeline.get('_embedded', {}).get('statuses', [])
            for status in statuses:
                if status.get('name', '').lower() == stage_name.lower():
                    return status.get('id')
        
        return None
    
    async def create_lead(self, name: str, phone: str, custom_fields: Optional[Dict] = None) -> Dict:
        """
        Cria um novo lead no CRM
        
        Args:
            name: Nome do lead
            phone: Telefone do lead
            custom_fields: Campos customizados adicionais
            
        Returns:
            Dict com os dados do lead criado
        """
        try:
            # Buscar ID do campo de telefone
            phone_field_id = await self._get_phone_field_id()
            
            # Preparar dados do lead
            lead_data = {
                "name": name,
                "custom_fields_values": []
            }
            
            # Adicionar telefone se campo encontrado
            if phone_field_id:
                lead_data["custom_fields_values"].append({
                    "field_id": phone_field_id,
                    "values": [{"value": phone}]
                })
            
            # Adicionar campos customizados extras
            if custom_fields:
                for field_id, value in custom_fields.items():
                    lead_data["custom_fields_values"].append({
                        "field_id": field_id,
                        "values": [{"value": value}]
                    })
            
            # Criar lead (API espera uma lista)
            response = await self._make_request('POST', '/leads', json=[lead_data])
            
            # Retornar o primeiro lead criado
            leads = response.get('_embedded', {}).get('leads', [])
            if leads:
                lead = leads[0]
                logger.info(f"Lead criado com sucesso: ID {lead.get('id')} - {name}")
                return lead
            
            raise KommoAPIError(0, "Lead criado mas resposta vazia")
            
        except KommoAPIError as e:
            logger.error(f"Erro ao criar lead: {e}")
            raise
    
    async def update_lead(self, lead_id: int, **kwargs) -> Dict:
        """
        Atualiza um lead existente
        
        Args:
            lead_id: ID do lead
            **kwargs: Campos a serem atualizados
            
        Returns:
            Dict com os dados do lead atualizado
        """
        try:
            # Preparar dados de atualização
            update_data = {"id": lead_id}
            update_data.update(kwargs)
            
            # Atualizar lead (API espera uma lista)
            response = await self._make_request('PATCH', '/leads', json=[update_data])
            
            # Retornar o primeiro lead atualizado
            leads = response.get('_embedded', {}).get('leads', [])
            if leads:
                lead = leads[0]
                logger.info(f"Lead {lead_id} atualizado com sucesso")
                return lead
            
            raise KommoAPIError(0, "Lead atualizado mas resposta vazia")
            
        except KommoAPIError as e:
            logger.error(f"Erro ao atualizar lead {lead_id}: {e}")
            raise
    
    async def get_lead(self, lead_id: int) -> Dict:
        """
        Busca um lead por ID
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Dict com os dados do lead
        """
        try:
            response = await self._make_request('GET', f'/leads/{lead_id}')
            logger.info(f"Lead {lead_id} encontrado")
            return response
        except KommoAPIError as e:
            logger.error(f"Erro ao buscar lead {lead_id}: {e}")
            raise
    
    async def update_lead_stage(self, lead_id: int, stage_name: str) -> Dict:
        """
        Move um lead para um estágio específico do pipeline
        
        Args:
            lead_id: ID do lead
            stage_name: Nome do estágio (usar valores de KOMMO_STAGES)
            
        Returns:
            Dict com os dados do lead atualizado
        """
        try:
            # Buscar ID do stage
            stage_id = await self._get_stage_id(stage_name)
            
            if not stage_id:
                # Tentar com o mapeamento KOMMO_STAGES
                for key, mapped_name in KOMMO_STAGES.items():
                    if key == stage_name or mapped_name == stage_name.lower():
                        stage_id = await self._get_stage_id(mapped_name)
                        break
            
            if not stage_id:
                raise KommoAPIError(0, f"Stage '{stage_name}' não encontrado")
            
            # Atualizar o lead com o novo stage
            return await self.update_lead(lead_id, status_id=stage_id)
            
        except KommoAPIError as e:
            logger.error(f"Erro ao mover lead {lead_id} para stage {stage_name}: {e}")
            raise
    
    async def add_note(self, lead_id: int, text: str) -> Dict:
        """
        Adiciona uma nota a um lead
        
        Args:
            lead_id: ID do lead
            text: Texto da nota
            
        Returns:
            Dict com os dados da nota criada
        """
        try:
            note_data = {
                "entity_id": lead_id,
                "note_type": "common",
                "params": {
                    "text": text
                }
            }
            
            response = await self._make_request('POST', f'/leads/{lead_id}/notes', json=[note_data])
            
            # Retornar a primeira nota criada
            notes = response.get('_embedded', {}).get('notes', [])
            if notes:
                note = notes[0]
                logger.info(f"Nota adicionada ao lead {lead_id}")
                return note
            
            raise KommoAPIError(0, "Nota criada mas resposta vazia")
            
        except KommoAPIError as e:
            logger.error(f"Erro ao adicionar nota ao lead {lead_id}: {e}")
            raise
    
    async def add_tag(self, lead_id: int, tag: str) -> Dict:
        """
        Adiciona uma tag a um lead
        
        Args:
            lead_id: ID do lead
            tag: Nome da tag
            
        Returns:
            Dict com os dados do lead atualizado
        """
        try:
            # Buscar lead atual para preservar tags existentes
            current_lead = await self.get_lead(lead_id)
            current_tags = current_lead.get('_embedded', {}).get('tags', [])
            
            # Adicionar nova tag se não existir
            tag_names = [t.get('name') for t in current_tags]
            if tag not in tag_names:
                tag_names.append(tag)
            
            # Atualizar lead com tags
            tag_data = {
                "id": lead_id,
                "_embedded": {
                    "tags": [{"name": name} for name in tag_names]
                }
            }
            
            response = await self._make_request('PATCH', '/leads', json=[tag_data])
            
            # Retornar o lead atualizado
            leads = response.get('_embedded', {}).get('leads', [])
            if leads:
                lead = leads[0]
                logger.info(f"Tag '{tag}' adicionada ao lead {lead_id}")
                return lead
            
            raise KommoAPIError(0, "Tag adicionada mas resposta vazia")
            
        except KommoAPIError as e:
            logger.error(f"Erro ao adicionar tag ao lead {lead_id}: {e}")
            raise
    
    async def search_leads(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Busca leads por query
        
        Args:
            query: Termo de busca (nome, telefone, email, etc)
            limit: Número máximo de resultados
            
        Returns:
            Lista de leads encontrados
        """
        try:
            params = {
                "query": query,
                "limit": limit
            }
            
            response = await self._make_request('GET', '/leads', params=params)
            leads = response.get('_embedded', {}).get('leads', [])
            
            logger.info(f"Encontrados {len(leads)} leads para query '{query}'")
            return leads
            
        except KommoAPIError as e:
            logger.error(f"Erro ao buscar leads: {e}")
            raise
    
    async def get_lead_by_phone(self, phone: str) -> Optional[Dict]:
        """
        Busca um lead pelo número de telefone
        
        Args:
            phone: Número de telefone
            
        Returns:
            Dict com os dados do lead ou None se não encontrado
        """
        try:
            # Limpar telefone para busca
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            # Buscar por diferentes formatos
            for search_term in [phone, clean_phone, f"+55{clean_phone}", clean_phone[-9:]]:
                leads = await self.search_leads(search_term)
                if leads:
                    # Retornar o primeiro lead encontrado
                    return leads[0]
            
            return None
            
        except KommoAPIError as e:
            logger.error(f"Erro ao buscar lead por telefone {phone}: {e}")
            return None
    
    async def create_task(self, lead_id: int, text: str, complete_till: Optional[datetime] = None) -> Dict:
        """
        Cria uma tarefa para um lead
        
        Args:
            lead_id: ID do lead
            text: Texto da tarefa
            complete_till: Data/hora limite para conclusão
            
        Returns:
            Dict com os dados da tarefa criada
        """
        try:
            task_data = {
                "text": text,
                "complete_till": int(complete_till.timestamp()) if complete_till else None,
                "entity_id": lead_id,
                "entity_type": "leads"
            }
            
            response = await self._make_request('POST', '/tasks', json=[task_data])
            
            # Retornar a primeira tarefa criada
            tasks = response.get('_embedded', {}).get('tasks', [])
            if tasks:
                task = tasks[0]
                logger.info(f"Tarefa criada para lead {lead_id}")
                return task
            
            raise KommoAPIError(0, "Tarefa criada mas resposta vazia")
            
        except KommoAPIError as e:
            logger.error(f"Erro ao criar tarefa para lead {lead_id}: {e}")
            raise
    
    async def close(self):
        """Fecha o cliente HTTP"""
        await self.client.aclose()


# Singleton do serviço
_kommo_service_instance = None


def get_kommo_service() -> KommoService:
    """
    Retorna uma instância singleton do KommoService
    
    Returns:
        Instância do KommoService
    """
    global _kommo_service_instance
    
    if _kommo_service_instance is None:
        _kommo_service_instance = KommoService()
    
    return _kommo_service_instance