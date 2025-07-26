"""
Agente SDR Demo - SolarPrime
============================
Versão de demonstração sem necessidade de API key
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from loguru import logger
import random

# Configurações locais
from config.agent_config import config, get_config
from utils.helpers import calculate_typing_delay, format_phone_number


class DemoSDRAgent:
    """Agente SDR de demonstração para testes sem API key"""
    
    def __init__(self):
        """Inicializa o agente demo"""
        self.config = get_config()
        self.current_stage = "INITIAL_CONTACT"
        self.lead_info = {}
        self.conversation_history = {}
        
        # Respostas pré-definidas para demo
        self.demo_responses = {
            "greeting": [
                f"Olá! 👋 Sou a {self.config.personality.name} da {self.config.personality.company}!\n\nEstou entrando em contato porque temos uma oportunidade incrível de economia na sua conta de energia através da energia solar.\n\nVocê tem interesse em conhecer como pode economizar até 95% na sua conta de luz? ☀️",
                f"Oi! Tudo bem? 😊 Aqui é a {self.config.personality.name} da {self.config.personality.company}.\n\nVi que você tem interesse em economizar na conta de luz! Com energia solar, você pode reduzir até 95% do valor.\n\nPosso te explicar como funciona?",
            ],
            "interest": [
                "Que ótimo! 😊 Fico feliz com seu interesse!\n\nA energia solar é uma das melhores formas de economizar hoje em dia. Antes de te explicar melhor, você mora em casa ou apartamento?",
                "Maravilha! A energia solar realmente é um excelente investimento.\n\nPara eu te apresentar a melhor solução, me conta: você é proprietário(a) do imóvel?",
            ],
            "no_interest": [
                "Entendo perfeitamente! Agradeço sua atenção.\n\nCaso mude de ideia ou queira saber mais sobre energia solar no futuro, estarei sempre à disposição.\n\nTenha um excelente dia! 😊",
                "Sem problemas! Obrigada pelo seu tempo.\n\nSe precisar de informações sobre energia solar no futuro, pode me procurar. Sucesso! 🌟",
            ],
            "cost_concern": [
                "Entendo sua preocupação! Na verdade, a energia solar hoje está muito mais acessível.\n\nTemos opções de financiamento onde a parcela fica menor que sua economia mensal. Ou seja, você começa a economizar desde o primeiro mês! 💰\n\nQual o valor médio da sua conta de luz hoje?",
                "Ótima pergunta! O investimento inicial pode parecer alto, mas pense assim:\n\n✅ Retorno em 3-4 anos\n✅ 25+ anos de energia grátis\n✅ Valorização do imóvel\n✅ Financiamento com parcelas menores que a economia\n\nVale muito a pena! Posso fazer uma simulação para você?",
            ],
            "how_it_works": [
                "Claro! É bem simples:\n\n1️⃣ Instalamos painéis solares no seu telhado\n2️⃣ Eles captam a luz do sol e geram energia\n3️⃣ Você usa essa energia na sua casa\n4️⃣ O excesso vai para a rede e gera créditos\n5️⃣ À noite você usa os créditos acumulados\n\nTudo isso reduz sua conta em até 95%! Legal, né?",
                "Com prazer! O sistema funciona assim:\n\n☀️ Durante o dia, os painéis geram energia\n🏠 Sua casa consome direto dos painéis\n🔌 O excedente gera créditos na distribuidora\n🌙 À noite, você usa os créditos\n💰 Economia de até 95% todo mês!\n\nÉ totalmente automatizado e monitorado por app!",
            ],
            "property_info": [
                "Perfeito! {property_type} é ideal para energia solar!\n\nAgora me conta: qual o valor médio da sua conta de energia?",
                "Excelente! Em {property_type} a instalação é ainda mais simples.\n\nPara fazer uma proposta personalizada, preciso saber: sua conta de luz vem em torno de quanto por mês?",
            ],
            "bill_value": [
                "R$ {value}? Excelente! Com esse consumo, você tem um potencial de economia muito bom! 💰\n\nCom energia solar, essa conta pode cair para apenas R$ {savings}!\n\nGostaria de receber uma proposta personalizada sem compromisso?",
                "Perfeito! Com uma conta de R$ {value}, você economizaria cerca de R$ {yearly} por ano!\n\nIsso dá quase {months} meses de conta grátis por ano! 🎉\n\nQue tal agendarmos uma conversa com nosso consultor para ver a melhor solução?",
            ],
            "scheduling": [
                "Maravilha! Vou agendar uma conversa com nosso especialista.\n\n📅 Quando seria melhor para você?\n- Amanhã às 10h ou 14h?\n- Quinta-feira às 9h ou 16h?\n\nOu prefere sugerir outro horário?",
                "Ótimo! Nosso consultor vai adorar conversar com você!\n\nQual período funciona melhor:\n🌅 Manhã (9h-12h)\n☀️ Tarde (14h-18h)\n\nE qual dia da semana?",
            ],
            "default": [
                "Interessante sua pergunta! Para te dar uma resposta mais precisa, me conta um pouco mais sobre o que você gostaria de saber?",
                "Boa pergunta! Cada caso é único, mas posso te ajudar. O que especificamente você gostaria de entender melhor?",
            ]
        }
        
        logger.info(f"Demo SDR Agent '{self.config.personality.name}' inicializado")
    
    def _get_demo_response(self, category: str, **kwargs) -> str:
        """Retorna uma resposta demo baseada na categoria"""
        responses = self.demo_responses.get(category, self.demo_responses["default"])
        response = random.choice(responses)
        
        # Substitui placeholders
        for key, value in kwargs.items():
            response = response.replace(f"{{{key}}}", str(value))
        
        return response
    
    def _analyze_message(self, message: str) -> Dict[str, Any]:
        """Analisa a mensagem e determina intenção (versão simplificada)"""
        message_lower = message.lower()
        
        # Análise básica de sentimento e intenção
        if any(word in message_lower for word in ["não", "nao", "nem", "nunca", "desculp"]):
            sentiment = "negativo"
            if any(word in message_lower for word in ["interesse", "quero", "preciso"]):
                intent = "no_interest"
            else:
                intent = "objection"
        elif any(word in message_lower for word in ["sim", "claro", "quero", "interesse", "legal", "ótimo"]):
            sentiment = "positivo"
            intent = "interest"
        elif any(word in message_lower for word in ["caro", "custo", "valor", "preço", "quanto"]):
            sentiment = "neutro"
            intent = "cost_concern"
        elif any(word in message_lower for word in ["funciona", "como", "explica"]):
            sentiment = "neutro"
            intent = "how_it_works"
        elif any(word in message_lower for word in ["casa", "apartamento", "ap"]):
            sentiment = "positivo"
            self.lead_info["property_type"] = "casa" if "casa" in message_lower else "apartamento"
            intent = "property_info"
        elif "r$" in message_lower or any(char.isdigit() for char in message):
            sentiment = "positivo"
            # Extrai valor aproximado
            import re
            numbers = re.findall(r'\d+', message)
            if numbers:
                self.lead_info["bill_value"] = numbers[0]
            intent = "bill_value"
        else:
            sentiment = "neutro"
            intent = "general"
        
        # Determina próximo estágio
        next_stage = self.current_stage
        if intent == "no_interest":
            next_stage = "CLOSED"
        elif intent == "interest" and self.current_stage == "INITIAL_CONTACT":
            next_stage = "IDENTIFICATION"
        elif intent == "property_info":
            next_stage = "DISCOVERY"
        elif intent == "bill_value":
            next_stage = "QUALIFICATION"
        elif self.current_stage == "QUALIFICATION" and sentiment == "positivo":
            next_stage = "SCHEDULING"
        
        return {
            "sentiment": sentiment,
            "intent": intent,
            "next_stage": next_stage,
            "confidence": 0.85
        }
    
    async def process_message(
        self, 
        message: str,
        phone_number: str,
        media_type: Optional[str] = None,
        media_data: Optional[Any] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Processa mensagem e retorna resposta demo"""
        try:
            # Inicializa histórico se necessário
            if phone_number not in self.conversation_history:
                self.conversation_history[phone_number] = []
            
            # Analisa mensagem
            analysis = self._analyze_message(message)
            self.current_stage = analysis["next_stage"]
            
            # Gera resposta apropriada
            if analysis["intent"] == "no_interest":
                response = self._get_demo_response("no_interest")
            elif analysis["intent"] == "interest":
                response = self._get_demo_response("interest")
            elif analysis["intent"] == "cost_concern":
                response = self._get_demo_response("cost_concern")
            elif analysis["intent"] == "how_it_works":
                response = self._get_demo_response("how_it_works")
            elif analysis["intent"] == "property_info" and "property_type" in self.lead_info:
                response = self._get_demo_response("property_info", 
                    property_type=self.lead_info["property_type"])
            elif analysis["intent"] == "bill_value" and "bill_value" in self.lead_info:
                value = int(self.lead_info.get("bill_value", 500))
                savings = int(value * 0.05)  # 5% da conta atual
                yearly = int(value * 0.95 * 12)  # Economia anual
                months = int(yearly / value)
                response = self._get_demo_response("bill_value", 
                    value=value, savings=savings, yearly=yearly, months=months)
            elif self.current_stage == "SCHEDULING":
                response = self._get_demo_response("scheduling")
            else:
                response = self._get_demo_response("default")
            
            # Salva no histórico
            self.conversation_history[phone_number].append({
                "user": message,
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Prepara metadados
            metadata = {
                "stage": self.current_stage,
                "sentiment": analysis["sentiment"],
                "intent": analysis["intent"],
                "lead_info": self.lead_info,
                "typing_delay": calculate_typing_delay(response),
                "demo_mode": True
            }
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Erro no demo agent: {e}")
            return "Desculpe, tive um problema. Pode repetir?", {"error": str(e)}
    
    async def start_conversation(self, phone_number: str) -> Tuple[str, Dict[str, Any]]:
        """Inicia nova conversa demo"""
        self.current_stage = "INITIAL_CONTACT"
        self.lead_info = {"phone": format_phone_number(phone_number)}
        
        greeting = self._get_demo_response("greeting")
        
        metadata = {
            "stage": self.current_stage,
            "typing_delay": calculate_typing_delay(greeting),
            "is_new_conversation": True,
            "demo_mode": True
        }
        
        return greeting, metadata
    
    async def handle_no_interest(self, phone_number: str) -> Tuple[str, Dict[str, Any]]:
        """Trata casos de não interesse"""
        farewell = self._get_demo_response("no_interest")
        
        self.lead_info["interested"] = False
        self.lead_info["closed_at"] = datetime.now().isoformat()
        
        metadata = {
            "stage": "CLOSED",
            "lead_qualified": False,
            "reason": "no_interest",
            "demo_mode": True
        }
        
        return farewell, metadata
    
    def get_conversation_summary(self, phone_number: str) -> Dict[str, Any]:
        """Retorna resumo da conversa"""
        return {
            "phone": phone_number,
            "lead_info": self.lead_info,
            "current_stage": self.current_stage,
            "conversation_count": len(self.conversation_history.get(phone_number, [])),
            "demo_mode": True
        }


# Função helper
def create_demo_agent() -> DemoSDRAgent:
    """Cria e retorna uma instância do agente demo"""
    return DemoSDRAgent()

__all__ = ["DemoSDRAgent", "create_demo_agent"]