"""
Serviço de mensagens para Evolution API v2
Gerencia envio de mensagens de texto, reações e localização
"""

import re
from typing import Optional, Dict, Any, List
from loguru import logger

from .client import EvolutionClient
from .types import (
    TextMessage,
    ReactionMessage,
    LocationMessage,
    MessageResponse,
    MessageKey
)
from agente.utils.formatters import format_phone_number


class MessageService:
    """
    Serviço para gerenciar mensagens
    
    Responsabilidades:
    - Envio de mensagens de texto
    - Chunking inteligente de mensagens longas
    - Envio de reações
    - Envio de localização
    """
    
    def __init__(self, client: EvolutionClient):
        """
        Inicializa serviço de mensagens
        
        Args:
            client: Cliente HTTP Evolution API
        """
        self.client = client
        self.max_message_length = 4096  # Limite do WhatsApp
        self.chunk_size = 3000  # Tamanho ideal para chunks
    
    async def send_text(
        self,
        phone: str,
        text: str,
        delay: int = 0,
        link_preview: bool = False
    ) -> Optional[MessageResponse]:
        """
        Envia mensagem de texto
        
        Args:
            phone: Número do destinatário
            text: Texto da mensagem
            delay: Delay em segundos antes de enviar
            link_preview: Se deve mostrar preview de links
            
        Returns:
            MessageResponse com resultado ou None em erro
        """
        # Formata número
        formatted_phone = format_phone_number(phone)
        
        # Se mensagem é muito longa, divide em chunks
        if len(text) > self.chunk_size:
            logger.info(
                f"Message too long, will send in chunks",
                phone=formatted_phone,
                text_length=len(text),
                chunk_size=self.chunk_size
            )
            return await self._send_chunked_message(
                formatted_phone, text, delay, link_preview
            )
        
        # Cria mensagem
        message = TextMessage(
            number=formatted_phone,
            text=text,
            delay=delay,
            linkPreview=link_preview
        )
        
        logger.info(
            f"Sending text message",
            phone=formatted_phone,
            text_length=len(text),
            delay=delay
        )
        
        # Envia mensagem
        response = await self.client.post(
            self.client.instance_endpoint("/message/sendText"),
            data=message.to_dict()
        )
        
        if response:
            msg_response = MessageResponse.from_dict(response)
            logger.info(
                f"Message sent successfully",
                phone=formatted_phone,
                message_id=msg_response.key.id
            )
            return msg_response
        else:
            logger.error(
                f"Failed to send message",
                phone=formatted_phone
            )
            return None
    
    async def _send_chunked_message(
        self,
        phone: str,
        text: str,
        base_delay: int,
        link_preview: bool
    ) -> Optional[MessageResponse]:
        """
        Envia mensagem dividida em chunks
        
        Args:
            phone: Número formatado
            text: Texto completo
            base_delay: Delay base
            link_preview: Preview de links
            
        Returns:
            Resposta do último chunk ou None
        """
        # Divide texto em chunks naturais
        chunks = self._split_text_naturally(text)
        
        logger.info(
            f"Sending message in {len(chunks)} chunks",
            phone=phone,
            total_length=len(text)
        )
        
        last_response = None
        
        for i, chunk in enumerate(chunks):
            # Delay progressivo para chunks
            chunk_delay = base_delay + (i * 2)
            
            # Envia chunk
            message = TextMessage(
                number=phone,
                text=chunk.strip(),
                delay=chunk_delay,
                linkPreview=link_preview and i == 0  # Preview só no primeiro
            )
            
            response = await self.client.post(
                self.client.instance_endpoint("/message/sendText"),
                data=message.to_dict()
            )
            
            if response:
                last_response = MessageResponse.from_dict(response)
                logger.debug(
                    f"Chunk {i+1}/{len(chunks)} sent",
                    phone=phone,
                    chunk_length=len(chunk)
                )
            else:
                logger.error(
                    f"Failed to send chunk {i+1}/{len(chunks)}",
                    phone=phone
                )
                break
        
        return last_response
    
    def _split_text_naturally(self, text: str) -> List[str]:
        """
        Divide texto em pontos naturais
        
        Args:
            text: Texto para dividir
            
        Returns:
            Lista de chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Divide por sentenças
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            # Se sentença é muito longa, divide por quebras menores
            if len(sentence) > self.chunk_size:
                # Força divisão da sentença longa
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # Divide sentença em pedaços menores
                words = sentence.split()
                temp_chunk = ""
                
                for word in words:
                    if len(temp_chunk) + len(word) + 1 > self.chunk_size:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = word
                        else:
                            # Palavra muito longa, força quebra
                            chunks.append(word[:self.chunk_size])
                            temp_chunk = word[self.chunk_size:]
                    else:
                        temp_chunk += (" " if temp_chunk else "") + word
                
                if temp_chunk:
                    current_chunk = temp_chunk
            else:
                # Sentença normal
                if len(current_chunk) + len(sentence) + 1 > self.chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        chunks.append(sentence)
                else:
                    current_chunk += (" " if current_chunk else "") + sentence
        
        # Adiciona último chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Remove chunks vazios
        return [chunk for chunk in chunks if chunk.strip()]
    
    async def send_reaction(
        self,
        phone: str,
        message_id: str,
        reaction: str
    ) -> Optional[MessageResponse]:
        """
        Envia reação a uma mensagem
        
        Args:
            phone: Número do destinatário
            message_id: ID da mensagem para reagir
            reaction: Emoji da reação
            
        Returns:
            MessageResponse ou None
        """
        # Formata número
        formatted_phone = format_phone_number(phone)
        
        # Cria reação
        reaction_msg = ReactionMessage(
            number=formatted_phone,
            reaction=reaction,
            msgId=message_id
        )
        
        logger.info(
            f"Sending reaction",
            phone=formatted_phone,
            message_id=message_id,
            reaction=reaction
        )
        
        # Envia reação
        response = await self.client.post(
            self.client.instance_endpoint("/message/sendReaction"),
            data=reaction_msg.to_dict()
        )
        
        if response:
            msg_response = MessageResponse.from_dict(response)
            logger.info(
                f"Reaction sent successfully",
                phone=formatted_phone,
                reaction=reaction
            )
            return msg_response
        else:
            logger.error(
                f"Failed to send reaction",
                phone=formatted_phone
            )
            return None
    
    async def send_location(
        self,
        phone: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None
    ) -> Optional[MessageResponse]:
        """
        Envia localização
        
        Args:
            phone: Número do destinatário
            latitude: Latitude
            longitude: Longitude
            name: Nome do local (opcional)
            
        Returns:
            MessageResponse ou None
        """
        # Formata número
        formatted_phone = format_phone_number(phone)
        
        # Cria localização
        location_msg = LocationMessage(
            number=formatted_phone,
            latitude=latitude,
            longitude=longitude,
            name=name
        )
        
        logger.info(
            f"Sending location",
            phone=formatted_phone,
            latitude=latitude,
            longitude=longitude,
            name=name
        )
        
        # Envia localização
        response = await self.client.post(
            self.client.instance_endpoint("/message/sendLocation"),
            data=location_msg.to_dict()
        )
        
        if response:
            msg_response = MessageResponse.from_dict(response)
            logger.info(
                f"Location sent successfully",
                phone=formatted_phone,
                message_id=msg_response.key.id
            )
            return msg_response
        else:
            logger.error(
                f"Failed to send location",
                phone=formatted_phone
            )
            return None