"""
Services do sistema SDR Agent
"""

from .supabase_service import SupabaseService, get_supabase_service
from .evolution_service import EvolutionAPIService, get_evolution_service as get_evolution_service_old
from .kommo_service import KommoService, get_kommo_service
from .calendar_service import GoogleCalendarService, get_calendar_service

# Novo serviço Evolution API v2
from .evolution import EvolutionService, get_evolution_service

__all__ = [
    'SupabaseService',
    'get_supabase_service',
    # Evolution API (old - manter temporariamente para compatibilidade)
    'EvolutionAPIService', 
    'get_evolution_service_old',
    # Evolution API v2 (new)
    'EvolutionService',
    'get_evolution_service',
    'KommoService',
    'get_kommo_service',
    'GoogleCalendarService',
    'get_calendar_service'
]