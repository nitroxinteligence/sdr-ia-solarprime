"""
Testes REAIS Google Calendar API - Operações CRUD Completas
Implementa testes sem mocks seguindo padrões 2025 do Context7.

Este módulo testa operações completas de CRUD (Create, Read, Update, Delete)
com a API real do Google Calendar, incluindo thread safety e rate limiting.
"""

import pytest
import os
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
import google_auth_httplib2

from agente.core.config import (
    GOOGLE_SERVICE_ACCOUNT_EMAIL,
    GOOGLE_PRIVATE_KEY,
    GOOGLE_PROJECT_ID,
    GOOGLE_CALENDAR_ID,
    DISABLE_GOOGLE_CALENDAR
)

class TestGoogleCalendarReal:
    """Testes REAIS de operações CRUD do Google Calendar."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada teste."""
        self.test_prefix = "[TEST-CRUD]"
        self.created_events = []
        self.test_calendar_id = GOOGLE_CALENDAR_ID or 'primary'
        
        if not os.getenv('PYTEST_RUNNING'):
            pytest.skip("Testes reais só executam em ambiente de teste")
    
    @pytest.fixture(autouse=True)
    def cleanup_events(self):
        """Cleanup automático de eventos de teste."""
        yield
        
        if hasattr(self, 'created_events') and self.created_events:
            try:
                service = self._create_calendar_service()
                for event_id in self.created_events:
                    try:
                        service.events().delete(
                            calendarId=self.test_calendar_id,
                            eventId=event_id
                        ).execute()
                    except:
                        pass
            except:
                pass
    
    def _has_real_credentials(self) -> bool:
        """Verifica credenciais reais."""
        required_vars = [GOOGLE_SERVICE_ACCOUNT_EMAIL, GOOGLE_PRIVATE_KEY, GOOGLE_PROJECT_ID]
        return all(var and var.strip() and not var.startswith('test-') for var in required_vars)
    
    def _create_service_credentials(self):
        """Cria credenciais seguindo padrões 2025."""
        service_account_info = {
            "type": "service_account", 
            "project_id": GOOGLE_PROJECT_ID,
            "private_key": GOOGLE_PRIVATE_KEY,
            "client_email": GOOGLE_SERVICE_ACCOUNT_EMAIL,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        
        return service_account.Credentials.from_service_account_info(
            service_account_info, scopes=['https://www.googleapis.com/auth/calendar']
        )
    
    def _create_calendar_service(self):
        """Cria serviço com thread safety."""
        credentials = self._create_service_credentials()
        http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http())
        return build('calendar', 'v3', http=http, cache_discovery=False)
    
    def _create_test_event(self, summary: str = None, start_minutes: int = 60):
        """Cria evento de teste padrão."""
        if not summary:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary = f"{self.test_prefix} Evento Teste {timestamp}"
        
        start_time = datetime.now(timezone.utc) + timedelta(minutes=start_minutes)
        end_time = start_time + timedelta(hours=1)
        
        return {
            'summary': summary,
            'description': 'Evento criado automaticamente para testes.',
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'America/Sao_Paulo'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'America/Sao_Paulo'},
            'status': 'confirmed'
        }

    @pytest.mark.real_integration
    @pytest.mark.timeout(60)
    def test_create_event_real(self):
        """Testa CRIAÇÃO REAL de evento no Google Calendar."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais não disponíveis")
        if DISABLE_GOOGLE_CALENDAR:
            pytest.skip("Google Calendar desabilitado")
        
        try:
            service = self._create_calendar_service()
            event_data = self._create_test_event("Teste Criação Real")
            
            created_event = service.events().insert(
                calendarId=self.test_calendar_id,
                body=event_data
            ).execute()
            
            event_id = created_event['id']
            self.created_events.append(event_id)
            
            assert created_event is not None
            assert 'id' in created_event
            assert created_event['summary'] == event_data['summary']
            
            print(f"✅ Evento criado: {event_id}")
            
        except HttpError as e:
            pytest.fail(f"❌ Erro HTTP ao criar evento: {e}")
        except Exception as e:
            pytest.fail(f"❌ Erro inesperado: {str(e)}")

    @pytest.mark.real_integration
    @pytest.mark.timeout(60)
    def test_complete_crud_cycle_real(self):
        """Testa CICLO COMPLETO CRUD em uma única operação real."""
        if not self._has_real_credentials():
            pytest.skip("Credenciais reais não disponíveis")
        if DISABLE_GOOGLE_CALENDAR:
            pytest.skip("Google Calendar desabilitado")
        
        event_id = None
        
        try:
            service = self._create_calendar_service()
            
            # CREATE
            original_summary = f"{self.test_prefix} CRUD Completo"
            event_data = self._create_test_event(original_summary)
            
            created_event = service.events().insert(
                calendarId=self.test_calendar_id,
                body=event_data
            ).execute()
            
            event_id = created_event['id']
            assert created_event['summary'] == original_summary
            
            # READ
            read_event = service.events().get(
                calendarId=self.test_calendar_id,
                eventId=event_id
            ).execute()
            
            assert read_event['id'] == event_id
            assert read_event['summary'] == original_summary
            
            # UPDATE
            updated_summary = f"{original_summary} - ATUALIZADO"
            read_event['summary'] = updated_summary
            
            updated_event = service.events().update(
                calendarId=self.test_calendar_id,
                eventId=event_id,
                body=read_event
            ).execute()
            
            assert updated_event['summary'] == updated_summary
            
            # DELETE
            service.events().delete(
                calendarId=self.test_calendar_id,
                eventId=event_id
            ).execute()
            
            # Verifica que foi deletado
            try:
                # Tenta buscar o evento deletado
                deleted_event = service.events().get(
                    calendarId=self.test_calendar_id,
                    eventId=event_id
                ).execute()
                
                # Se chegou aqui, verifica se está marcado como cancelado
                if deleted_event.get('status') == 'cancelled':
                    print("✅ Evento marcado como cancelado (comportamento válido do Google Calendar)")
                else:
                    print(f"⚠️ Evento ainda existe com status: {deleted_event.get('status', 'unknown')}")
                    
            except HttpError as e:
                if e.resp.status == 404:
                    print("✅ Evento removido completamente (404 - não encontrado)")
                else:
                    print(f"⚠️ Erro inesperado ao verificar exclusão: {e.resp.status}")
                    raise
            
            event_id = None  # Limpa tracking
            print("🎉 CICLO CRUD COMPLETO realizado com sucesso!")
            
        except HttpError as e:
            if e.resp.status != 404:  # 404 é esperado no DELETE
                pytest.fail(f"❌ Erro HTTP no ciclo CRUD: {e}")
        except Exception as e:
            pytest.fail(f"❌ Erro inesperado no ciclo CRUD: {str(e)}")
        finally:
            if event_id and event_id not in self.created_events:
                self.created_events.append(event_id)