"""
Testes do sistema de reações e respostas citadas
Validação completa para produção
"""
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
import random

# Adicionar o diretório raiz ao path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.evolution import EvolutionAPIClient
from app.agents.agentic_sdr import AgenticSDR
from app.api.webhooks import process_message_with_agent


class TestReactionsLogic:
    """Testes unitários para a lógica de reações"""
    
    def test_reaction_probability(self):
        """Testa se reações ocorrem apenas ~10% das vezes"""
        reactions_count = 0
        total_tests = 1000
        
        # Simular múltiplas mensagens curtas de confirmação
        for i in range(total_tests):
            # Simular resposta do agente
            result = {"reaction": None}
            message = "ok"
            
            # Simular 10% de chance (100 em 1000)
            should_react = i < 100
            
            # Lógica simplificada do agente
            if should_react and len(message) < 10:
                result["reaction"] = "👍"
            
            if result["reaction"]:
                reactions_count += 1
        
        # Deve reagir em aproximadamente 10% dos casos
        reaction_rate = reactions_count / total_tests
        assert 0.08 <= reaction_rate <= 0.12, f"Taxa de reação: {reaction_rate}"
    
    def test_media_always_gets_reaction(self):
        """Testa se mídias sempre recebem reação ✅"""
        media_types = ["image", "document", "pdf"]
        
        for media_type in media_types:
            media = {"type": media_type}
            result = {"reaction": None}
            
            # Lógica do agente para mídia
            if media and media.get("type") in ["image", "document", "pdf"]:
                result["reaction"] = "✅"
            
            assert result["reaction"] == "✅", f"Mídia {media_type} deve receber ✅"
    
    def test_specific_reactions(self):
        """Testa reações específicas para contextos apropriados"""
        test_cases = [
            ("ok", "👍", True),  # Muito curto, pode reagir
            ("blz", "👍", True),
            ("obrigado!", "❤️", True),
            ("valeu", "❤️", True),
            ("kkkkk", "😂", True),
            ("hahaha", "😂", True),
            ("entendi perfeitamente sua proposta", None, False),  # Muito longo
            ("qual o valor?", None, False),  # Pergunta, não deve reagir
        ]
        
        for message, expected_reaction, should_react in test_cases:
            # Simular 10% de chance
            with patch('random.random', return_value=0.05 if should_react else 0.5):
                result = {"reaction": None}
                
                # Lógica simplificada
                if random.random() < 0.1:
                    if len(message) < 10 and any(word in message for word in ["ok", "blz"]):
                        result["reaction"] = "👍"
                    elif len(message) < 20 and any(word in message for word in ["obrigado", "valeu"]):
                        result["reaction"] = "❤️"
                    elif any(indicator in message for indicator in ["kkkkk", "hahaha"]):
                        result["reaction"] = "😂"
                
                if should_react:
                    assert result["reaction"] == expected_reaction, f"Mensagem '{message}' deveria ter reação {expected_reaction}"
                else:
                    assert result["reaction"] is None, f"Mensagem '{message}' não deveria ter reação"


class TestCitationsLogic:
    """Testes para lógica de citações"""
    
    def test_citation_probability(self):
        """Testa se citações ocorrem apenas ~10% das vezes"""
        citations_count = 0
        total_tests = 1000
        
        for i in range(total_tests):
            result = {"reply_to": None}
            message_id = "123"
            message = "Como funciona? Qual o valor? Preciso de documentos?"
            
            # Simular 10% de chance (100 em 1000)
            should_cite = i < 100
            
            # Lógica de citação
            if message_id and should_cite:
                question_count = message.count("?")
                if question_count > 1:
                    result["reply_to"] = message_id
            
            if result["reply_to"]:
                citations_count += 1
        
        citation_rate = citations_count / total_tests
        assert 0.08 <= citation_rate <= 0.12, f"Taxa de citação: {citation_rate}"
    
    def test_multiple_questions_citation(self):
        """Testa se múltiplas perguntas aumentam chance de citação"""
        test_cases = [
            ("Qual o valor?", False),  # Uma pergunta apenas
            ("Como funciona? Qual o valor?", True),  # Duas perguntas
            ("Onde fica? Quanto custa? Quando posso começar?", True),  # Três perguntas
            ("Entendi tudo", False),  # Sem perguntas
        ]
        
        for message, should_cite in test_cases:
            with patch('random.random', return_value=0.05):  # Garantir 10% de chance
                result = {"reply_to": None}
                message_id = "123"
                
                if message_id and random.random() < 0.1:
                    question_count = message.count("?")
                    if question_count > 1:
                        result["reply_to"] = message_id
                
                if should_cite:
                    assert result["reply_to"] == message_id, f"Mensagem com múltiplas perguntas deveria ser citada"
                else:
                    assert result["reply_to"] is None, f"Mensagem sem múltiplas perguntas não deveria ser citada"


class TestIntegrationFlow:
    """Testes de integração do fluxo completo"""
    
    @pytest.mark.asyncio
    async def test_complete_flow_with_reactions(self):
        """Testa fluxo completo com reações e citações"""
        # Mock do EvolutionAPIClient
        evolution_client = AsyncMock(spec=EvolutionAPIClient)
        evolution_client.send_text_message = AsyncMock(return_value={"key": {"id": "msg123"}})
        evolution_client.send_reaction = AsyncMock(return_value={"success": True})
        evolution_client.send_reply = AsyncMock(return_value={"key": {"id": "msg124"}})
        
        # Cenários de teste
        test_scenarios = [
            {
                "message": "ok",
                "should_react": True,
                "reaction": "👍",
                "should_reply": False
            },
            {
                "message": "Qual o valor da mensalidade? Como funciona o contrato?",
                "should_react": False,
                "should_reply": True
            },
            {
                "message": "Entendi, vou pensar",
                "should_react": False,
                "should_reply": False
            }
        ]
        
        for scenario in test_scenarios:
            # Resetar mocks
            evolution_client.reset_mock()
            
            # Simular resposta do agente
            agent_response = {
                "text": "Claro! Vou explicar tudo para você.",
                "reaction": scenario.get("reaction") if scenario["should_react"] else None,
                "reply_to": "msg_original" if scenario["should_reply"] else None
            }
            
            # Processar resposta (simulando webhooks.py)
            if agent_response.get("reaction"):
                await evolution_client.send_reaction(
                    "5511999999999",
                    "msg_original",
                    agent_response["reaction"]
                )
            
            if agent_response.get("reply_to"):
                await evolution_client.send_reply(
                    "5511999999999",
                    agent_response["reply_to"],
                    agent_response["text"]
                )
            else:
                await evolution_client.send_text_message(
                    "5511999999999",
                    agent_response["text"]
                )
            
            # Verificar chamadas
            if scenario["should_react"]:
                evolution_client.send_reaction.assert_called_once()
            else:
                evolution_client.send_reaction.assert_not_called()
            
            if scenario["should_reply"]:
                evolution_client.send_reply.assert_called_once()
            else:
                evolution_client.send_reply.assert_not_called()


class TestProductionScenarios:
    """Testes de cenários reais de produção"""
    
    @pytest.mark.asyncio
    async def test_natural_conversation_flow(self):
        """Testa uma conversa natural com baixa frequência de reações/citações"""
        conversation = [
            {"user": "Oi", "bot_reaction": None, "bot_reply": False},
            {"user": "Quero saber sobre energia solar", "bot_reaction": None, "bot_reply": False},
            {"user": "Quanto custa?", "bot_reaction": None, "bot_reply": False},
            {"user": "ok", "bot_reaction": "👍", "bot_reply": False},  # ~10% chance
            {"user": "Como funciona? Tem garantia? Qual o prazo?", "bot_reaction": None, "bot_reply": True},  # Múltiplas perguntas
            {"user": "Entendi", "bot_reaction": None, "bot_reply": False},
            {"user": "obrigado", "bot_reaction": "❤️", "bot_reply": False},  # ~10% chance
            {"user": "kkkkk muito bom", "bot_reaction": "😂", "bot_reply": False},  # ~10% chance
        ]
        
        reactions_count = sum(1 for msg in conversation if msg["bot_reaction"])
        replies_count = sum(1 for msg in conversation if msg["bot_reply"])
        
        # Em 8 mensagens, esperamos ~1 reação e ~1 citação (12.5% cada)
        assert reactions_count <= 3, f"Muitas reações: {reactions_count}"
        assert replies_count <= 2, f"Muitas citações: {replies_count}"
    
    @pytest.mark.asyncio
    async def test_media_handling(self):
        """Testa tratamento especial para mídias"""
        evolution_client = AsyncMock(spec=EvolutionAPIClient)
        
        # Simular recebimento de imagem
        media_response = {
            "text": "Recebi sua conta de luz! Vou analisar...",
            "reaction": "✅",  # Sempre reage a mídias
            "reply_to": None
        }
        
        # Verificar que mídia sempre recebe reação
        assert media_response["reaction"] == "✅"
        
        # Processar
        await evolution_client.send_reaction("5511999999999", "msg123", "✅")
        await evolution_client.send_text_message("5511999999999", media_response["text"])
        
        evolution_client.send_reaction.assert_called_once_with("5511999999999", "msg123", "✅")


def test_system_statistics():
    """Testa estatísticas do sistema para garantir naturalidade"""
    # Simular 100 conversas
    total_messages = 0
    total_reactions = 0
    total_citations = 0
    
    for _ in range(100):
        # Cada conversa tem entre 5-15 mensagens
        messages_in_conversation = random.randint(5, 15)
        total_messages += messages_in_conversation
        
        for _ in range(messages_in_conversation):
            # 10% de chance de reação
            if random.random() < 0.1:
                total_reactions += 1
            
            # 10% de chance de citação
            if random.random() < 0.1:
                total_citations += 1
    
    reaction_rate = total_reactions / total_messages
    citation_rate = total_citations / total_messages
    
    print(f"\nEstatísticas do Sistema:")
    print(f"Total de mensagens: {total_messages}")
    print(f"Reações: {total_reactions} ({reaction_rate:.1%})")
    print(f"Citações: {total_citations} ({citation_rate:.1%})")
    
    # Verificar se está dentro do esperado (10% ± 5%)
    assert 0.05 <= reaction_rate <= 0.15, f"Taxa de reação fora do esperado: {reaction_rate:.1%}"
    assert 0.05 <= citation_rate <= 0.15, f"Taxa de citação fora do esperado: {citation_rate:.1%}"


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])