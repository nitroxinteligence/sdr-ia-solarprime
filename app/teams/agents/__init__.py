"""
Agentes Especializados do SDR Team
Cada agente tem uma responsabilidade específica no processo de vendas
"""

from .qualification import QualificationAgent
from .calendar import CalendarAgent
from .followup import FollowUpAgent
from .knowledge import KnowledgeAgent
from .crm import CRMAgent
from .bill_analyzer import BillAnalyzerAgent

__all__ = [
    'QualificationAgent',
    'CalendarAgent', 
    'FollowUpAgent',
    'KnowledgeAgent',
    'CRMAgent',
    'BillAnalyzerAgent'
]