"""
CRM Service 100% REAL - Kommo API
ZERO simulação, MÁXIMA simplicidade
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import random
from functools import wraps
from app.utils.logger import emoji_logger
from app.config import settings

def async_retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0, max_delay: float = 30.0, backoff_factor: float = 2.0):
    """
    Decorator para retry assíncrono com backoff exponencial
    ZERO complexidade, MÁXIMA resiliência
    
    Args:
        max_retries: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        max_delay: Delay máximo em segundos
        backoff_factor: Fator de multiplicação do delay
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = initial_delay
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # Adiciona jitter para evitar thundering herd
                        jitter = random.uniform(0, delay * 0.1)
                        sleep_time = min(delay + jitter, max_delay)
                        
                        emoji_logger.service_warning(
                            f"Tentativa {attempt + 1}/{max_retries} falhou: {e}. Aguardando {sleep_time:.1f}s..."
                        )
                        await asyncio.sleep(sleep_time)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        emoji_logger.service_error(f"Todas as {max_retries} tentativas falharam: {e}")
                except Exception as e:
                    # Para outros erros, não fazer retry
                    raise e
            
            # Se chegou aqui, todas as tentativas falharam
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

class CRMServiceReal:
    """
    Serviço REAL de CRM - Kommo API
    SIMPLES e FUNCIONAL - 100% real
    """
    
    def __init__(self):
        self.is_initialized = False
        self.base_url = settings.kommo_base_url or "https://leonardofvieira00.kommo.com"
        self.access_token = settings.kommo_long_lived_token
        self.pipeline_id = int(settings.kommo_pipeline_id or 11672895)  # Garantir que é int
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        self.session = None
        self._session_timeout = aiohttp.ClientTimeout(total=30)  # 30s timeout
        
        # Cache SIMPLES de estágios (evita buscar toda vez)
        self._stages_cache = None
        self._cache_ttl = 3600  # 1 hora de cache
        self._cache_timestamp = None
        
        # IDs dos campos customizados VALIDADOS e TESTADOS (2025-08-13)
        # Todos os campos abaixo foram testados e validados na API do Kommo
        self.custom_fields = {
            # ===== CAMPOS VALIDADOS E FUNCIONAIS =====
            "phone": 392802,          # WhatsApp (text) ✅ TESTADO
            "whatsapp": 392802,       # Alias para phone ✅ TESTADO
            "bill_value": 392804,     # Valor Conta Energia (numeric) ✅ TESTADO
            "valor_conta": 392804,    # Alias para bill_value ✅ TESTADO
            "solution_type": 392808,  # Solução Solar (select) ✅ TESTADO
            "solucao_solar": 392808,  # Alias para solution_type ✅ TESTADO
            "calendar_link": 395520,  # Link do evento no Google Calendar (url) ✅ TESTADO
            "google_calendar": 395520, # Alias para calendar_link ✅ TESTADO
            
            # ===== CAMPOS DE OUTRAS ENTIDADES (NÃO USAR EM LEADS) =====
            # "location": 152429,     # Endereço (textarea) - COMPANIES apenas, não LEADS
            
            # ===== CAMPOS REMOVIDOS (CAUSAVAM ERRO OU NÃO EXISTEM) =====
            # "conversation_id": 392860,  # Removido por conflitos
            # "score": None,              # Removido - causava erro 400
            # "email": None,              # Não existe campo email customizado em LEADS
            # "property_type": None,      # Não existe campo tipo de propriedade
            "conversation_id": 392860     # Mantendo para compatibilidade
        }
        
        # Mapeamento de valores do campo SELECT "Solução Solar" (ID: 392808)
        # IMPORTANTE: Usar enum_id, não o texto!
        # Valores REAIS validados em 13/08/2025 via API Kommo
        self.solution_type_values = {
            "usina própria": 326358,
            "usina propria": 326358,
            "fazenda solar": 326360,
            "consórcio": 326362,
            "consorcio": 326362,
            "consultoria": 326364,
            "não definido": 326366,
            "nao definido": 326366,
            "aluguel de lote": 1078618,  # ID correto do Kommo
            "compra com desconto": 1078620,  # ID correto do Kommo
            "usina investimento": 1078622  # ID correto do Kommo
        }
        
        # Opções do campo solution_type (select) - VALIDADAS
        self.solution_type_options = {
            "Usina Própria": 326358,
            "Fazenda Solar": 326360,
            "Consórcio": 326362,
            "Consultoria": 326364,
            "Não Definido": 326366,
            "Aluguel de Lote": 1078618,
            "Compra com Desconto": 1078620,
            "Usina Investimento": 1078622
        }
        
    async def initialize(self):
        """Inicializa conexão REAL com Kommo CRM e busca IDs dinamicamente"""
        if self.is_initialized:
            return
        
        try:
            # 🔧 Criar sessão HTTP com timeout e connector configurado
            connector = aiohttp.TCPConnector(
                limit=10,  # Max 10 conexões simultâneas
                limit_per_host=5,  # Max 5 por host
                ttl_dns_cache=300,  # Cache DNS por 5min
                use_dns_cache=True,
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self._session_timeout
            )
            
            # Testar conexão com a API
            async with self.session.get(
                f"{self.base_url}/api/v4/account",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    account = await response.json()
                    emoji_logger.service_ready(
                        f"✅ Kommo CRM conectado: {account.get('name', 'CRM')}"
                    )
                    
                    # Buscar campos customizados dinamicamente
                    await self._fetch_custom_fields()
                    
                    # Buscar estágios do pipeline dinamicamente
                    await self._fetch_pipeline_stages()
                    
                    self.is_initialized = True
                else:
                    raise Exception(f"Erro ao conectar: {response.status}")
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao conectar Kommo: {e}")
            if self.session:
                await self._close_session_safely()
            raise
    
    async def _fetch_custom_fields(self):
        """Busca IDs dos campos customizados dinamicamente"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v4/leads/custom_fields",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    fields = await response.json()
                    
                    # Mapear campos pelo nome (baseado nos campos reais do Kommo)
                    field_mapping = {
                        "whatsapp": "phone",
                        "telefone": "phone",
                        "phone": "phone",
                        "valor conta energia": "bill_value",
                        "valor_conta_energia": "bill_value",
                        "valor da conta": "bill_value",
                        "valor conta": "bill_value",
                        "solução solar": "solution_type",
                        "solucao solar": "solution_type",
                        "tipo de solução": "solution_type",
                        "link do evento no google calendar": "calendar_link",
                        "link do evento": "calendar_link",
                        "google calendar": "calendar_link",
                        "calendario": "calendar_link",
                        "local da instalação": "location",
                        "local_da_instalação": "location",
                        "localização": "location",
                        "endereço": "location",
                        "score qualificação": "score",
                        "score_qualificação": "score",
                        "score": "score",
                        "id conversa": "conversation_id",
                        "id_conversa": "conversation_id"
                    }
                    
                    # Atualizar mapeamento de campos
                    for field in fields.get("_embedded", {}).get("custom_fields", []):
                        field_name_lower = field.get("name", "").lower()
                        for key, mapped_name in field_mapping.items():
                            if key in field_name_lower:
                                self.custom_fields[mapped_name] = field.get("id")
                                emoji_logger.system_debug(f"Campo mapeado: {mapped_name} -> {field.get('id')}")
                                break
                    
                    emoji_logger.service_info(f"📊 {len(self.custom_fields)} campos customizados mapeados")
        except Exception as e:
            emoji_logger.service_warning(f"Erro ao buscar campos customizados: {e}")
            # Manter os IDs padrão se falhar
    
    async def _fetch_pipeline_stages(self):
        """Busca estágios do pipeline dinamicamente COM CACHE SIMPLES"""
        try:
            # Verificar cache primeiro
            import time
            current_time = time.time()
            
            if (self._stages_cache and 
                self._cache_timestamp and 
                (current_time - self._cache_timestamp) < self._cache_ttl):
                emoji_logger.system_debug("📦 Usando cache de estágios")
                self.stage_map = self._stages_cache
                return
            
            emoji_logger.system_debug("🔄 Buscando estágios do Kommo...")
            
            # Buscar estágios do Kommo
            async with self.session.get(
                f"{self.base_url}/api/v4/leads/pipelines",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    pipelines = await response.json()
                    
                    # Encontrar o pipeline correto
                    for pipeline in pipelines.get("_embedded", {}).get("pipelines", []):
                        if pipeline.get("id") == self.pipeline_id:
                            # Criar mapa de estágios
                            self.stage_map = {}
                            for status in pipeline.get("_embedded", {}).get("statuses", []):
                                stage_name = status.get("name", "").lower()
                                stage_id = status.get("id")
                                
                                # Mapear variações do nome
                                self.stage_map[stage_name] = stage_id
                                self.stage_map[stage_name.replace(" ", "_")] = stage_id
                                self.stage_map[stage_name.upper()] = stage_id
                                
                                # Adicionar versões sem acentos para compatibilidade
                                import unicodedata
                                stage_name_normalized = unicodedata.normalize('NFKD', stage_name)
                                stage_name_no_accents = ''.join([c for c in stage_name_normalized if not unicodedata.combining(c)])
                                
                                self.stage_map[stage_name_no_accents] = stage_id
                                self.stage_map[stage_name_no_accents.replace(" ", "_")] = stage_id
                                
                                # Adicionar mapeamentos específicos conhecidos
                                if "não interessado" in stage_name:
                                    self.stage_map["nao_interessado"] = stage_id
                                    self.stage_map["NAO_INTERESSADO"] = stage_id
                                elif "reunião agendada" in stage_name:
                                    self.stage_map["reuniao_agendada"] = stage_id
                                    self.stage_map["REUNIAO_AGENDADA"] = stage_id
                                elif "em qualificação" in stage_name:
                                    self.stage_map["em_qualificacao"] = stage_id
                                    self.stage_map["EM_QUALIFICACAO"] = stage_id
                                
                            emoji_logger.service_info(f"📈 {len(self.stage_map)} estágios mapeados")
                            
                            # Salvar no cache SIMPLES
                            import time
                            self._stages_cache = self.stage_map.copy()
                            self._cache_timestamp = time.time()
                            emoji_logger.system_debug("💾 Cache de estágios atualizado")
                            
                            break
        except Exception as e:
            emoji_logger.service_warning(f"Erro ao buscar estágios: {e}")
            # Manter mapeamento padrão se falhar
    
    async def create_or_update_lead_direct(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método direto para criar/atualizar lead no Kommo (alias para create_or_update_lead)
        Usado pelo KommoAutoSyncService
        """
        return await self.create_or_update_lead(lead_data)
    
    @async_retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def create_or_update_lead(self, lead_data: Dict[str, Any], tags: List[str] = None) -> Dict[str, Any]:
        """
        Cria ou atualiza lead REAL no Kommo com tags
        🔥 FIX: Adicionando tags diretamente no _embedded
        """
        print(f"🔍 DEBUG: create_or_update_lead chamado com: {lead_data}")
        
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Primeiro, verificar se lead já existe pelo telefone
            phone = lead_data.get("phone", "")
            existing_lead = None
            
            if phone:
                existing_lead = await self._find_lead_by_phone(phone)
            
            # Preparar dados do lead
            kommo_lead = {
                "name": lead_data.get("name", "Lead Solar"),
                "price": int((lead_data.get("bill_value") or 0) * 12 * 5),  # Valor potencial 5 anos
                "pipeline_id": self.pipeline_id,
                "custom_fields_values": []
            }
            
            # 🔥 FIX: Adicionar tags no _embedded se fornecidas
            if tags:
                kommo_lead["_embedded"] = {
                    "tags": [{"name": tag} for tag in tags]
                }
            
            print(f"🔍 DEBUG: Preparando lead: {kommo_lead}")
            
            # ===== ADICIONAR CAMPOS CUSTOMIZADOS VALIDADOS =====
            
            # Campo WhatsApp/Phone (text)
            if lead_data.get("phone") and self.custom_fields.get("phone"):
                kommo_lead["custom_fields_values"].append({
                    "field_id": self.custom_fields["phone"],
                    "values": [{"value": lead_data["phone"]}]
                })
            
            # Campo Valor Conta Energia (numeric)
            if lead_data.get("bill_value") and self.custom_fields.get("bill_value"):
                kommo_lead["custom_fields_values"].append({
                    "field_id": self.custom_fields["bill_value"],
                    "values": [{"value": str(lead_data["bill_value"])}]
                })
            
            # Campo Solução Solar (select) - VALIDADO ✅
            if lead_data.get("solution_type") and self.custom_fields.get("solution_type"):
                solution_text = str(lead_data["solution_type"]).lower()
                enum_id = self.solution_type_values.get(solution_text)
                
                if enum_id:
                    kommo_lead["custom_fields_values"].append({
                        "field_id": self.custom_fields["solution_type"],
                        "values": [{"enum_id": enum_id}]  # Usar enum_id para SELECT
                    })
                    emoji_logger.system_debug(f"Solution type '{solution_text}' mapeado para enum_id {enum_id}")
                else:
                    emoji_logger.service_warning(
                        f"Valor '{lead_data['solution_type']}' não é válido para Solução Solar. "
                        f"Use: {list(self.solution_type_values.keys())}"
                    )
            
            # Campo Calendar Link (url) - VALIDADO ✅
            if lead_data.get("calendar_link") and self.custom_fields.get("calendar_link"):
                kommo_lead["custom_fields_values"].append({
                    "field_id": self.custom_fields["calendar_link"],
                    "values": [{"value": str(lead_data["calendar_link"])}]
                })
            
            # ===== CAMPOS NÃO SUPORTADOS =====
            # Campo email: Não existe como campo customizado em LEADS (apenas CONTACTS)
            # Campo location: Existe apenas em COMPANIES, não em LEADS
            # Campo score: Removido - causava erro 400
            # Campo conversation_id: Removido por conflitos
            
            print(f"🔍 DEBUG: Campos customizados preparados: {kommo_lead['custom_fields_values']}")
            
            # Criar ou atualizar no Kommo
            if existing_lead:
                # Atualizar lead existente
                lead_id = existing_lead["id"]
                print(f"🔍 DEBUG: Atualizando lead existente: {lead_id}")
                async with self.session.patch(
                    f"{self.base_url}/api/v4/leads/{lead_id}",
                    headers=self.headers,
                    json=kommo_lead
                ) as response:
                    if response.status in [200, 202]:
                        emoji_logger.crm_event(
                            f"✅ Lead ATUALIZADO no Kommo: {lead_data.get('name')} - ID: {lead_id}"
                        )
                        return {
                            "success": True,
                            "lead_id": lead_id,
                            "action": "updated",
                            "message": "Lead atualizado com sucesso no CRM",
                            "real": True
                        }
            else:
                # Criar novo lead
                print(f"🔍 DEBUG: Criando novo lead com dados: {kommo_lead}")
                async with self.session.post(
                    f"{self.base_url}/api/v4/leads",
                    headers=self.headers,
                    json=[kommo_lead]  # API espera array
                ) as response:
                    print(f"🔍 DEBUG: Response status: {response.status}")
                    if response.status in [200, 201]:
                        result = await response.json()
                        print(f"🔍 DEBUG: Response JSON: {result}")
                        if result.get("_embedded", {}).get("leads"):
                            lead_id = result["_embedded"]["leads"][0]["id"]
                        else:
                            # Fallback se estrutura for diferente
                            lead_id = result.get("id", f"lead_{datetime.now().timestamp()}")
                        
                        emoji_logger.crm_event(
                            f"✅ Lead CRIADO no Kommo: {lead_data.get('name')} - ID: {lead_id}"
                        )
                        
                        # Adicionar nota inicial
                        await self.add_note(
                            str(lead_id),  # Garantir que é string
                            f"Lead criado via SDR IA\nScore: {lead_data.get('qualification_score', 0)}/100"
                        )
                        
                        return {
                            "success": True,
                            "lead_id": str(lead_id),  # Garantir que é string
                            "action": "created",
                            "message": "Lead criado com sucesso no CRM",
                            "real": True
                        }
                    else:
                        error_text = await response.text()
                        print(f"🔍 DEBUG: Erro na resposta: {error_text}")
            
            # Se chegou aqui, houve erro
            print(f"🔍 DEBUG: Chegou ao final sem sucesso")
            return {
                "success": False,
                "message": "Erro ao processar lead no CRM"
            }
            
        except Exception as e:
            import traceback
            emoji_logger.service_error(f"Erro ao criar/atualizar lead: {e}")
            emoji_logger.service_error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Erro ao processar lead: {e}",
                "error_details": str(e),
                "traceback": traceback.format_exc()
            }
    
    async def _find_lead_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Busca lead pelo telefone"""
        try:
            # Limpar telefone
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            # Buscar no Kommo
            async with self.session.get(
                f"{self.base_url}/api/v4/leads",
                headers=self.headers,
                params={"query": clean_phone}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    leads = result.get("_embedded", {}).get("leads", [])
                    if leads:
                        return leads[0]
        except:
            pass
        return None
    
    @async_retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def update_lead_stage(self, 
                               lead_id: str, 
                               stage: str,
                               notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Atualiza estágio REAL do lead no funil
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Usar mapa dinâmico se disponível, senão usar padrão
            if hasattr(self, 'stage_map') and self.stage_map:
                # Usar mapa dinâmico buscado na inicialização
                stage_map = self.stage_map
            else:
                # Mapeamento UNIFICADO de estágios para IDs do Kommo
                # ACEITA tanto PORTUGUÊS quanto INGLÊS
                stage_map = {
                    # ========== NOVO LEAD (ID: 89709459) ==========
                    # Português
                    "novo": 89709459,
                    "novo_lead": 89709459,
                    "NOVO": 89709459,
                    "NOVO_LEAD": 89709459,
                    # Inglês
                    "initial_contact": 89709459,
                    "INITIAL_CONTACT": 89709459,
                    "new_lead": 89709459,
                    "NEW_LEAD": 89709459,
                    
                    # ========== EM QUALIFICAÇÃO (ID: 89709463) ==========
                    # Português
                    "em_qualificacao": 89709463,
                    "em_qualificação": 89709463,
                    "EM_QUALIFICACAO": 89709463,
                    "EM_QUALIFICAÇÃO": 89709463,
                    "contato": 89709463,
                    "CONTATO": 89709463,
                    # Inglês
                    "qualifying": 89709463,
                    "QUALIFYING": 89709463,
                    "in_qualification": 89709463,
                    "IN_QUALIFICATION": 89709463,
                    
                    # ========== QUALIFICADO (ID: 89709467) ==========
                    # Português
                    "qualificado": 89709467,
                    "QUALIFICADO": 89709467,
                    # Inglês
                    "qualified": 89709467,
                    "QUALIFIED": 89709467,
                    
                    # ========== REUNIÃO AGENDADA (ID: 89709595) ==========
                    # Português
                    "reunião_agendada": 89709595,
                    "reuniao_agendada": 89709595,
                    "REUNIÃO_AGENDADA": 89709595,
                    "REUNIAO_AGENDADA": 89709595,
                    "proposta": 89709595,
                    "PROPOSTA": 89709595,
                    # Inglês
                    "meeting_scheduled": 89709595,
                    "MEETING_SCHEDULED": 89709595,
                    "proposal": 89709595,
                    "PROPOSAL": 89709595,
                    
                    # ========== NÃO INTERESSADO (ID: 89709599) ==========
                    # Português
                    "não_interessado": 89709599,
                    "nao_interessado": 89709599,
                    "NÃO_INTERESSADO": 89709599,
                    "NAO_INTERESSADO": 89709599,
                    # Inglês
                    "not_interested": 89709599,
                    "NOT_INTERESTED": 89709599,
                    
                    # ========== GANHO/FECHADO (ID: 142) ==========
                    # Português
                    "ganho": 142,
                    "GANHO": 142,
                    "fechado": 142,
                    "FECHADO": 142,
                    # Inglês
                    "won": 142,
                    "WON": 142,
                    "closed": 142,
                    "CLOSED": 142,
                    
                    # ========== PERDIDO (ID: 143) ==========
                    # Português
                    "perdido": 143,
                    "PERDIDO": 143,
                    # Inglês
                    "lost": 143,
                    "LOST": 143
                }
            
            # Buscar ID com fallback para primeiro estágio (Novo Lead)
            status_id = stage_map.get(stage, stage_map.get(stage.lower(), stage_map.get(stage.upper(), 89709459)))
            
            # Atualizar no Kommo
            async with self.session.patch(
                f"{self.base_url}/api/v4/leads/{lead_id}",
                headers=self.headers,
                json={"status_id": status_id}
            ) as response:
                if response.status in [200, 202]:
                    emoji_logger.crm_event(
                        f"📈 Lead {lead_id} movido para: {stage} (REAL)"
                    )
                    
                    # Adicionar nota se fornecida
                    if notes:
                        await self.add_note(lead_id, notes)
                    
                    return {
                        "success": True,
                        "message": f"Lead atualizado para estágio {stage}",
                        "real": True
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Erro {response.status}: {error}")
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao atualizar estágio: {e}")
            return {
                "success": False,
                "message": f"Erro ao atualizar estágio: {e}"
            }
    
    async def add_note(self, lead_id: str, note: str) -> Dict[str, Any]:
        """
        Adiciona nota REAL ao lead
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            note_data = {
                "entity_id": int(lead_id),
                "note_type": "common",
                "params": {
                    "text": note
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v4/leads/{lead_id}/notes",
                headers=self.headers,
                json=[note_data]
            ) as response:
                if response.status in [200, 201]:
                    emoji_logger.crm_note(
                        f"📝 Nota REAL adicionada ao lead {lead_id}"
                    )
                    return {
                        "success": True,
                        "message": "Nota adicionada com sucesso",
                        "real": True
                    }
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao adicionar nota: {e}")
            return {
                "success": False,
                "message": f"Erro ao adicionar nota: {e}"
            }
    
    async def create_task(self, 
                         lead_id: str,
                         task_type: str,
                         due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Cria tarefa REAL no Kommo
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Data de vencimento (padrão: amanhã)
            if not due_date:
                due_date = datetime.now() + timedelta(days=1)
            
            task_data = {
                "text": task_type,
                "complete_till": int(due_date.timestamp()),
                "entity_id": int(lead_id),
                "entity_type": "leads",
                "task_type_id": 1  # 1 = Call
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v4/tasks",
                headers=self.headers,
                json=[task_data]
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    task_id = result["_embedded"]["tasks"][0]["id"]
                    
                    emoji_logger.crm_event(
                        f"📋 Tarefa REAL criada: {task_type} - ID: {task_id}"
                    )
                    
                    return {
                        "success": True,
                        "task_id": task_id,
                        "message": f"Tarefa '{task_type}' criada com sucesso",
                        "real": True
                    }
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao criar tarefa: {e}")
            return {
                "success": False,
                "message": f"Erro ao criar tarefa: {e}"
            }
    
    @async_retry_with_backoff(max_retries=2, initial_delay=0.5)
    async def get_lead_info(self, lead_id: str) -> Dict[str, Any]:
        """
        Busca informações REAIS do lead
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/v4/leads/{lead_id}",
                headers=self.headers,
                params={"with": "contacts"}
            ) as response:
                if response.status == 200:
                    lead = await response.json()
                    
                    # Extrair campos customizados
                    custom_values = {}
                    for field in lead.get("custom_fields_values", []):
                        field_id = field["field_id"]
                        value = field["values"][0]["value"] if field["values"] else None
                        
                        # Mapear IDs para nomes
                        for name, fid in self.custom_fields.items():
                            if fid == field_id:
                                custom_values[name] = value
                                break
                    
                    return {
                        "success": True,
                        "lead": {
                            "id": lead["id"],
                            "name": lead["name"],
                            "price": lead.get("price", 0),
                            "status": lead.get("status_id"),
                            "phone": custom_values.get("phone"),
                            "email": custom_values.get("email"),
                            "bill_value": custom_values.get("bill_value"),
                            "created_at": lead.get("created_at")
                        },
                        "real": True
                    }
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao buscar lead: {e}")
            return {
                "success": False,
                "message": f"Erro ao buscar lead: {e}"
            }
    
    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca lead por ID (alias simplificado para get_lead_info)
        Retorna os dados do lead ou None se não encontrado
        """
        result = await self.get_lead_info(lead_id)
        if result.get("success"):
            lead = result.get("lead", {})
            # Retorna direto o lead com status_id no formato esperado
            return {
                "id": lead.get("id"),
                "name": lead.get("name"),
                "status_id": lead.get("status"),  # Renomeia status para status_id
                "pipeline_id": lead.get("pipeline_id"),  # Adicionar se disponível
                "phone": lead.get("phone"),
                "email": lead.get("email"),
                "bill_value": lead.get("bill_value"),
                "created_at": lead.get("created_at")
            }
        return None
    
    @async_retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def add_tags_to_lead(self, lead_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Adiciona tags REAIS ao lead no Kommo
        🔥 FIX: Usando _embedded no PATCH ao invés do endpoint /tags
        
        Args:
            lead_id: ID do lead
            tags: Lista de tags a adicionar
            
        Returns:
            Dict com resultado da operação
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 🔥 FIX: Usar PATCH com _embedded para adicionar tags
            update_data = {
                "_embedded": {
                    "tags": [{"name": tag} for tag in tags]
                }
            }
            
            async with self.session.patch(
                f"{self.base_url}/api/v4/leads/{lead_id}",
                headers=self.headers,
                json=update_data
            ) as response:
                if response.status in [200, 202]:
                    emoji_logger.crm_event(
                        f"🏷️ Tags adicionadas ao lead {lead_id}: {', '.join(tags)}"
                    )
                    return {
                        "success": True,
                        "message": f"Tags adicionadas com sucesso: {', '.join(tags)}",
                        "tags": tags,
                        "real": True
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Erro {response.status}: {error}")
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao adicionar tags: {e}")
            return {
                "success": False,
                "message": f"Erro ao adicionar tags: {e}"
            }
        
        # CÓDIGO ORIGINAL COMENTADO - CAUSAVA ERRO 404
        # if not self.is_initialized:
        #     await self.initialize()
        # 
        # try:
        #     # Preparar dados das tags
        #     tags_data = {
        #         "_embedded": {
        #             "tags": [{"name": tag} for tag in tags]
        #         }
        #     }
        #     
        #     # Adicionar tags ao lead
        #     async with self.session.post(
        #         f"{self.base_url}/api/v4/leads/{lead_id}/tags",
        #         headers=self.headers,
        #         json=tags_data
        #     ) as response:
        #         if response.status in [200, 201, 202]:
        #             emoji_logger.crm_event(
        #                 f"🏷️ Tags adicionadas ao lead {lead_id}: {', '.join(tags)}"
        #             )
        #             return {
        #                 "success": True,
        #                 "message": f"Tags adicionadas: {', '.join(tags)}",
        #                 "tags": tags,
        #                 "real": True
        #             }
        #         else:
        #             error = await response.text()
        #             raise Exception(f"Erro {response.status}: {error}")
        #             
        # except Exception as e:
        #     emoji_logger.service_error(f"Erro ao adicionar tags: {e}")
        #     return {
        #         "success": False,
        #         "message": f"Erro ao adicionar tags: {e}"
        #     }
    
    @async_retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def update_fields(self, lead_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza campos customizados do lead de forma DINÂMICA
        ZERO complexidade, MÁXIMA flexibilidade
        
        Args:
            lead_id: ID do lead no Kommo
            fields: Dict com campos a atualizar (usa nomes amigáveis)
                   Ex: {"bill_value": "500", "solution_type": "Usina própria"}
        
        Returns:
            Dict com resultado da operação
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Preparar campos customizados
            custom_fields_values = []
            
            # Mapear campos conhecidos (usar campos da inicialização ou padrões)
            # SIMPLES: Usa apenas campos confirmados como válidos
            field_mapping = {}
            
            # Adicionar campos do self.custom_fields que existem
            for field_name, field_id in self.custom_fields.items():
                if field_id:  # Apenas campos com ID válido
                    field_mapping[field_name] = field_id
            
            # Aliases adicionais para campos conhecidos
            if self.custom_fields.get("phone"):
                field_mapping["whatsapp"] = self.custom_fields["phone"]
                field_mapping["telefone"] = self.custom_fields["phone"]
            
            if self.custom_fields.get("bill_value"):
                field_mapping["valor_conta"] = self.custom_fields["bill_value"]
                field_mapping["conta_energia"] = self.custom_fields["bill_value"]
            
            if self.custom_fields.get("solution_type"):
                field_mapping["solucao_solar"] = self.custom_fields["solution_type"]
                field_mapping["solução_solar"] = self.custom_fields["solution_type"]
            
            if self.custom_fields.get("calendar_link"):
                field_mapping["google_calendar"] = self.custom_fields["calendar_link"]
                field_mapping["link_calendario"] = self.custom_fields["calendar_link"]
            
            # Adicionar campos ao payload
            for field_name, field_value in fields.items():
                field_name_lower = field_name.lower()
                
                # Procurar ID do campo
                field_id = field_mapping.get(field_name_lower)
                
                if field_id:
                    # Verificar se é o campo SELECT solution_type (ID: 392808)
                    if field_id == 392808:
                        # Para campos SELECT, usar enum_id
                        solution_text = str(field_value).lower()
                        enum_id = self.solution_type_values.get(solution_text)
                        
                        if enum_id:
                            custom_fields_values.append({
                                "field_id": field_id,
                                "values": [{"enum_id": enum_id}]  # Usar enum_id para SELECT
                            })
                            emoji_logger.system_debug(f"Campo SELECT {field_name}: enum_id {enum_id}")
                        else:
                            emoji_logger.service_warning(
                                f"Valor '{field_value}' inválido para Solução Solar. "
                                f"Use: {list(self.solution_type_values.keys())}"
                            )
                    else:
                        # Campos TEXT, NUMERIC, URL - usar value
                        custom_fields_values.append({
                            "field_id": field_id,
                            "values": [{"value": str(field_value)}]
                        })
                        emoji_logger.system_debug(f"Campo {field_name} (ID {field_id}): {field_value}")
                else:
                    emoji_logger.service_warning(f"Campo '{field_name}' não mapeado, ignorando")
            
            # Se não há campos para atualizar, retornar sucesso
            if not custom_fields_values:
                return {
                    "success": True,
                    "message": "Nenhum campo válido para atualizar",
                    "real": True
                }
            
            # Atualizar no Kommo
            update_data = {
                "custom_fields_values": custom_fields_values
            }
            
            async with self.session.patch(
                f"{self.base_url}/api/v4/leads/{lead_id}",
                headers=self.headers,
                json=update_data
            ) as response:
                if response.status in [200, 202]:
                    emoji_logger.crm_event(
                        f"✅ Campos atualizados no lead {lead_id}: {list(fields.keys())}"
                    )
                    return {
                        "success": True,
                        "message": f"Campos atualizados com sucesso",
                        "fields_updated": list(fields.keys()),
                        "real": True
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Erro {response.status}: {error}")
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao atualizar campos: {e}")
            return {
                "success": False,
                "message": f"Erro ao atualizar campos: {e}"
            }
    
    async def create_or_update_lead_direct(self, lead_data: Dict[str, Any], tags: List[str] = None) -> Dict[str, Any]:
        """
        Método direto para criar/atualizar lead sem decorators - usado pelo auto sync
        🔥 FIX: Passando tags diretamente para create_or_update_lead
        
        Args:
            lead_data: Dados do lead
            tags: Lista de tags
            
        Returns:
            Dict com resultado da operação incluindo crm_id
        """
        try:
            # 🔥 FIX: Passar tags diretamente no método create_or_update_lead
            result = await self.create_or_update_lead(lead_data, tags)
            
            if result.get("success"):
                # Log das tags adicionadas
                if tags:
                    emoji_logger.crm_event(
                        f"🏷️ Tags adicionadas ao lead {result.get('lead_id')}: {', '.join(tags)}"
                    )
                
                # Reformatar resposta para compatibilidade com auto sync
                return {
                    "success": True,
                    "crm_id": result.get("lead_id"),  # Campo esperado pelo auto sync
                    "lead_id": result.get("lead_id"),
                    "action": result.get("action", "processed"),
                    "message": result.get("message", "Lead processado com sucesso"),
                    "real": True
                }
            else:
                return result
                
        except Exception as e:
            emoji_logger.service_error(f"Erro em create_or_update_lead_direct: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_custom_fields(self, lead_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza campos customizados dinamicamente
        
        Args:
            lead_id: ID do lead
            fields: Dicionário com campos a atualizar {nome_campo: valor}
            
        Returns:
            Dict com resultado da operação
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Preparar campos customizados
            custom_fields_values = []
            
            # Mapear campos por nome amigável
            field_name_mapping = {
                "telefone": "phone",
                "phone": "phone",
                "email": "email",
                "e-mail": "email",
                "valor_conta": "bill_value",
                "bill_value": "bill_value",
                "valor": "bill_value",
                "localizacao": "location",
                "location": "location",
                "endereco": "location",
                "tipo_propriedade": "property_type",
                "property_type": "property_type",
                "tipo": "property_type"
            }
            
            # Processar cada campo
            for field_name, value in fields.items():
                # Normalizar nome do campo
                normalized_name = field_name.lower().replace(" ", "_")
                
                # Tentar mapear para campo conhecido
                mapped_name = field_name_mapping.get(normalized_name, normalized_name)
                
                # Se temos o ID do campo, adicionar
                if mapped_name in self.custom_fields:
                    field_id = self.custom_fields[mapped_name]
                    custom_fields_values.append({
                        "field_id": field_id,
                        "values": [{"value": str(value)}]
                    })
                    emoji_logger.system_debug(f"Campo {field_name} ({mapped_name}) -> ID {field_id} = {value}")
                else:
                    emoji_logger.service_warning(f"Campo desconhecido: {field_name}")
            
            # Se há campos para atualizar
            if custom_fields_values:
                update_data = {
                    "custom_fields_values": custom_fields_values
                }
                
                async with self.session.patch(
                    f"{self.base_url}/api/v4/leads/{lead_id}",
                    headers=self.headers,
                    json=update_data
                ) as response:
                    if response.status in [200, 202]:
                        emoji_logger.crm_event(
                            f"📝 Campos customizados atualizados no lead {lead_id}"
                        )
                        return {
                            "success": True,
                            "message": f"Atualizados {len(custom_fields_values)} campos",
                            "fields_updated": list(fields.keys()),
                            "real": True
                        }
                    else:
                        error = await response.text()
                        raise Exception(f"Erro {response.status}: {error}")
            else:
                return {
                    "success": False,
                    "message": "Nenhum campo válido para atualizar"
                }
                
        except Exception as e:
            emoji_logger.service_error(f"Erro ao atualizar campos: {e}")
            return {
                "success": False,
                "message": f"Erro ao atualizar campos: {e}"
            }
    
    async def health_check(self) -> bool:
        """Verifica saúde do serviço"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Testar acesso à API
            async with self.session.get(
                f"{self.base_url}/api/v4/account",
                headers=self.headers
            ) as response:
                return response.status == 200
                
        except:
            return False
    
    async def close(self):
        """Fecha conexões de forma segura"""
        await self._close_session_safely()
    
    async def _close_session_safely(self):
        """🛡️ Fecha sessão aiohttp de forma segura"""
        if self.session and not self.session.closed:
            try:
                await self.session.close()
                # Aguardar um pouco para garantir que conexões sejam fechadas
                await asyncio.sleep(0.1)
                emoji_logger.service_info("🔌 Sessão CRM fechada com segurança")
            except Exception as e:
                emoji_logger.service_warning(f"Aviso ao fechar sessão CRM: {e}")
            finally:
                self.session = None
    
    def __del__(self):
        """🗑️ Destrutor para garantir limpeza de recursos"""
        if self.session and not self.session.closed:
            # Criar nova task para fechar sessão se event loop estiver rodando
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._close_session_safely())
                else:
                    loop.run_until_complete(self._close_session_safely())
            except RuntimeError:
                # Event loop não disponível - criar novo loop para fechamento
                try:
                    if hasattr(self.session, '_connector') and self.session._connector:
                        # Criar novo loop temporário para fechamento limpo
                        temp_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(temp_loop)
                        temp_loop.run_until_complete(self._close_session_safely())
                        temp_loop.close()
                except:
                    pass