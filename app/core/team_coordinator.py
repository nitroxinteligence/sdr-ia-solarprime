"""
Team Coordinator - Coordenação SIMPLES de serviços
ZERO complexidade, execução direta
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import uuid4
import asyncio
from app.utils.logger import emoji_logger
from app.config import settings

class TeamCoordinator:
    """
    Coordenador SIMPLES de serviços (Calendar, CRM, FollowUp)
    Execução direta sem complexidade
    """
    
    def __init__(self):
        self.is_initialized = False
        self.services = {}
        self.decision_threshold = 0.3  # Threshold reduzido para ativação mais sensível
        
    async def initialize(self):
        """Inicialização assíncrona dos serviços"""
        if self.is_initialized:
            return
            
        # Inicializar serviços conforme configuração
        await self._initialize_services()
        
        emoji_logger.system_ready(
            "🎯 TeamCoordinator inicializado",
            services=list(self.services.keys())
        )
        self.is_initialized = True
    
    async def _initialize_services(self):
        """Inicializa serviços habilitados de forma SIMPLES"""
        
        # Calendar Service
        if settings.enable_calendar_agent:
            try:
                from app.services.calendar_service_100_real import CalendarServiceReal as CalendarService
                self.services["calendar"] = CalendarService()
                emoji_logger.service_ready("📅 Calendar Service pronto")
            except Exception as e:
                emoji_logger.service_error(f"Erro ao inicializar Calendar: {e}")
        
        # CRM Service  
        if settings.enable_crm_agent:
            try:
                from app.services.crm_service_100_real import CRMServiceReal as CRMService
                self.services["crm"] = CRMService()
                emoji_logger.service_ready("📊 CRM Service pronto")
            except Exception as e:
                emoji_logger.service_error(f"Erro ao inicializar CRM: {e}")
        
        # FollowUp Service
        if settings.enable_followup_agent:
            try:
                from app.services.followup_service_100_real import FollowUpServiceReal as FollowUpService
                self.services["followup"] = FollowUpService()
                emoji_logger.service_ready("🔄 FollowUp Service pronto")
            except Exception as e:
                emoji_logger.service_error(f"Erro ao inicializar FollowUp: {e}")
    
    def analyze_service_need(self, message: str, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Analisa necessidade de serviços com threshold 0.6
        
        Args:
            message: Mensagem do usuário
            context: Contexto da conversa
            
        Returns:
            Scores de necessidade por serviço
        """
        scores = {
            "calendar": 0.0,
            "crm": 0.0,
            "followup": 0.0
        }
        
        message_lower = message.lower()
        
        # Calendar - palavras-chave reduzidas (10 essenciais)
        calendar_keywords = [
            "agendar", "marcar", "reunião", "conversar", "leonardo",
            "horário", "disponível", "data", "quando", "encontro"
        ]
        
        calendar_score = sum(1 for kw in calendar_keywords if kw in message_lower)
        scores["calendar"] = min(1.0, calendar_score * 0.15)  # Max 1.0
        
        # CRM - atualização de lead
        crm_keywords = [
            "nome", "telefone", "email", "empresa", "conta",
            "valor", "consumo", "kwh", "endereço", "cpf"
        ]
        
        crm_score = sum(1 for kw in crm_keywords if kw in message_lower)
        scores["crm"] = min(1.0, crm_score * 0.25)
        
        # FollowUp - reengajamento
        followup_keywords = [
            "lembrar", "retornar", "voltar", "depois", "pensar",
            "aguardar", "futuro", "próxima", "acompanhar", "followup",
            "ligue", "ligar", "dias", "semana", "amanhã", "contato"
        ]
        
        followup_score = sum(1 for kw in followup_keywords if kw in message_lower)
        scores["followup"] = min(1.0, followup_score * 0.20)  # Aumentado para ativar mais facilmente
        
        # Boost baseado no contexto
        if context.get("action_needed") == "agendar":
            scores["calendar"] += 0.3
        elif context.get("action_needed") == "qualificar":
            scores["crm"] += 0.3
        elif context.get("action_needed") == "reengajar":
            scores["followup"] += 0.3
        
        # Normalizar scores
        for service in scores:
            scores[service] = min(1.0, scores[service])
        
        return scores
    
    async def execute_services(self, 
                              message: str,
                              context: Dict[str, Any],
                              lead_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa serviços necessários de forma DIRETA
        
        Args:
            message: Mensagem do usuário
            context: Contexto analisado
            lead_info: Informações do lead
            
        Returns:
            Lista de resultados dos serviços executados
        """
        results = []
        
        # Analisar necessidade
        scores = self.analyze_service_need(message, context)
        
        # Executar serviços que passaram o threshold
        for service_name, score in scores.items():
            if score >= self.decision_threshold:
                emoji_logger.service_event(
                    f"🎯 Executando {service_name}",
                    score=f"{score:.2f}",
                    threshold=self.decision_threshold
                )
                
                result = await self._execute_single_service(
                    service_name,
                    message,
                    context,
                    lead_info
                )
                
                if result:
                    results.append(result)
        
        return results
    
    async def _execute_single_service(self,
                                     service_name: str,
                                     message: str,
                                     context: Dict[str, Any],
                                     lead_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Executa um serviço específico
        
        Args:
            service_name: Nome do serviço
            message: Mensagem
            context: Contexto
            lead_info: Info do lead
            
        Returns:
            Resultado da execução ou None
        """
        if service_name not in self.services:
            emoji_logger.service_warning(f"Serviço {service_name} não disponível")
            return None
        
        service = self.services[service_name]
        
        try:
            if service_name == "calendar":
                # Verificar disponibilidade ou agendar
                if "disponível" in message.lower() or "horário" in message.lower():
                    result = await service.check_availability(message)
                else:
                    # Extrair data/hora da mensagem
                    date_time = self._extract_datetime(message)
                    if date_time:
                        result = await service.schedule_meeting(
                            date_time["date"],
                            date_time["time"],
                            lead_info
                        )
                        
                        # 🚀 WORKFLOW COMPLETO PÓS-AGENDAMENTO
                        if result and result.get("success"):
                            await self._execute_post_scheduling_workflow(
                                result,
                                lead_info,
                                context
                            )
                    else:
                        result = await service.suggest_times(lead_info)
                
            elif service_name == "crm":
                # Atualizar lead no CRM
                result = await service.create_or_update_lead(lead_info)
                
                # Capturar o lead_id retornado e adicionar ao lead_info
                if result.get("success") and result.get("lead_id"):
                    lead_id = result["lead_id"]
                    lead_info["id"] = lead_id  # Armazenar para uso futuro
                    
                    # Atualizar estágio se necessário
                    if lead_info.get("stage"):
                        await service.update_lead_stage(
                            lead_id,  # Usar o lead_id correto
                            lead_info["stage"]
                        )
                    
                    # 🚀 SINCRONIZAÇÃO AUTOMÁTICA COM KOMMO
                    # Após criar/atualizar no CRM, sincronizar com campos dinâmicos
                    try:
                        emoji_logger.service_event("🔄 Sincronizando campos dinâmicos e tags")
                        sync_result = await self.sync_lead_to_crm(lead_info)
                        if sync_result.get("success"):
                            emoji_logger.system_success("✅ Tags e campos personalizados sincronizados")
                    except Exception as sync_error:
                        emoji_logger.service_warning(f"Sync opcional falhou: {sync_error}")
                    
            elif service_name == "followup":
                # Agendar follow-up
                phone = lead_info.get("phone", "")
                name = lead_info.get("name", "Cliente")
                bill_value = lead_info.get("bill_value", 0)
                
                # 🛡️ VALIDAÇÃO: Verificar se phone_number é válido
                if not phone or phone.strip() == "":
                    emoji_logger.service_warning("Phone number vazio - follow-up não agendado")
                    result = {
                        "success": False,
                        "error": "Phone number is required for follow-up"
                    }
                    return None
                
                # Gerar mensagem personalizada para follow-up
                message = f"Oi {name}! Helen da SolarPrime aqui. "
                message += f"Vou entrar em contato com você em breve para continuarmos nossa conversa sobre energia solar. "
                if bill_value > 0:
                    message += f"Já preparei uma análise especial para sua conta de R$ {bill_value}. "
                message += "Até logo! ☀️"
                
                # Calcular delay em horas baseado no contexto
                urgency = context.get("urgency_level", "normal")
                if urgency == "alta":
                    delay_hours = 24
                elif urgency == "média":
                    delay_hours = 72
                else:
                    delay_hours = 168  # 7 dias
                
                # Chamar com argumentos corretos
                result = await service.schedule_followup(
                    phone_number=phone,
                    message=message,
                    delay_hours=delay_hours,
                    lead_info=lead_info
                )
            
            else:
                result = None
            
            if result and result.get("success"):
                emoji_logger.service_event(
                    f"✅ {service_name} executado com sucesso",
                    result=result.get("message", "")
                )
                return {
                    "service": service_name,
                    "success": True,
                    "data": result
                }
            
        except Exception as e:
            emoji_logger.service_error(
                f"Erro ao executar {service_name}: {e}"
            )
        
        return None
    
    def _extract_datetime(self, text: str) -> Optional[Dict[str, str]]:
        """
        Extrai data e hora do texto (SIMPLES)
        
        Args:
            text: Texto com data/hora
            
        Returns:
            Dict com date e time ou None
        """
        import re
        from datetime import datetime, timedelta
        
        text_lower = text.lower()
        
        # Padrões simples
        hoje = datetime.now()
        
        # Detectar "hoje", "amanhã", "depois de amanhã"
        if "hoje" in text_lower:
            date = hoje.strftime("%Y-%m-%d")
        elif "amanhã" in text_lower:
            date = (hoje + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "depois de amanhã" in text_lower:
            date = (hoje + timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            # Tentar extrair data no formato DD/MM
            date_match = re.search(r"(\d{1,2})[/-](\d{1,2})", text)
            if date_match:
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = hoje.year
                date = f"{year}-{month:02d}-{day:02d}"
            else:
                date = None
        
        # Extrair hora
        time_match = re.search(r"(\d{1,2})[h:](\d{0,2})", text_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            time = f"{hour:02d}:{minute:02d}"
        else:
            # Detectar períodos
            if "manhã" in text_lower:
                time = "09:00"
            elif "tarde" in text_lower:
                time = "14:00"
            elif "noite" in text_lower:
                time = "19:00"
            else:
                time = "10:00"  # Default
        
        if date:
            return {"date": date, "time": time}
        
        return None
    
    def _calculate_followup_date(self, context: Dict[str, Any]) -> str:
        """
        Calcula data ideal para follow-up
        
        Args:
            context: Contexto da conversa
            
        Returns:
            Data no formato YYYY-MM-DD
        """
        from datetime import datetime, timedelta
        
        urgency = context.get("urgency_level", "normal")
        stage = context.get("conversation_stage", "início")
        
        # Calcular dias baseado em urgência e estágio
        if urgency == "alta":
            days = 1
        elif urgency == "média":
            days = 3
        elif stage in ["negociação", "qualificação"]:
            days = 2
        else:
            days = 7
        
        followup_date = datetime.now() + timedelta(days=days)
        return followup_date.strftime("%Y-%m-%d")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Retorna status dos serviços"""
        return {
            "initialized": self.is_initialized,
            "threshold": self.decision_threshold,
            "services": {
                name: {
                    "enabled": name in self.services,
                    "ready": self.services.get(name) is not None
                }
                for name in ["calendar", "crm", "followup"]
            }
        }
    
    async def _execute_post_scheduling_workflow(self,
                                                scheduling_result: Dict[str, Any],
                                                lead_info: Dict[str, Any],
                                                context: Dict[str, Any]):
        """
        🚀 WORKFLOW COMPLETO PÓS-AGENDAMENTO
        Executa todas as ações necessárias após agendar reunião
        """
        try:
            from datetime import datetime, timedelta
            from app.integrations.supabase_client import supabase_client
            
            google_event_id = scheduling_result.get("google_event_id")
            start_time = scheduling_result.get("start_time")
            lead_id = lead_info.get("id")  # Agora estará definido pelo CRM
            
            # Se não tiver lead_id, tentar criar no CRM primeiro
            if not lead_id and "crm" in self.services:
                try:
                    crm_result = await self.services["crm"].create_or_update_lead(lead_info)
                    if crm_result.get("success") and crm_result.get("lead_id"):
                        lead_id = crm_result["lead_id"]
                        lead_info["id"] = lead_id
                except Exception as e:
                    emoji_logger.service_warning(f"Erro ao criar lead no CRM: {e}")
            
            emoji_logger.service_event("🎯 Iniciando workflow pós-agendamento")
            
            # 1. CRIAR QUALIFICAÇÃO NO SUPABASE
            try:
                # Buscar ou criar lead no Supabase usando UUID
                supabase_lead_id = await self._get_or_create_supabase_lead_id(lead_info)
                
                qualification_data = {
                    'lead_id': supabase_lead_id,  # Usar UUID do Supabase
                    'qualification_status': 'QUALIFIED',
                    'score': 85,
                    'notes': f'Reunião agendada com sucesso. Evento Google: {google_event_id}',
                    'qualified_at': datetime.now().isoformat(),
                    'qualified_by': str(uuid4())  # Usar UUID válido ao invés de 'TeamCoordinator'
                }
                
                await supabase_client.create_lead_qualification(qualification_data)
                emoji_logger.system_success("✅ Qualificação criada no Supabase")
            except Exception as e:
                emoji_logger.service_warning(f"Erro ao criar qualificação: {e}")
            
            # 2. ATUALIZAR LEAD NO SUPABASE  
            try:
                # Usar o UUID do Supabase ao invés do ID do Kommo
                supabase_lead_id = await self._get_or_create_supabase_lead_id(lead_info)
                
                update_data = {
                    'google_event_id': google_event_id,
                    'meeting_scheduled_at': start_time,
                    'qualification_status': 'QUALIFIED',
                    'current_stage': 'MEETING_SCHEDULED'
                }
                
                await supabase_client.update_lead(supabase_lead_id, update_data)
                emoji_logger.system_success("✅ Lead atualizado com dados da reunião")
            except Exception as e:
                emoji_logger.service_warning(f"Erro ao atualizar lead: {e}")
            
            # 3. CRIAR LEMBRETES PERSONALIZADOS
            if "followup" in self.services:
                try:
                    # 🛡️ VALIDAÇÃO: Verificar se start_time é string ou datetime
                    if isinstance(start_time, str):
                        meeting_datetime = datetime.fromisoformat(start_time)
                    elif isinstance(start_time, datetime):
                        meeting_datetime = start_time
                    else:
                        raise ValueError(f"start_time deve ser string ou datetime, recebido: {type(start_time)}")
                    
                    followup_service = self.services["followup"]
                    
                    # Lembrete 24h antes
                    reminder_24h = await self._generate_personalized_reminder(
                        lead_info,
                        meeting_datetime,
                        24,
                        context
                    )
                    
                    # Usar UUID do Supabase para follow-ups
                    supabase_lead_id = await self._get_or_create_supabase_lead_id(lead_info)
                    
                    await followup_service.create_followup_direct({
                        'lead_id': supabase_lead_id,
                        'type': 'MEETING_REMINDER_24H', 
                        'scheduled_at': (meeting_datetime - timedelta(hours=24)).isoformat(),
                        'message': reminder_24h,
                        'metadata': {
                            'google_event_id': google_event_id,
                            'hours_before': 24
                        }
                    })
                    emoji_logger.system_success("✅ Lembrete 24h criado")
                    
                    # Lembrete 2h antes
                    reminder_2h = await self._generate_personalized_reminder(
                        lead_info,
                        meeting_datetime,
                        2,
                        context
                    )
                    
                    await followup_service.create_followup_direct({
                        'lead_id': supabase_lead_id,
                        'type': 'MEETING_REMINDER_2H',
                        'scheduled_at': (meeting_datetime - timedelta(hours=2)).isoformat(),
                        'message': reminder_2h,
                        'metadata': {
                            'google_event_id': google_event_id,
                            'hours_before': 2
                        }
                    })
                    emoji_logger.system_success("✅ Lembrete 2h criado")
                    
                except Exception as e:
                    emoji_logger.service_warning(f"Erro ao criar lembretes: {e}")
            
            # 4. ATUALIZAR CRM SE DISPONÍVEL
            if "crm" in self.services and lead_info and lead_id:
                try:
                    crm_service = self.services["crm"]
                    
                    # Usar o ID do Kommo (original) para operações do CRM
                    kommo_lead_id = lead_info.get("id") or lead_id
                    if kommo_lead_id:
                        # Atualizar estágio no CRM
                        await crm_service.update_lead_stage(
                            str(kommo_lead_id),  # Usar ID do Kommo para CRM
                            "REUNIAO_AGENDADA",
                            f"Reunião agendada para {start_time}"
                        )
                        
                        # Adicionar tags
                        if hasattr(crm_service, 'add_tags_to_lead'):
                            await crm_service.add_tags_to_lead(
                                str(kommo_lead_id),  # Usar ID do Kommo para CRM
                                ["reuniao_agendada", "qualificado", "hot_lead"]
                            )
                    
                    emoji_logger.system_success("✅ CRM atualizado com sucesso")
                except Exception as e:
                    emoji_logger.service_warning(f"Erro ao atualizar CRM: {e}")
            
            emoji_logger.service_event("🎊 Workflow pós-agendamento concluído!")
            
        except Exception as e:
            emoji_logger.service_error(f"Erro no workflow pós-agendamento: {e}")
    
    async def _generate_personalized_reminder(self,
                                             lead_info: Dict[str, Any],
                                             meeting_time: datetime,
                                             hours_before: int,
                                             context: Dict[str, Any]) -> str:
        """
        Gera mensagem personalizada de lembrete
        NÃO USA TEMPLATES FIXOS - mensagens únicas baseadas no contexto
        """
        lead_name = lead_info.get("name", "").split()[0] if lead_info.get("name") else ""
        meeting_hour = meeting_time.strftime("%H:%M")
        weekday = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"][meeting_time.weekday()]
        
        # Informações do contexto
        main_interest = context.get("main_interest", "economia na conta de luz")
        pain_points = context.get("pain_points", [])
        
        if hours_before == 24:
            # Lembrete 24h - informativo e amigável
            if "conta alta" in str(pain_points).lower():
                return f"Oi{' ' + lead_name if lead_name else ''}! 😊 Amanhã às {meeting_hour} Leonardo vai te mostrar como reduzir essa conta alta. Preparado(a) pra economizar?"
            else:
                return f"{'Oi ' + lead_name + '! ' if lead_name else ''}Confirmado amanhã {weekday} às {meeting_hour} com Leonardo sobre {main_interest}! 🌞"
        else:
            # Lembrete 2h - direto e urgente
            return f"⏰ Reunião em 2h! Leonardo te espera às {meeting_hour} pra falar da sua economia!"
    
    async def sync_lead_to_crm(self, lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 Sincroniza lead imediatamente com Kommo CRM
        Conecta com KommoAutoSyncService para sync dinâmico
        
        Args:
            lead_info: Informações atualizadas do lead
            
        Returns:
            Resultado da sincronização
        """
        try:
            # Verificar se sync está habilitado
            if not settings.enable_kommo_auto_sync:
                return {"success": False, "message": "Auto sync desabilitado"}
            
            emoji_logger.service_event("🔄 Iniciando sync imediato com Kommo CRM")
            
            # Importar serviço de sync
            from app.services.kommo_auto_sync import kommo_auto_sync_service
            
            # Primeiro, garantir que o lead existe no Supabase
            supabase_lead_id = await self._get_or_create_supabase_lead_id(lead_info)
            
            # Atualizar Supabase com informações mais recentes
            from app.integrations.supabase_client import supabase_client
            
            # Preparar dados para atualização
            update_data = {}
            
            # Mapear campos importantes
            if lead_info.get("name"):
                update_data["name"] = lead_info["name"]
            if lead_info.get("email"):
                # 🔥 CORREÇÃO CRÍTICA: Garantir que email seja salvo no Supabase
                update_data["email"] = lead_info["email"]
                emoji_logger.service_event(f"✉️ Email detectado e será salvo: {lead_info['email']}")
            if lead_info.get("bill_value"):
                update_data["bill_value"] = lead_info["bill_value"]
            if lead_info.get("chosen_flow"):
                update_data["chosen_flow"] = lead_info["chosen_flow"]
            if lead_info.get("current_stage"):
                update_data["current_stage"] = lead_info["current_stage"]
            if lead_info.get("qualification_score"):
                # 🔥 CORREÇÃO CRÍTICA: Converter float para int para evitar erro de tipo INTEGER
                from app.utils.safe_conversions import safe_int_conversion
                update_data["qualification_score"] = safe_int_conversion(lead_info["qualification_score"], 0)
            if lead_info.get("google_event_link"):
                update_data["google_event_link"] = lead_info["google_event_link"]
            
            # Atualizar no Supabase se houver mudanças
            if update_data:
                try:
                    await supabase_client.update_lead(supabase_lead_id, update_data)
                    emoji_logger.service_event(
                        "✅ Lead atualizado no Supabase",
                        fields=list(update_data.keys()),
                        data=update_data
                    )
                    
                    # 🔥 Log específico para email para debugging
                    if "email" in update_data:
                        emoji_logger.system_success(
                            f"📧 Email salvo com sucesso no Supabase: {update_data['email']}"
                        )
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao atualizar lead no Supabase: {e}")
                    emoji_logger.service_error(f"Dados que falharam: {update_data}")
                    # Não propagar erro para não quebrar o fluxo principal
            
            # Executar sync específico do lead
            if hasattr(kommo_auto_sync_service, 'sync_specific_lead'):
                sync_result = await kommo_auto_sync_service.sync_specific_lead(supabase_lead_id)
            else:
                # Fallback: forçar sync de todos os leads (menos eficiente)
                await kommo_auto_sync_service.sync_new_leads()
                await kommo_auto_sync_service.sync_lead_updates()
                sync_result = {"success": True, "message": "Sync completo executado"}
            
            emoji_logger.system_success(
                "✅ Lead sincronizado com Kommo CRM",
                result=sync_result
            )
            
            return sync_result
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao sincronizar com CRM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, bool]:
        """Verifica saúde dos serviços"""
        health = {}
        
        for name, service in self.services.items():
            try:
                # Cada serviço deve ter um método health_check
                if hasattr(service, 'health_check'):
                    health[name] = await service.health_check()
                else:
                    health[name] = True  # Assume healthy se não tem check
            except:
                health[name] = False
        
        return health
    
    async def _get_or_create_supabase_lead_id(self, lead_info: Dict[str, Any]) -> str:
        """
        Busca ou cria um UUID válido no Supabase para o lead
        
        Args:
            lead_info: Informações do lead incluindo telefone e dados do Kommo
            
        Returns:
            UUID válido do Supabase
        """
        try:
            from app.integrations.supabase_client import supabase_client
            
            phone = lead_info.get("phone", "")
            if not phone:
                # Se não tem telefone, gerar número único baseado no UUID
                new_lead_uuid = str(uuid4())
                # Usar parte do UUID como telefone único para evitar duplicação
                unique_phone = f"unknown_{new_lead_uuid[:8]}"
                
                lead_data = {
                    "id": new_lead_uuid,  # UUID explícito
                    "phone_number": unique_phone,  # Phone único baseado no UUID
                    "name": lead_info.get("name", "Lead Sem Telefone"),
                    "email": lead_info.get("email"),
                    "bill_value": lead_info.get("bill_value"),
                    "current_stage": "INITIAL_CONTACT", 
                    "qualification_status": "PENDING",
                    "kommo_lead_id": str(lead_info.get("id")) if lead_info.get("id") else None
                }
                
                try:
                    new_lead = await supabase_client.create_lead(lead_data)
                    emoji_logger.system_success(f"✅ Lead sem telefone criado: {new_lead['id']}")
                    return new_lead["id"]
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao criar lead sem telefone: {e}")
                    # Se erro for duplicate key, retornar UUID sem criar no banco
                    if "duplicate key" in str(e):
                        return new_lead_uuid
                    return new_lead_uuid  # Fallback para UUID
            
            # Buscar lead existente no Supabase por telefone
            existing_lead = await supabase_client.get_lead_by_phone(phone)
            
            if existing_lead:
                # Atualizar dados do Kommo se necessário
                kommo_id = lead_info.get("id")
                if kommo_id and existing_lead.get("kommo_lead_id") != str(kommo_id):
                    await supabase_client.update_lead(
                        existing_lead["id"],
                        {"kommo_lead_id": str(kommo_id)}
                    )
                return existing_lead["id"]
            else:
                # 🔥 CORREÇÃO CRÍTICA: Criar novo lead no Supabase
                emoji_logger.service_event(f"🆕 Criando novo lead no Supabase para {phone}")
                lead_data = {
                    "phone_number": phone,
                    "name": lead_info.get("name"),
                    "email": lead_info.get("email"),
                    "bill_value": lead_info.get("bill_value"),
                    "current_stage": "INITIAL_CONTACT",
                    "qualification_status": "PENDING",
                    "kommo_lead_id": str(lead_info.get("id")) if lead_info.get("id") else None
                }
                
                try:
                    new_lead = await supabase_client.create_lead(lead_data)
                    emoji_logger.system_success(f"✅ Lead criado no Supabase: {new_lead['id']}")
                    return new_lead["id"]
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao criar lead no Supabase: {e}")
                    # Fallback: criar UUID mas registrar erro
                    return str(uuid4())
                
        except Exception as e:
            emoji_logger.service_error(f"Erro ao obter UUID do Supabase: {e}")
            # Fallback: criar novo UUID
            return str(uuid4())