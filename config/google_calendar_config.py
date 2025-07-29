"""
Google Calendar Configuration
=============================
Configuração para integração com Google Calendar
"""

import os
from pathlib import Path
from typing import Optional

class GoogleCalendarConfig:
    """Configuração do Google Calendar"""
    
    def __init__(self):
        # Paths para credenciais
        self.credentials_path = os.getenv(
            'GOOGLE_CALENDAR_CREDENTIALS_PATH', 
            'credentials/google_calendar_credentials.json'
        )
        self.token_path = os.getenv(
            'GOOGLE_CALENDAR_TOKEN_PATH', 
            'credentials/google_calendar_token.pickle'
        )
        
        # ID do calendário (primary = calendário principal do usuário)
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        # Configurações de reunião
        self.default_meeting_duration = int(os.getenv('MEETING_DURATION_MINUTES', '60'))
        self.meeting_location = os.getenv(
            'MEETING_LOCATION', 
            'SolarPrime - Av. Boa Viagem, 3344 - Boa Viagem, Recife - PE'
        )
        
        # Horários de atendimento
        self.business_hours_start = int(os.getenv('BUSINESS_HOURS_START', '9'))
        self.business_hours_end = int(os.getenv('BUSINESS_HOURS_END', '18'))
        self.business_days = [0, 1, 2, 3, 4]  # Segunda a sexta
        
        # Configurações de notificação
        self.reminder_minutes = [
            24 * 60,  # 1 dia antes
            60,       # 1 hora antes
            15        # 15 minutos antes
        ]
        
        # Templates de evento
        self.event_templates = {
            'initial_meeting': {
                'title': '☀️ Reunião SolarPrime - {lead_name}',
                'description': """
🌟 REUNIÃO DE APRESENTAÇÃO - SOLARPRIME

👤 Cliente: {lead_name}
📱 Telefone: {lead_phone}
💰 Valor da conta: R$ {bill_value}
⚡ Consumo: {consumption_kwh} kWh
🎯 Solução de interesse: {solution_type}

📋 AGENDA DA REUNIÃO:
1. Apresentação da SolarPrime
2. Análise da conta de energia
3. Demonstração da economia
4. Apresentação das soluções
5. Proposta personalizada
6. Esclarecimento de dúvidas

💡 PREPARAR:
- Proposta personalizada
- Simulação de economia
- Cases de sucesso similares
- Contrato padrão

🔗 Mais informações no CRM: {crm_link}
                """
            },
            'follow_up_meeting': {
                'title': '🔄 Follow-up SolarPrime - {lead_name}',
                'description': """
🔄 REUNIÃO DE FOLLOW-UP - SOLARPRIME

👤 Cliente: {lead_name}
📱 Telefone: {lead_phone}
📅 Reunião anterior: {last_meeting_date}

📋 PONTOS A REVISAR:
- Status da proposta
- Dúvidas pendentes
- Ajustes necessários
- Próximos passos

🔗 Histórico no CRM: {crm_link}
                """
            },
            'contract_signing': {
                'title': '✍️ Assinatura Contrato - {lead_name}',
                'description': """
✍️ ASSINATURA DE CONTRATO - SOLARPRIME

👤 Cliente: {lead_name}
📱 Telefone: {lead_phone}
💰 Valor do investimento: R$ {investment_value}
📊 Economia prevista: R$ {monthly_savings}/mês

📋 DOCUMENTOS NECESSÁRIOS:
- RG e CPF
- Comprovante de residência
- Última conta de energia
- Comprovante de renda (se financiamento)

🔗 Proposta no CRM: {crm_link}
                """
            }
        }
        
        # Configurações AGnO Framework
        self.agno_config = {
            'use_agno_tools': True,  # Usar GoogleCalendarTools do AGnO
            'fallback_to_api': True,  # Fallback para API direta se AGnO falhar
            'cache_events': True,     # Cache de eventos para performance
            'cache_duration': 300     # 5 minutos de cache
        }
    
    def validate(self) -> bool:
        """Valida se as configurações estão corretas"""
        # Verificar se arquivo de credenciais existe
        if not Path(self.credentials_path).exists():
            print(f"⚠️  Arquivo de credenciais não encontrado: {self.credentials_path}")
            print("📝 Para configurar o Google Calendar:")
            print("1. Acesse: https://console.cloud.google.com/")
            print("2. Crie um novo projeto ou selecione um existente")
            print("3. Ative a API do Google Calendar")
            print("4. Crie credenciais OAuth 2.0")
            print("5. Baixe o arquivo JSON e salve em: " + self.credentials_path)
            return False
        
        return True
    
    def get_event_template(self, template_type: str = 'initial_meeting') -> dict:
        """Retorna template de evento"""
        return self.event_templates.get(template_type, self.event_templates['initial_meeting'])


# Instância global
google_calendar_config = GoogleCalendarConfig()