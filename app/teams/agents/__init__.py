"""
Agentes Especializados do SDR Team
Cada agente tem uma responsabilidade específica no processo de vendas
NOTAS: 
- QualificationAgent removido - lógica migrada para AgenticSDR
- KnowledgeAgent removido - substituído por KnowledgeService
"""

# QualificationAgent REMOVIDO - lógica migrada para AgenticSDR
# KnowledgeAgent REMOVIDO - substituído por KnowledgeService
# from .qualification import QualificationAgent
# from .knowledge import KnowledgeAgent
from .calendar import CalendarAgent
from .followup import FollowUpAgent
from .crm import CRMAgent
# BillAnalyzerAgent REMOVIDO - substituído por função simples no AgenticSDR
# from .bill_analyzer import BillAnalyzerAgent

__all__ = [
    # 'QualificationAgent',  # REMOVIDO - migrado para AgenticSDR
    # 'KnowledgeAgent',      # REMOVIDO - substituído por KnowledgeService
    'CalendarAgent', 
    'FollowUpAgent',
    'CRMAgent',
    # 'BillAnalyzerAgent'   # REMOVIDO - substituído por função Vision AI no AgenticSDR
]