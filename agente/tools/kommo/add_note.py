"""
Tool para adicionar notas e comentários a leads no Kommo CRM
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from agno.tools import tool
from loguru import logger

from ...services.kommo_service import get_kommo_service, KommoAPIError


@tool(show_result=True)
async def add_kommo_note(
    lead_id: int,
    text: str,
    note_type: str = "common"
) -> Dict[str, Any]:
    """
    Adiciona uma nota/comentário a um lead no Kommo CRM.
    
    Args:
        lead_id: ID do lead no Kommo
        text: Texto da nota/comentário
        note_type: Tipo da nota (padrão: "common")
        
    Returns:
        Dict contendo:
            - success: bool indicando sucesso
            - note_id: ID da nota criada
            - lead_id: ID do lead
            - created_at: timestamp de criação
            - error: mensagem de erro (se houver)
    """
    try:
        logger.info(f"Adicionando nota ao lead {lead_id}")
        
        # Validar entrada
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Texto da nota não pode estar vazio",
                "note_id": None,
                "lead_id": lead_id,
                "created_at": None
            }
        
        # Obter instância do serviço
        kommo = get_kommo_service()
        
        # Verificar se lead existe
        try:
            lead = await kommo.get_lead(lead_id)
            lead_name = lead.get('name', 'Lead sem nome')
        except KommoAPIError as e:
            if e.status_code == 404:
                return {
                    "success": False,
                    "error": f"Lead {lead_id} não encontrado",
                    "note_id": None,
                    "lead_id": lead_id,
                    "created_at": None
                }
            raise
        
        # Adicionar timestamp à nota
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        formatted_text = f"[{timestamp}] {text}"
        
        # Adicionar nota
        note = await kommo.add_note(lead_id, formatted_text)
        
        logger.success(f"Nota adicionada ao lead {lead_id} (ID da nota: {note.get('id')})")
        
        return {
            "success": True,
            "note_id": note.get('id'),
            "lead_id": lead_id,
            "lead_name": lead_name,
            "created_at": note.get('created_at'),
            "text": text,
            "message": f"Nota adicionada com sucesso ao lead '{lead_name}'"
        }
        
    except KommoAPIError as e:
        logger.error(f"Erro da API do Kommo ao adicionar nota: {e}")
        return {
            "success": False,
            "note_id": None,
            "lead_id": lead_id,
            "created_at": None,
            "error": f"Erro da API do Kommo: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao adicionar nota: {e}")
        return {
            "success": False,
            "note_id": None,
            "lead_id": lead_id,
            "created_at": None,
            "error": f"Erro inesperado: {str(e)}"
        }


@tool(show_result=True)
async def add_qualification_note(
    lead_id: int,
    qualification_data: Dict[str, Any],
    score: Optional[int] = None
) -> Dict[str, Any]:
    """
    Adiciona uma nota de qualificação estruturada a um lead.
    
    Args:
        lead_id: ID do lead no Kommo
        qualification_data: Dados de qualificação (dict com campos como urgency, budget, etc)
        score: Score de qualificação (0-100)
        
    Returns:
        Dict contendo resultado da operação
    """
    try:
        logger.info(f"Adicionando nota de qualificação ao lead {lead_id}")
        
        # Formatar nota de qualificação
        note_lines = ["📋 QUALIFICAÇÃO DO LEAD"]
        note_lines.append("=" * 30)
        
        # Score de qualificação
        if score is not None:
            emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
            note_lines.append(f"{emoji} Score: {score}/100")
            note_lines.append("")
        
        # Dados de qualificação
        field_mapping = {
            "name": "👤 Nome",
            "email": "📧 Email",
            "phone": "📱 Telefone",
            "property_type": "🏠 Tipo de Imóvel",
            "address": "📍 Endereço",
            "bill_value": "💰 Valor da Conta",
            "consumption_kwh": "⚡ Consumo (kWh)",
            "urgency": "🚨 Urgência",
            "decision_maker": "✅ Tomador de Decisão",
            "has_discount": "💳 Possui Desconto",
            "interested": "💚 Interesse",
            "objections": "❌ Objeções"
        }
        
        for key, label in field_mapping.items():
            if key in qualification_data and qualification_data[key] is not None:
                value = qualification_data[key]
                
                # Formatação especial para alguns campos
                if key == "bill_value":
                    value = f"R$ {value:,.2f}"
                elif key == "consumption_kwh":
                    value = f"{value} kWh/mês"
                elif key == "urgency":
                    value = value.upper()
                elif key == "decision_maker":
                    value = "Sim" if value else "Não"
                elif key == "has_discount":
                    value = "Sim" if value else "Não"
                elif key == "interested":
                    value = "Sim" if value else "Não"
                elif key == "objections" and isinstance(value, list):
                    value = ", ".join(value) if value else "Nenhuma"
                
                note_lines.append(f"{label}: {value}")
        
        # Adicionar timestamp
        note_lines.append("")
        note_lines.append(f"🕐 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Criar texto da nota
        note_text = "\n".join(note_lines)
        
        # Usar a função base para adicionar a nota
        result = await add_kommo_note(lead_id, note_text)
        
        if result["success"]:
            result["message"] = "Nota de qualificação adicionada com sucesso"
            result["qualification_score"] = score
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao adicionar nota de qualificação: {e}")
        return {
            "success": False,
            "note_id": None,
            "lead_id": lead_id,
            "created_at": None,
            "error": f"Erro ao adicionar nota de qualificação: {str(e)}"
        }


@tool(show_result=True)
async def add_interaction_log(
    lead_id: int,
    interaction_type: str,
    details: str,
    sentiment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Adiciona um log de interação ao lead (chamada, mensagem, reunião, etc).
    
    Args:
        lead_id: ID do lead no Kommo
        interaction_type: Tipo de interação (call, message, meeting, email)
        details: Detalhes da interação
        sentiment: Sentimento da interação (positive, neutral, negative)
        
    Returns:
        Dict contendo resultado da operação
    """
    try:
        logger.info(f"Adicionando log de interação ao lead {lead_id}")
        
        # Mapear tipos de interação para emojis
        type_emojis = {
            "call": "📞",
            "message": "💬",
            "whatsapp": "📱",
            "meeting": "🤝",
            "email": "📧",
            "task": "📋"
        }
        
        # Mapear sentimentos para emojis
        sentiment_emojis = {
            "positive": "😊",
            "neutral": "😐",
            "negative": "😟"
        }
        
        # Construir nota
        emoji = type_emojis.get(interaction_type.lower(), "📝")
        sentiment_emoji = sentiment_emojis.get(sentiment, "") if sentiment else ""
        
        note_text = f"{emoji} {interaction_type.upper()}"
        if sentiment_emoji:
            note_text += f" {sentiment_emoji}"
        
        note_text += f"\n\n{details}"
        
        # Usar a função base para adicionar a nota
        result = await add_kommo_note(lead_id, note_text)
        
        if result["success"]:
            result["interaction_type"] = interaction_type
            result["sentiment"] = sentiment
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao adicionar log de interação: {e}")
        return {
            "success": False,
            "note_id": None,
            "lead_id": lead_id,
            "created_at": None,
            "error": f"Erro ao adicionar log de interação: {str(e)}"
        }


# Exportar tools
AddKommoNoteTool = add_kommo_note
AddQualificationNoteTool = add_qualification_note
AddInteractionLogTool = add_interaction_log