"""
Gemini Direct Implementation
===========================
Implementação direta do Google Gemini sem usar AGnO
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from google import genai
from loguru import logger
from pydantic import BaseModel
import base64
from PIL import Image
import io

# Criar cliente do novo SDK
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiConfig(BaseModel):
    """Configuração do Gemini"""
    model_name: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.95
    top_k: int = 40


class GeminiAgent:
    """Agente Gemini Direto"""
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or GeminiConfig()
        self.client = client
        self.model_name = self.config.model_name
        self.generation_config = {
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "top_k": self.config.top_k,
            "max_output_tokens": self.config.max_tokens,
        }
        self.chat = None
        self.history = []
    
    def start_chat(self, system_prompt: str = ""):
        """Inicia uma nova conversa"""
        # No novo SDK, o chat é mantido via histórico de mensagens
        self.history = []
        if system_prompt:
            # Adicionar prompt do sistema como primeira mensagem
            self.history.append({
                "role": "system",
                "content": system_prompt,
                "timestamp": datetime.now().isoformat()
            })
        return self
    
    async def send_message(
        self, 
        message: str, 
        images: Optional[List[Union[str, bytes, Image.Image]]] = None,
        role: str = "user"
    ) -> str:
        """Envia mensagem para o Gemini"""
        try:
            # Preparar conteúdo
            contents = [message]
            
            # Adicionar imagens se houver
            if images:
                for img in images:
                    if isinstance(img, str):
                        # Se for path ou base64
                        if img.startswith('data:image'):
                            # É base64
                            base64_data = img.split(',')[1]
                            img_bytes = base64.b64decode(base64_data)
                            img = Image.open(io.BytesIO(img_bytes))
                        else:
                            # É path
                            img = Image.open(img)
                    elif isinstance(img, bytes):
                        img = Image.open(io.BytesIO(img))
                    
                    contents.append(img)
            
            # Construir mensagens para o novo SDK
            messages = []
            
            # Adicionar histórico anterior se houver
            for hist in self.history:
                if hist["role"] != "system":
                    messages.append({
                        "role": hist["role"] if hist["role"] != "assistant" else "model",
                        "parts": [{"text": hist["content"]}]
                    })
                else:
                    # System prompt é adicionado como primeira mensagem do usuário
                    messages.append({
                        "role": "user",
                        "parts": [{"text": f"SISTEMA: {hist['content']}"}]
                    })
                    messages.append({
                        "role": "model",
                        "parts": [{"text": "Entendido. Vou seguir essas instruções."}]
                    })
            
            # Adicionar mensagem atual
            current_parts = [{"text": message}]
            if images:
                for img in images:
                    if isinstance(img, Image.Image):
                        # Converter PIL Image para bytes
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        img_bytes = img_byte_arr.getvalue()
                        current_parts.append({"inline_data": {"mime_type": "image/png", "data": base64.b64encode(img_bytes).decode()}})
            
            messages.append({
                "role": "user",
                "parts": current_parts
            })
            
            # Gerar resposta usando o novo SDK
            response = await self.client.models.generate_content_async(
                model=self.model_name,
                contents=messages,
                config=self.generation_config
            )
            
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Salvar no histórico
            self.history.append({
                "role": role,
                "content": message,
                "has_images": bool(images),
                "timestamp": datetime.now().isoformat()
            })
            
            self.history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            return response_text
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para Gemini: {e}")
            raise
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Retorna o histórico da conversa"""
        return self.history
    
    def clear_history(self):
        """Limpa o histórico"""
        self.history = []


# Função helper para criar agente compatível com a interface antiga
def create_gemini_agent(
    system_prompt: str,
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> GeminiAgent:
    """Cria um agente Gemini com as configurações especificadas"""
    config = GeminiConfig(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    agent = GeminiAgent(config)
    agent.start_chat(system_prompt)
    
    return agent