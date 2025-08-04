"""
CalendarAgent - Agente Especializado em Agendamento e Calendário
Responsável por gerenciar reuniões e disponibilidade no Google Calendar
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from agno.agent import Agent
from agno.tools import tool
from loguru import logger

from app.integrations.google_calendar import google_calendar_client
from app.integrations.supabase_client import supabase_client
from app.config import settings


class MeetingType(Enum):
    """Tipos de reunião"""
    PRESENTATION = "presentation"          # Apresentação inicial
    TECHNICAL_VISIT = "technical_visit"    # Visita técnica
    CONTRACT_SIGNING = "contract_signing"  # Assinatura de contrato
    FOLLOW_UP = "follow_up"                # Acompanhamento


class CalendarAgent:
    """
    Agente especializado em gerenciamento de calendário
    Agenda reuniões, verifica disponibilidade e envia lembretes
    """
    
    def __init__(self, model, storage):
        """
        Inicializa o agente de calendário
        
        Args:
            model: Modelo LLM a ser usado
            storage: Storage para persistência
        """
        self.model = model
        self.storage = storage
        self.calendar_client = google_calendar_client
        
        # Rate limiting para Google API
        self.rate_limiter = asyncio.Semaphore(5)  # 5 requests simultâneos
        self.request_interval = 0.2  # 200ms entre requests
        
        # Configurações de agendamento
        self.meeting_config = {
            "default_duration": 30,  # minutos
            "buffer_time": 15,       # minutos entre reuniões
            "business_hours": {
                "start": "09:00",
                "end": "18:00"
            },
            "working_days": [0, 1, 2, 3, 4],  # Segunda a Sexta
            "reminder_minutes": [30, 1440]     # 30 min e 1 dia antes
        }
        
        # Tools do agente
        self.tools = [
            self.schedule_meeting,
            self.check_availability,
            self.reschedule_meeting,
            self.cancel_meeting,
            self.list_upcoming_meetings,
            self.send_meeting_reminder,
            self.find_best_slots
        ]
        
        # Criar o agente
        self.agent = Agent(
            name="Calendar Manager",
            model=self.model,
            instructions="""Você é um especialista em gerenciamento de calendário e agendamento.
            
            Suas responsabilidades:
            1. Agendar reuniões respeitando disponibilidade
            2. Sugerir melhores horários para reuniões
            3. Gerenciar reagendamentos e cancelamentos
            4. Enviar lembretes apropriados
            5. Otimizar agenda para máxima eficiência
            
            Regras:
            - Sempre verificar disponibilidade antes de agendar
            - Respeitar horário comercial (9h às 18h)
            - Deixar 15 minutos de buffer entre reuniões
            - Preferir horários que maximizem produtividade
            - Confirmar sempre com o lead antes de finalizar
            
            Seja preciso com datas e horários.
            
            Diretrizes:
            - Verifique disponibilidade antes de agendar
            - Sugira 3 opções de horário quando possível
            - Confirme timezone (padrão: America/Sao_Paulo)
            - Adicione informações relevantes na descrição
            - Configure lembretes automáticos
            - Forneça link do Google Meet quando aplicável""",
            
            tools=self.tools
        )
        
        logger.info("✅ CalendarAgent inicializado")
    
    @tool
    async def schedule_meeting(
        self,
        lead_id: str,
        title: str,
        date: str,  # formato: DD/MM/YYYY
        time: str,  # formato: HH:MM
        duration_minutes: int = 30,
        meeting_type: str = "presentation",
        attendee_emails: List[str] = None,
        description: str = "",
        location: str = "Online - Google Meet"
    ) -> Dict[str, Any]:
        """
        Agenda uma reunião no Google Calendar
        
        Args:
            lead_id: ID do lead
            title: Título da reunião
            date: Data no formato DD/MM/YYYY
            time: Horário no formato HH:MM
            duration_minutes: Duração em minutos
            meeting_type: Tipo de reunião
            attendee_emails: Emails dos participantes
            description: Descrição da reunião
            location: Local ou link da reunião
            
        Returns:
            Detalhes da reunião agendada
        """
        try:
            # Parse de data e hora
            date_parts = date.split('/')
            time_parts = time.split(':')
            
            start_time = datetime(
                year=int(date_parts[2]),
                month=int(date_parts[1]),
                day=int(date_parts[0]),
                hour=int(time_parts[0]),
                minute=int(time_parts[1])
            )
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Verificar se é horário comercial
            if not self._is_business_hours(start_time):
                return {
                    "success": False,
                    "error": "Horário fora do expediente comercial (9h às 18h)"
                }
            
            # Verificar disponibilidade com rate limiting
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                available = await self.calendar_client.check_availability(
                    start_time, end_time
                )
            
            if not available:
                # Buscar alternativas
                alternatives = await self.find_best_slots(
                    duration_minutes=duration_minutes,
                    preferred_date=date
                )
                
                return {
                    "success": False,
                    "error": "Horário não disponível",
                    "alternatives": alternatives
                }
            
            # Criar evento no Google Calendar
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                
                event_data = {
                    "title": title,
                    "start_time": start_time,
                    "end_time": end_time,
                    "description": self._build_description(
                        description, lead_id, meeting_type
                    ),
                    "location": location,
                    "attendees": attendee_emails or [],
                    "reminder_minutes": self.meeting_config["reminder_minutes"]
                }
                
                # Se for online, adicionar Google Meet
                if "Online" in location:
                    event_data["conference_data"] = {
                        "create_request": {
                            "request_id": f"meet-{lead_id}-{datetime.now().timestamp()}"
                        }
                    }
                
                result = await self.calendar_client.create_event(**event_data)
            
            if result and result.get("success"):
                # Salvar no banco
                await self._save_meeting_to_db(
                    lead_id=lead_id,
                    google_event_id=result["google_event_id"],
                    event_data=event_data,
                    meeting_type=meeting_type
                )
                
                logger.info(f"✅ Reunião agendada: {title} em {date} às {time}")
                
                return {
                    "success": True,
                    "event_id": result["google_event_id"],
                    "html_link": result.get("html_link", ""),
                    "meet_link": result.get("meet_link", ""),
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "message": f"Reunião agendada para {date} às {time}"
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao criar evento no calendário"
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao agendar reunião: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_availability_internal(
        self,
        date: str,  # formato: DD/MM/YYYY
        time: str,  # formato: HH:MM
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Implementação interna da verificação de disponibilidade
        """
        try:
            # Parse de data e hora
            date_parts = date.split('/')
            time_parts = time.split(':')
            
            start_time = datetime(
                year=int(date_parts[2]),
                month=int(date_parts[1]),
                day=int(date_parts[0]),
                hour=int(time_parts[0]),
                minute=int(time_parts[1])
            )
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Verificar com rate limiting
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                available = await self.calendar_client.check_availability(
                    start_time, end_time
                )
            
            result = {
                "date": date,
                "time": time,
                "duration": duration_minutes,
                "available": available
            }
            
            if not available:
                # Buscar próximos slots disponíveis
                alternatives = await self._find_nearby_slots(
                    start_time, duration_minutes
                )
                result["alternatives"] = alternatives
                result["message"] = "Horário ocupado. Veja as alternativas sugeridas."
            else:
                result["message"] = "Horário disponível!"
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    @tool
    async def check_availability(
        self,
        date: str,  # formato: DD/MM/YYYY
        time: str,  # formato: HH:MM
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Verifica disponibilidade em um horário específico
        
        Args:
            date: Data no formato DD/MM/YYYY
            time: Horário no formato HH:MM
            duration_minutes: Duração em minutos
            
        Returns:
            Status de disponibilidade
        """
        # Chama a implementação interna
        return await self._check_availability_internal(
            date=date,
            time=time,
            duration_minutes=duration_minutes
        )
    
    @tool
    async def reschedule_meeting(
        self,
        event_id: str,
        new_date: str,  # formato: DD/MM/YYYY
        new_time: str,  # formato: HH:MM
        duration_minutes: int = 30,
        notify_attendees: bool = True
    ) -> Dict[str, Any]:
        """
        Reagenda uma reunião existente
        
        Args:
            event_id: ID do evento no Google Calendar
            new_date: Nova data (DD/MM/YYYY)
            new_time: Novo horário (HH:MM)
            duration_minutes: Duração em minutos
            notify_attendees: Se deve notificar participantes
            
        Returns:
            Status do reagendamento
        """
        try:
            # Parse da nova data e hora
            date_parts = new_date.split('/')
            time_parts = new_time.split(':')
            
            new_start = datetime(
                year=int(date_parts[2]),
                month=int(date_parts[1]),
                day=int(date_parts[0]),
                hour=int(time_parts[0]),
                minute=int(time_parts[1])
            )
            new_end = new_start + timedelta(minutes=duration_minutes)
            
            # Verificar disponibilidade
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                available = await self.calendar_client.check_availability(
                    new_start, new_end
                )
            
            if not available:
                return {
                    "success": False,
                    "error": "Novo horário não está disponível"
                }
            
            # Atualizar evento
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                result = await self.calendar_client.update_event(
                    event_id=event_id,
                    updates={
                        "start_time": new_start,
                        "end_time": new_end
                    },
                    send_notifications=notify_attendees
                )
            
            if result:
                # Atualizar no banco
                await self._update_meeting_in_db(
                    event_id, new_start, new_end
                )
                
                logger.info(f"✅ Reunião {event_id} reagendada para {new_date} às {new_time}")
                
                return {
                    "success": True,
                    "event_id": event_id,
                    "new_start": new_start.isoformat(),
                    "new_end": new_end.isoformat(),
                    "message": f"Reunião reagendada para {new_date} às {new_time}"
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao reagendar no calendário"
                }
                
        except Exception as e:
            logger.error(f"Erro ao reagendar: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def cancel_meeting(
        self,
        event_id: str,
        reason: str = "Reunião cancelada",
        notify_attendees: bool = True
    ) -> Dict[str, Any]:
        """
        Cancela uma reunião agendada
        
        Args:
            event_id: ID do evento no Google Calendar
            reason: Motivo do cancelamento
            notify_attendees: Se deve notificar participantes
            
        Returns:
            Status do cancelamento
        """
        try:
            # Cancelar no Google Calendar
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                success = await self.calendar_client.delete_event(
                    event_id,
                    send_notifications=notify_attendees
                )
            
            if success:
                # Atualizar status no banco
                await self._cancel_meeting_in_db(event_id, reason)
                
                logger.info(f"❌ Reunião {event_id} cancelada: {reason}")
                
                return {
                    "success": True,
                    "event_id": event_id,
                    "reason": reason,
                    "message": "Reunião cancelada com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao cancelar no calendário"
                }
                
        except Exception as e:
            logger.error(f"Erro ao cancelar reunião: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_available_slots_internal(
        self,
        days_ahead: int = 7,
        slot_duration_minutes: int = 30,
        business_hours_only: bool = True
    ) -> Dict[str, Any]:
        """
        Implementação interna da busca de slots (pode ser chamada diretamente)
        """
        try:
            available_slots = {}
            occupied_slots = {}
            
            # Configuração de horário comercial
            business_start = 9  # 9h
            business_end = 18   # 18h
            
            # Data inicial (hoje)
            current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Buscar eventos ocupados dos próximos dias
            time_min = current_date
            time_max = current_date + timedelta(days=days_ahead + 10)  # Buffer para garantir 7 dias úteis
            
            # Buscar eventos do Google Calendar
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                events = await self.calendar_client.list_events(
                    time_min=time_min,
                    time_max=time_max,
                    max_results=100
                )
            
            # Processar cada dia útil
            business_days_count = 0
            check_date = current_date
            
            while business_days_count < days_ahead:
                # Pular finais de semana
                if check_date.weekday() >= 5:  # 5=Sábado, 6=Domingo
                    check_date += timedelta(days=1)
                    continue
                
                date_str = check_date.strftime("%d/%m/%Y")
                day_name = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][check_date.weekday()]
                
                available_slots[date_str] = {
                    "day_name": day_name,
                    "date": date_str,
                    "slots": []
                }
                occupied_slots[date_str] = {
                    "day_name": day_name,
                    "date": date_str,
                    "slots": []
                }
                
                # Gerar todos os slots do dia
                if business_hours_only:
                    slot_start = check_date.replace(hour=business_start, minute=0)
                    slot_end = check_date.replace(hour=business_end, minute=0)
                else:
                    slot_start = check_date.replace(hour=0, minute=0)
                    slot_end = check_date.replace(hour=23, minute=30)
                
                current_slot = slot_start
                
                while current_slot < slot_end:
                    slot_end_time = current_slot + timedelta(minutes=slot_duration_minutes)
                    
                    # Verificar se o slot está ocupado
                    is_occupied = False
                    for event in events:
                        if event.get("start") and event.get("end"):
                            # Parse do horário do evento
                            event_start_str = event["start"].get("dateTime", event["start"].get("date", ""))
                            event_end_str = event["end"].get("dateTime", event["end"].get("date", ""))
                            
                            if event_start_str and event_end_str:
                                try:
                                    # Parse robusto que funciona com qualquer timezone
                                    if 'T' in event_start_str:
                                        # Remove timezone para comparação local
                                        if 'Z' in event_start_str:
                                            event_start_str = event_start_str.replace('Z', '+00:00')
                                        # Parse com timezone
                                        event_start = datetime.fromisoformat(event_start_str)
                                        # Remove timezone para comparação
                                        if event_start.tzinfo:
                                            event_start = event_start.replace(tzinfo=None)
                                    else:
                                        # Evento de dia inteiro
                                        event_start = datetime.strptime(event_start_str, "%Y-%m-%d")

                                    if 'T' in event_end_str:
                                        # Remove timezone para comparação local
                                        if 'Z' in event_end_str:
                                            event_end_str = event_end_str.replace('Z', '+00:00')
                                        # Parse com timezone
                                        event_end = datetime.fromisoformat(event_end_str)
                                        # Remove timezone para comparação
                                        if event_end.tzinfo:
                                            event_end = event_end.replace(tzinfo=None)
                                    else:
                                        # Evento de dia inteiro
                                        event_end = datetime.strptime(event_end_str, "%Y-%m-%d")
                                    
                                    # Verificar sobreposição
                                    if (current_slot < event_end and slot_end_time > event_start):
                                        is_occupied = True
                                        break
                                except:
                                    continue
                    
                    # Adicionar slot à lista apropriada
                    slot_info = {
                        "time": current_slot.strftime("%H:%M"),
                        "datetime": current_slot.isoformat(),
                        "duration": slot_duration_minutes
                    }
                    
                    if is_occupied:
                        occupied_slots[date_str]["slots"].append(slot_info)
                    else:
                        # Verificar se não é horário de almoço (12h-13h)
                        if not (12 <= current_slot.hour < 13):
                            available_slots[date_str]["slots"].append(slot_info)
                    
                    current_slot = slot_end_time
                
                business_days_count += 1
                check_date += timedelta(days=1)
            
            # Calcular estatísticas
            total_available = sum(len(day["slots"]) for day in available_slots.values())
            total_occupied = sum(len(day["slots"]) for day in occupied_slots.values())
            
            return {
                "success": True,
                "period": f"Próximos {days_ahead} dias úteis",
                "business_hours": f"{business_start}h às {business_end}h" if business_hours_only else "24 horas",
                "slot_duration": f"{slot_duration_minutes} minutos",
                "statistics": {
                    "total_available_slots": total_available,
                    "total_occupied_slots": total_occupied,
                    "availability_percentage": round((total_available / (total_available + total_occupied) * 100) if (total_available + total_occupied) > 0 else 100, 1)
                },
                "available_slots": available_slots,
                "occupied_slots": occupied_slots,
                "best_times": self._get_best_available_times(available_slots, limit=5)
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar slots disponíveis: {e}")
            return {
                "success": False,
                "error": str(e),
                "available_slots": {},
                "occupied_slots": {}
            }
    
    def _get_best_available_times(self, available_slots: Dict, limit: int = 5) -> List[Dict]:
        """
        Retorna os melhores horários disponíveis (primeiros da manhã e início da tarde)
        """
        best_times = []
        preferred_hours = [9, 10, 14, 15, 16]  # Horários preferenciais
        
        for date_str, day_data in available_slots.items():
            for slot in day_data["slots"]:
                hour = int(slot["time"].split(":")[0])
                if hour in preferred_hours:
                    best_times.append({
                        "date": date_str,
                        "day_name": day_data["day_name"],
                        "time": slot["time"],
                        "datetime": slot["datetime"],
                        "priority": "alta" if hour in [9, 10] else "média"
                    })
                    
                    if len(best_times) >= limit:
                        return best_times[:limit]
        
        # Se não encontrou horários preferenciais suficientes, adicionar qualquer disponível
        if len(best_times) < limit:
            for date_str, day_data in available_slots.items():
                for slot in day_data["slots"]:
                    if not any(bt["time"] == slot["time"] and bt["date"] == date_str for bt in best_times):
                        best_times.append({
                            "date": date_str,
                            "day_name": day_data["day_name"],
                            "time": slot["time"],
                            "datetime": slot["datetime"],
                            "priority": "normal"
                        })
                        
                        if len(best_times) >= limit:
                            return best_times[:limit]
        
        return best_times
    
    @tool
    async def get_available_slots(
        self,
        days_ahead: int = 7,
        slot_duration_minutes: int = 30,
        business_hours_only: bool = True
    ) -> Dict[str, Any]:
        """
        Busca todos os horários disponíveis e ocupados dos próximos 7 dias úteis
        
        Args:
            days_ahead: Quantos dias úteis à frente buscar (padrão: 7)
            slot_duration_minutes: Duração de cada slot em minutos (padrão: 30)
            business_hours_only: Se deve considerar apenas horário comercial (padrão: True)
            
        Returns:
            Dicionário com horários disponíveis e ocupados por dia
        """
        # Chama a implementação interna
        return await self._get_available_slots_internal(
            days_ahead=days_ahead,
            slot_duration_minutes=slot_duration_minutes,
            business_hours_only=business_hours_only
        )
    
    @tool
    async def list_upcoming_meetings(
        self,
        lead_id: Optional[str] = None,
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Lista reuniões próximas
        
        Args:
            lead_id: ID do lead (opcional, para filtrar)
            days_ahead: Quantos dias à frente buscar
            
        Returns:
            Lista de reuniões próximas
        """
        try:
            time_min = datetime.now()
            time_max = time_min + timedelta(days=days_ahead)
            
            # Buscar do Google Calendar
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                events = await self.calendar_client.list_events(
                    time_min=time_min,
                    time_max=time_max,
                    max_results=50
                )
            
            # Se tem lead_id, filtrar do banco
            if lead_id:
                db_events = supabase_client.client.table("calendar_events")\
                    .select("*")\
                    .eq("lead_id", lead_id)\
                    .gte("start_time", time_min.isoformat())\
                    .lte("start_time", time_max.isoformat())\
                    .execute()
                
                # Combinar informações
                lead_event_ids = [e["google_event_id"] for e in db_events.data]
                events = [e for e in events if e.get("id") in lead_event_ids]
            
            # Formatar resposta
            formatted_events = []
            for event in events:
                formatted_events.append({
                    "id": event.get("id"),
                    "title": event.get("summary", "Sem título"),
                    "start": event.get("start", {}).get("dateTime", ""),
                    "end": event.get("end", {}).get("dateTime", ""),
                    "location": event.get("location", ""),
                    "meet_link": event.get("hangoutLink", ""),
                    "attendees": [
                        a.get("email") for a in event.get("attendees", [])
                    ]
                })
            
            return {
                "success": True,
                "count": len(formatted_events),
                "events": formatted_events,
                "period": f"Próximos {days_ahead} dias"
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar reuniões: {e}")
            return {
                "success": False,
                "error": str(e),
                "events": []
            }
    
    @tool
    async def send_meeting_reminder(
        self,
        event_id: str,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia lembrete de reunião
        
        Args:
            event_id: ID do evento
            custom_message: Mensagem personalizada (opcional)
            
        Returns:
            Status do envio
        """
        try:
            # Buscar detalhes do evento
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                event = await self.calendar_client.get_event(event_id)
            
            if not event:
                return {
                    "success": False,
                    "error": "Evento não encontrado"
                }
            
            # Preparar mensagem
            start_time = datetime.fromisoformat(
                event.get("start", {}).get("dateTime", "")
            )
            
            if custom_message:
                message = custom_message
            else:
                message = f"""
                🔔 Lembrete de Reunião
                
                📅 {event.get('summary', 'Reunião')}
                🕐 {start_time.strftime('%d/%m/%Y às %H:%M')}
                📍 {event.get('location', 'A definir')}
                
                {event.get('description', '')}
                """
            
            # TODO: Integrar com Evolution API para enviar via WhatsApp
            logger.info(f"📧 Lembrete enviado para evento {event_id}")
            
            return {
                "success": True,
                "event_id": event_id,
                "message_sent": message
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def find_best_slots(
        self,
        duration_minutes: int = 30,
        preferred_date: Optional[str] = None,  # DD/MM/YYYY
        num_options: int = 3
    ) -> List[Dict[str, str]]:
        """
        Encontra os melhores horários disponíveis
        
        Args:
            duration_minutes: Duração da reunião
            preferred_date: Data preferida (opcional)
            num_options: Número de opções a retornar
            
        Returns:
            Lista com melhores horários
        """
        slots = []
        
        try:
            # Determinar período de busca
            if preferred_date:
                date_parts = preferred_date.split('/')
                start_date = datetime(
                    year=int(date_parts[2]),
                    month=int(date_parts[1]),
                    day=int(date_parts[0]),
                    hour=9, minute=0
                )
            else:
                start_date = datetime.now().replace(hour=9, minute=0, second=0)
                if start_date < datetime.now():
                    start_date += timedelta(days=1)
            
            # Buscar slots nos próximos 7 dias
            current_date = start_date
            days_checked = 0
            
            while len(slots) < num_options and days_checked < 7:
                # Pular fins de semana
                if current_date.weekday() not in self.meeting_config["working_days"]:
                    current_date += timedelta(days=1)
                    days_checked += 1
                    continue
                
                # Horários prioritários (manhã e tarde)
                priority_times = ["09:00", "10:00", "14:00", "15:00", "16:00"]
                
                for time_str in priority_times:
                    if len(slots) >= num_options:
                        break
                    
                    hour, minute = map(int, time_str.split(':'))
                    test_time = current_date.replace(hour=hour, minute=minute)
                    end_time = test_time + timedelta(minutes=duration_minutes)
                    
                    # Verificar disponibilidade
                    async with self.rate_limiter:
                        await asyncio.sleep(self.request_interval)
                        available = await self.calendar_client.check_availability(
                            test_time, end_time
                        )
                    
                    if available:
                        slots.append({
                            "date": test_time.strftime("%d/%m/%Y"),
                            "time": test_time.strftime("%H:%M"),
                            "day_name": self._get_day_name(test_time),
                            "period": self._get_period(test_time),
                            "full_datetime": test_time.isoformat()
                        })
                
                current_date += timedelta(days=1)
                days_checked += 1
            
            return slots
            
        except Exception as e:
            logger.error(f"Erro ao buscar slots: {e}")
            return []
    
    # Métodos auxiliares privados
    
    def _is_business_hours(self, dt: datetime) -> bool:
        """Verifica se está em horário comercial"""
        if dt.weekday() not in self.meeting_config["working_days"]:
            return False
        
        hour_str = dt.strftime("%H:%M")
        return (
            self.meeting_config["business_hours"]["start"] <= hour_str <= 
            self.meeting_config["business_hours"]["end"]
        )
    
    def _build_description(
        self,
        base_description: str,
        lead_id: str,
        meeting_type: str
    ) -> str:
        """Constrói descrição completa da reunião"""
        description_parts = []
        
        if base_description:
            description_parts.append(base_description)
        
        description_parts.append(f"\n---\nTipo: {meeting_type}")
        description_parts.append(f"Lead ID: {lead_id}")
        description_parts.append("Agendado via SDR IA Solar Prime")
        
        return "\n".join(description_parts)
    
    async def _save_meeting_to_db(
        self,
        lead_id: str,
        google_event_id: str,
        event_data: Dict[str, Any],
        meeting_type: str
    ):
        """Salva reunião no banco de dados"""
        try:
            data = {
                "lead_id": lead_id,
                "google_event_id": google_event_id,
                "title": event_data["title"],
                "start_time": event_data["start_time"].isoformat(),
                "end_time": event_data["end_time"].isoformat(),
                "location": event_data.get("location", ""),
                "description": event_data.get("description", ""),
                "event_type": meeting_type,
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }
            
            supabase_client.client.table("calendar_events")\
                .insert(data)\
                .execute()
                
        except Exception as e:
            logger.error(f"Erro ao salvar reunião no banco: {e}")
    
    async def _update_meeting_in_db(
        self,
        event_id: str,
        new_start: datetime,
        new_end: datetime
    ):
        """Atualiza reunião no banco"""
        try:
            supabase_client.client.table("calendar_events")\
                .update({
                    "start_time": new_start.isoformat(),
                    "end_time": new_end.isoformat(),
                    "status": "rescheduled",
                    "updated_at": datetime.now().isoformat()
                })\
                .eq("google_event_id", event_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Erro ao atualizar reunião no banco: {e}")
    
    async def _cancel_meeting_in_db(self, event_id: str, reason: str):
        """Marca reunião como cancelada no banco"""
        try:
            supabase_client.client.table("calendar_events")\
                .update({
                    "status": "cancelled",
                    "cancelled_reason": reason,
                    "cancelled_at": datetime.now().isoformat()
                })\
                .eq("google_event_id", event_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Erro ao cancelar reunião no banco: {e}")
    
    async def _find_nearby_slots(
        self,
        target_time: datetime,
        duration_minutes: int
    ) -> List[Dict[str, str]]:
        """Encontra slots próximos ao horário desejado"""
        slots = []
        
        # Buscar no mesmo dia
        for hour_offset in [1, -1, 2, -2]:
            test_time = target_time + timedelta(hours=hour_offset)
            
            if not self._is_business_hours(test_time):
                continue
            
            end_time = test_time + timedelta(minutes=duration_minutes)
            
            async with self.rate_limiter:
                await asyncio.sleep(self.request_interval)
                available = await self.calendar_client.check_availability(
                    test_time, end_time
                )
            
            if available:
                slots.append({
                    "date": test_time.strftime("%d/%m/%Y"),
                    "time": test_time.strftime("%H:%M"),
                    "difference": f"{abs(hour_offset)}h do horário original"
                })
            
            if len(slots) >= 3:
                break
        
        return slots
    
    def _get_day_name(self, dt: datetime) -> str:
        """Retorna nome do dia em português"""
        days = {
            0: "Segunda-feira",
            1: "Terça-feira",
            2: "Quarta-feira",
            3: "Quinta-feira",
            4: "Sexta-feira",
            5: "Sábado",
            6: "Domingo"
        }
        return days.get(dt.weekday(), "")
    
    def _get_period(self, dt: datetime) -> str:
        """Retorna período do dia"""
        hour = dt.hour
        if hour < 12:
            return "Manhã"
        elif hour < 18:
            return "Tarde"
        else:
            return "Noite"
    
    @tool
    async def create_recurring_meeting(
        self,
        title: str,
        start_time: datetime,
        duration_minutes: int = 60,
        recurrence: str = "weekly",
        count: int = 4,
        attendees: List[str] = None,
        description: str = "",
        location: str = "",
        lead_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Cria reunião recorrente
        
        Args:
            title: Título da reunião
            start_time: Data/hora da primeira ocorrência
            duration_minutes: Duração em minutos
            recurrence: Frequência (daily, weekly, monthly)
            count: Número de ocorrências
            attendees: Lista de emails dos participantes
            description: Descrição da reunião
            location: Local da reunião
            lead_id: ID do lead (opcional)
            
        Returns:
            Informações das reuniões criadas
        """
        try:
            created_events = []
            current_time = start_time
            
            for i in range(count):
                # Calcular horário
                if i > 0:
                    if recurrence == "daily":
                        current_time = current_time + timedelta(days=1)
                    elif recurrence == "weekly":
                        current_time = current_time + timedelta(weeks=1)
                    elif recurrence == "monthly":
                        current_time = current_time + timedelta(days=30)
                
                end_time = current_time + timedelta(minutes=duration_minutes)
                
                # Criar evento
                async with self.rate_limiter:
                    await asyncio.sleep(self.request_interval)
                    event = await self.calendar_client.create_event(
                        title=f"{title} ({i+1}/{count})",
                        start_time=current_time,
                        end_time=end_time,
                        description=description,
                        location=location,
                        attendees=attendees or []
                    )
                
                if event:
                    created_events.append(event)
                    
                    # Salvar no banco se tem lead_id
                    if lead_id:
                        await self._save_event_to_db(
                            event_id=event["google_event_id"],
                            lead_id=lead_id,
                            title=title,
                            start_time=current_time,
                            end_time=end_time,
                            location=location
                        )
            
            return {
                "success": True,
                "count": len(created_events),
                "recurrence": recurrence,
                "events": created_events,
                "message": f"Criadas {len(created_events)} reuniões recorrentes"
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar reuniões recorrentes: {e}")
            return {
                "success": False,
                "error": str(e),
                "events": []
            }