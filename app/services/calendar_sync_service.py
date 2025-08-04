"""
Calendar Sync Service - Sincronização Google Calendar ↔ Supabase
Serviço para manter calendário sincronizado e enviar lembretes
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from app.integrations.google_calendar import google_calendar_client
from app.integrations.supabase_client import SupabaseClient
from app.integrations.evolution import evolution_client
from app.config import settings

logger = logging.getLogger(__name__)

class CalendarSyncService:
    """
    Serviço de sincronização de calendário
    Mantém Google Calendar e Supabase sincronizados
    Envia lembretes de reuniões via WhatsApp
    """
    
    def __init__(self):
        """Inicializa o serviço de sincronização"""
        self.calendar_client = google_calendar_client
        self.db = SupabaseClient()
        self.evolution = evolution_client  # Usar singleton existente
        self.running = False
        self.sync_interval = 300  # 5 minutos
        self.reminder_interval = 60  # 1 minuto
        
    async def start(self):
        """Inicia o serviço de sincronização"""
        if self.running:
            logger.warning("Serviço de sincronização já está rodando")
            return
            
        self.running = True
        logger.info("🚀 Iniciando serviço de sincronização de calendário")
        
        # Iniciar tarefas assíncronas
        asyncio.create_task(self._sync_loop())
        asyncio.create_task(self._reminder_loop())
        
    async def stop(self):
        """Para o serviço de sincronização"""
        self.running = False
        logger.info("⏹️ Parando serviço de sincronização de calendário")
        
    async def _sync_loop(self):
        """Loop principal de sincronização"""
        while self.running:
            try:
                await self.sync_events()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Erro no loop de sincronização: {e}")
                await asyncio.sleep(60)
    
    async def _reminder_loop(self):
        """Loop de envio de lembretes"""
        while self.running:
            try:
                await self.send_pending_reminders()
                await asyncio.sleep(self.reminder_interval)
            except Exception as e:
                logger.error(f"Erro no loop de lembretes: {e}")
                await asyncio.sleep(60)
    
    async def sync_events(self):
        """
        Sincroniza eventos entre Google Calendar e Supabase
        Busca eventos dos próximos 30 dias
        """
        try:
            logger.info("🔄 Iniciando sincronização de eventos")
            
            # Buscar eventos do Google Calendar
            time_min = datetime.now()
            time_max = time_min + timedelta(days=30)
            
            google_events = await self.calendar_client.list_events(
                time_min=time_min,
                time_max=time_max,
                max_results=100
            )
            
            # Buscar eventos do banco
            db_events = self.db.client.table('calendar_events').select("*").gte(
                'start_time', time_min.isoformat()
            ).lte(
                'start_time', time_max.isoformat()
            ).execute()
            
            # Criar mapas para comparação
            google_map = {e['google_event_id']: e for e in google_events if e.get('google_event_id')}
            db_map = {e['google_event_id']: e for e in db_events.data if e.get('google_event_id')}
            
            # Sincronizar diferenças
            await self._sync_new_events(google_map, db_map)
            await self._sync_updated_events(google_map, db_map)
            await self._sync_deleted_events(google_map, db_map)
            
            logger.info(f"✅ Sincronização concluída: {len(google_events)} eventos processados")
            
        except Exception as e:
            logger.error(f"❌ Erro na sincronização: {e}")
    
    async def _sync_new_events(self, google_map: Dict, db_map: Dict):
        """Sincroniza novos eventos do Google para o banco"""
        new_events = [
            event for event_id, event in google_map.items()
            if event_id not in db_map
        ]
        
        for event in new_events:
            try:
                # Preparar dados para inserção
                db_event = {
                    'google_event_id': event['google_event_id'],
                    'title': event.get('title', 'Sem título'),
                    'description': event.get('description', ''),
                    'start_time': self._parse_google_time(event.get('start')),
                    'end_time': self._parse_google_time(event.get('end')),
                    'location': event.get('location', ''),
                    'status': event.get('status', 'confirmed'),
                    'attendees': json.dumps(event.get('attendees', [])),
                    'metadata': json.dumps({
                        'html_link': event.get('html_link', ''),
                        'synced_at': datetime.now().isoformat()
                    })
                }
                
                # Inserir no banco
                self.db.client.table('calendar_events').insert(db_event).execute()  # Removido await - cliente síncrono
                logger.info(f"📅 Novo evento sincronizado: {event.get('title')}")
                
            except Exception as e:
                logger.error(f"Erro ao sincronizar novo evento: {e}")
    
    async def _sync_updated_events(self, google_map: Dict, db_map: Dict):
        """Atualiza eventos modificados"""
        for event_id in set(google_map.keys()) & set(db_map.keys()):
            google_event = google_map[event_id]
            db_event = db_map[event_id]
            
            # Verificar se há mudanças
            if self._event_changed(google_event, db_event):
                try:
                    updates = {
                        'title': google_event.get('title'),
                        'description': google_event.get('description', ''),
                        'start_time': self._parse_google_time(google_event.get('start')),
                        'end_time': self._parse_google_time(google_event.get('end')),
                        'location': google_event.get('location', ''),
                        'status': google_event.get('status'),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    self.db.client.table('calendar_events').update(updates).eq(
                        'google_event_id', event_id
                    ).execute()
                    
                    logger.info(f"📝 Evento atualizado: {google_event.get('title')}")
                    
                except Exception as e:
                    logger.error(f"Erro ao atualizar evento: {e}")
    
    async def _sync_deleted_events(self, google_map: Dict, db_map: Dict):
        """Marca eventos deletados como cancelados"""
        deleted_events = [
            event_id for event_id in db_map.keys()
            if event_id not in google_map
        ]
        
        for event_id in deleted_events:
            try:
                self.db.client.table('calendar_events').update({
                    'status': 'cancelled',
                    'cancelled_at': datetime.now().isoformat()
                }).eq(
                    'google_event_id', event_id
                ).execute()
                
                logger.info(f"❌ Evento marcado como cancelado: {event_id}")
                
            except Exception as e:
                logger.error(f"Erro ao marcar evento como cancelado: {e}")
    
    async def send_pending_reminders(self):
        """
        Envia lembretes de reuniões próximas
        Verifica eventos que precisam de lembrete
        """
        try:
            # Buscar eventos que precisam de lembrete
            now = datetime.now()
            
            # Query para eventos nos próximos 30 minutos que não receberam lembrete
            events = self.db.client.table('calendar_events').select("*").eq(
                'status', 'scheduled'
            ).eq(
                'reminder_sent', False
            ).gte(
                'start_time', now.isoformat()
            ).lte(
                'start_time', (now + timedelta(minutes=30)).isoformat()
            ).execute()
            
            for event in events.data:
                await self._send_reminder(event)
                
        except Exception as e:
            logger.error(f"Erro ao enviar lembretes: {e}")
    
    async def _send_reminder(self, event: Dict[str, Any]):
        """Envia lembrete individual via WhatsApp"""
        try:
            lead_id = event.get('lead_id')
            if not lead_id:
                return
            
            # Buscar dados do lead
            lead_result = self.db.client.table('leads').select("*").eq(
                'id', lead_id
            ).single().execute()
            
            if not lead_result.data:
                return
            
            lead = lead_result.data
            phone = lead.get('phone_number')
            
            if not phone:
                return
            
            # Calcular tempo até o evento
            start_time = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
            time_until = start_time - datetime.now()
            minutes_until = int(time_until.total_seconds() / 60)
            
            # Preparar mensagem
            if minutes_until <= 5:
                message = f"🔔 {lead.get('name')}, nossa reunião começa em poucos minutos!\n"
            elif minutes_until <= 30:
                message = f"⏰ {lead.get('name')}, lembrete: nossa reunião é em {minutes_until} minutos\n"
            else:
                return  # Não enviar se for mais de 30 minutos
            
            message += f"📅 {event['title']}\n"
            message += f"🕐 {start_time.strftime('%H:%M')}\n"
            
            if event.get('meeting_link'):
                message += f"🔗 Link: {event['meeting_link']}\n"
            
            # Enviar via Evolution API
            await self.evolution.send_text_message(
                phone=phone,
                message=message
            )
            
            # Marcar lembrete como enviado
            self.db.client.table('calendar_events').update({
                'reminder_sent': True
            }).eq(
                'id', event['id']
            ).execute()
            
            logger.info(f"📱 Lembrete enviado para {lead.get('name')}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete: {e}")
    
    def _parse_google_time(self, time_data: Any) -> str:
        """Parse de tempo do Google Calendar para ISO format"""
        if isinstance(time_data, dict):
            datetime_str = time_data.get('dateTime', time_data.get('date'))
        else:
            datetime_str = time_data
            
        if not datetime_str:
            return datetime.now().isoformat()
            
        # Converter para datetime e retornar ISO
        try:
            if 'T' in datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(datetime_str, '%Y-%m-%d')
            return dt.isoformat()
        except:
            return datetime.now().isoformat()
    
    def _event_changed(self, google_event: Dict, db_event: Dict) -> bool:
        """Verifica se um evento foi modificado"""
        # Comparar campos principais
        fields_to_check = ['title', 'description', 'location', 'status']
        
        for field in fields_to_check:
            if google_event.get(field) != db_event.get(field):
                return True
        
        # Comparar horários
        google_start = self._parse_google_time(google_event.get('start'))
        google_end = self._parse_google_time(google_event.get('end'))
        
        db_start = db_event.get('start_time')
        db_end = db_event.get('end_time')
        
        # Normalizar para comparação
        if isinstance(db_start, str):
            db_start = datetime.fromisoformat(db_start.replace('Z', '+00:00')).isoformat()
        if isinstance(db_end, str):
            db_end = datetime.fromisoformat(db_end.replace('Z', '+00:00')).isoformat()
        
        return google_start != db_start or google_end != db_end
    
    async def force_sync(self) -> Dict[str, Any]:
        """
        Força sincronização imediata
        Útil para testes ou sincronização manual
        """
        try:
            await self.sync_events()
            await self.send_pending_reminders()
            
            return {
                'success': True,
                'message': 'Sincronização forçada concluída'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Singleton
calendar_sync_service = CalendarSyncService()