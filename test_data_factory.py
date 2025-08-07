#!/usr/bin/env python3
"""
TEST DATA FACTORY - UUID SPECIALIST 2025
Classe modular para gerar dados de teste válidos com UUIDs reais
Compatível com PostgreSQL/Supabase schema
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List


class TestDataFactory:
    """Factory para gerar dados de teste com UUIDs válidos"""
    
    @staticmethod
    def generate_uuid() -> str:
        """
        Gera UUID v4 válido (melhor prática 2025)
        Retorna string para compatibilidade com Supabase
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def create_test_lead(
        name: str = "João Silva",
        phone: str = "5511999887766",
        bill_value: float = 450.0,
        email: str = "joao.silva@email.com"
    ) -> Dict[str, Any]:
        """
        Cria dados de lead de teste com UUID válido
        
        Args:
            name: Nome do lead
            phone: Telefone do lead
            bill_value: Valor da conta de luz
            email: Email do lead
            
        Returns:
            Dict com dados do lead incluindo UUID válido
        """
        return {
            'id': TestDataFactory.generate_uuid(),  # UUID real
            'name': name,
            'phone_number': phone,
            'bill_value': bill_value,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def create_google_event(
        lead_name: str = "João Silva",
        hours_from_now: int = 25
    ) -> Dict[str, Any]:
        """
        Cria evento Google Calendar de teste
        
        Args:
            lead_name: Nome do lead para o evento
            hours_from_now: Horas no futuro para o evento
            
        Returns:
            Dict com dados do evento Google Calendar
        """
        meeting_time = datetime.now() + timedelta(hours=hours_from_now)
        
        return {
            'id': f'google-event-{TestDataFactory.generate_uuid()}',
            'summary': f'Consultoria Energia Solar - {lead_name}',
            'start': {
                'dateTime': meeting_time.isoformat() + 'Z'
            },
            'location': 'Online',
            'hangoutLink': f'https://meet.google.com/{TestDataFactory.generate_uuid()[:10]}',
            'description': 'Reunião para apresentar proposta personalizada de energia solar'
        }
    
    @staticmethod
    def create_qualification_id() -> str:
        """
        Cria ID de qualificação válido (UUID)
        
        Returns:
            UUID string válido
        """
        return TestDataFactory.generate_uuid()
    
    @staticmethod
    def create_conversation_id() -> str:
        """
        Cria ID de conversa válido (UUID)
        
        Returns:
            UUID string válido
        """
        return TestDataFactory.generate_uuid()
    
    @staticmethod
    def create_conversation_history(
        lead_name: str = "João Silva",
        bill_value: float = 450.0
    ) -> List[Dict[str, Any]]:
        """
        Cria histórico de conversa realista para testes
        
        Args:
            lead_name: Nome do lead para personalização
            bill_value: Valor da conta para contexto
            
        Returns:
            Lista com mensagens da conversa
        """
        first_name = lead_name.split()[0]
        savings = int(bill_value * 0.3)  # 30% economia
        
        return [
            {
                'role': 'user',
                'content': 'Olá, gostaria de saber sobre energia solar',
                'created_at': (datetime.now() - timedelta(hours=48)).isoformat()
            },
            {
                'role': 'assistant', 
                'content': f'Olá {first_name}! Sou a Helen, consultora em energia solar. Que bom saber do seu interesse! Qual o valor da sua conta de luz atual?',
                'created_at': (datetime.now() - timedelta(hours=48, minutes=1)).isoformat()
            },
            {
                'role': 'user',
                'content': f'Minha conta fica em torno de R$ {bill_value:.0f} por mês',
                'created_at': (datetime.now() - timedelta(hours=47)).isoformat()
            },
            {
                'role': 'assistant',
                'content': f'Perfeito {first_name}! Com R$ {bill_value:.0f}/mês você pode economizar cerca de R$ {savings} mensais (30%) com energia solar. Você tem interesse em conhecer nossa proposta personalizada?',
                'created_at': (datetime.now() - timedelta(hours=47, minutes=2)).isoformat()
            },
            {
                'role': 'user', 
                'content': 'Sim, tenho muito interesse! Como funciona?',
                'created_at': (datetime.now() - timedelta(hours=46)).isoformat()
            },
            {
                'role': 'assistant',
                'content': 'Que ótimo! Vou agendar uma reunião para te mostrar tudo detalhadamente. Que tal amanhã às 14h?',
                'created_at': (datetime.now() - timedelta(hours=46, minutes=3)).isoformat()
            },
            {
                'role': 'user',
                'content': 'Perfeito! Confirmo para amanhã às 14h',
                'created_at': (datetime.now() - timedelta(hours=45)).isoformat()
            }
        ]
    
    @staticmethod
    def create_complete_test_data(
        lead_name: str = "João Silva",
        phone: str = "5511999887766", 
        bill_value: float = 450.0,
        email: str = "joao.silva@email.com",
        meeting_hours_from_now: int = 25
    ) -> Dict[str, Any]:
        """
        Cria conjunto completo de dados de teste com UUIDs válidos
        
        Args:
            lead_name: Nome do lead
            phone: Telefone do lead
            bill_value: Valor da conta de luz
            email: Email do lead  
            meeting_hours_from_now: Horas até a reunião
            
        Returns:
            Dict completo com todos os dados de teste
        """
        return {
            'lead_data': TestDataFactory.create_test_lead(
                name=lead_name,
                phone=phone, 
                bill_value=bill_value,
                email=email
            ),
            'google_event': TestDataFactory.create_google_event(
                lead_name=lead_name,
                hours_from_now=meeting_hours_from_now
            ),
            'qualification_id': TestDataFactory.create_qualification_id(),
            'conversation_id': TestDataFactory.create_conversation_id(),
            'conversation_history': TestDataFactory.create_conversation_history(
                lead_name=lead_name,
                bill_value=bill_value
            )
        }


# Exemplo de uso
if __name__ == "__main__":
    # Teste da factory
    print("🧪 TESTANDO TEST DATA FACTORY")
    print("=" * 50)
    
    # Gerar UUID
    print(f"UUID gerado: {TestDataFactory.generate_uuid()}")
    
    # Gerar lead
    lead = TestDataFactory.create_test_lead()
    print(f"Lead ID: {lead['id']}")
    print(f"Lead Name: {lead['name']}")
    
    # Gerar dados completos
    complete_data = TestDataFactory.create_complete_test_data()
    print(f"Qualification ID: {complete_data['qualification_id']}")
    print(f"Conversation ID: {complete_data['conversation_id']}")
    print(f"Google Event ID: {complete_data['google_event']['id']}")
    
    print("✅ Test Data Factory funcionando corretamente!")