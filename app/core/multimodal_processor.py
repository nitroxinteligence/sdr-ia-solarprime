"""
Multimodal Processor - Processamento SIMPLES de mídia
ZERO complexidade, funcionalidade total
"""

from typing import Dict, Any, Optional, List
import base64
import io
import asyncio
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
import PyPDF2
from docx import Document
from app.utils.logger import emoji_logger
from app.config import settings

class MultimodalProcessor:
    """
    Processador SIMPLES de mídia (imagens, áudio, documentos)
    Mantém 100% da funcionalidade multimodal
    """
    
    def __init__(self):
        self.enabled = settings.enable_multimodal_analysis
        self.is_initialized = False
        
    def initialize(self):
        """Inicialização simples"""
        if self.is_initialized:
            return
            
        if self.enabled:
            emoji_logger.system_ready("🎨 MultimodalProcessor habilitado")
        else:
            emoji_logger.system_warning("🎨 MultimodalProcessor desabilitado")
            
        self.is_initialized = True
    
    async def process_media(self, media_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mídia de forma SIMPLES e DIRETA
        
        Args:
            media_data: Dados da mídia com type e content
            
        Returns:
            Resultado do processamento
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "Processamento multimodal desabilitado"
            }
        
        media_type = media_data.get("type", "").lower()
        content = media_data.get("content", "")
        
        try:
            if media_type == "image":
                return await self.process_image(content)
            elif media_type in ["audio", "voice"]:
                return await self.process_audio(content)
            elif media_type == "document":
                return await self.process_document(content)
            else:
                return {
                    "success": False,
                    "message": f"Tipo de mídia não suportado: {media_type}"
                }
        except Exception as e:
            emoji_logger.service_error(f"Erro ao processar mídia: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar mídia: {str(e)}"
            }
    
    async def process_image(self, image_data: str) -> Dict[str, Any]:
        """
        Processa imagem com OCR
        
        Args:
            image_data: Base64 da imagem
            
        Returns:
            Texto extraído e análise
        """
        try:
            # Decodificar base64
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # OCR com Tesseract
            text = ""
            enable_ocr = getattr(settings, 'enable_ocr', True)  # Default True se não existir
            if enable_ocr:
                try:
                    text = pytesseract.image_to_string(image, lang='por')
                    emoji_logger.multimodal_event(f"📸 OCR extraiu {len(text)} caracteres")
                except Exception as ocr_error:
                    emoji_logger.system_warning(f"OCR falhou: {ocr_error}")
            
            # Análise básica da imagem
            width, height = image.size
            format_img = image.format or "unknown"
            
            result = {
                "success": True,
                "type": "image",
                "text": text.strip() if text else "",
                "metadata": {
                    "width": width,
                    "height": height,
                    "format": format_img
                },
                "analysis": self._analyze_image_content(text)
            }
            
            emoji_logger.multimodal_event(f"✅ Imagem processada: {width}x{height}")
            return result
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao processar imagem: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar imagem: {str(e)}"
            }
    
    async def process_audio(self, audio_data: str) -> Dict[str, Any]:
        """
        Processa áudio com transcrição
        
        Args:
            audio_data: Base64 do áudio
            
        Returns:
            Transcrição do áudio
        """
        try:
            # Decodificar base64
            if "base64," in audio_data:
                audio_data = audio_data.split("base64,")[1]
            
            audio_bytes = base64.b64decode(audio_data)
            
            # Converter para formato processável
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            # Exportar como WAV para transcrição
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            
            # Transcrever com SpeechRecognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_buffer) as source:
                audio_record = recognizer.record(source)
                text = recognizer.recognize_google(audio_record, language="pt-BR")
            
            result = {
                "success": True,
                "type": "audio",
                "text": text,
                "metadata": {
                    "duration": len(audio) / 1000.0,  # Em segundos
                    "channels": audio.channels,
                    "sample_rate": audio.frame_rate
                }
            }
            
            emoji_logger.multimodal_event(f"🎤 Áudio transcrito: {len(text)} caracteres")
            return result
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao processar áudio: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar áudio: {str(e)}"
            }
    
    async def process_document(self, doc_data: str) -> Dict[str, Any]:
        """
        Processa documento (PDF, DOCX)
        
        Args:
            doc_data: Base64 do documento
            
        Returns:
            Texto extraído do documento
        """
        try:
            # Decodificar base64
            if "base64," in doc_data:
                doc_data = doc_data.split("base64,")[1]
            
            doc_bytes = base64.b64decode(doc_data)
            doc_buffer = io.BytesIO(doc_bytes)
            
            # Detectar tipo e processar
            text = ""
            doc_type = "unknown"
            
            # Tentar como PDF
            try:
                pdf_reader = PyPDF2.PdfReader(doc_buffer)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                doc_type = "pdf"
            except:
                # Tentar como DOCX
                try:
                    doc_buffer.seek(0)
                    doc = Document(doc_buffer)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    doc_type = "docx"
                except:
                    pass
            
            if text:
                result = {
                    "success": True,
                    "type": "document",
                    "text": text,
                    "metadata": {
                        "doc_type": doc_type,
                        "char_count": len(text)
                    }
                }
                emoji_logger.multimodal_event(f"📄 Documento processado: {doc_type}")
                return result
            else:
                return {
                    "success": False,
                    "message": "Não foi possível extrair texto do documento"
                }
                
        except Exception as e:
            emoji_logger.system_error(f"Erro ao processar documento: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar documento: {str(e)}"
            }
    
    def _analyze_image_content(self, text: str) -> Dict[str, Any]:
        """
        Análise simples do conteúdo da imagem
        
        Args:
            text: Texto extraído por OCR
            
        Returns:
            Análise do conteúdo
        """
        analysis = {
            "has_text": bool(text and text.strip()),
            "is_bill": False,
            "bill_value": None
        }
        
        if text:
            # Verificar se é conta de luz
            bill_keywords = ["energia", "kwh", "consumo", "fatura", "conta"]
            text_lower = text.lower()
            
            if any(keyword in text_lower for keyword in bill_keywords):
                analysis["is_bill"] = True
                
                # Tentar extrair valor
                import re
                value_pattern = r"R\$?\s*(\d+[.,]\d{2})"
                matches = re.findall(value_pattern, text)
                if matches:
                    try:
                        # Pegar o maior valor (provavelmente o total)
                        values = [float(m.replace(",", ".")) for m in matches]
                        analysis["bill_value"] = max(values)
                    except:
                        pass
        
        return analysis
    
    def get_supported_types(self) -> List[str]:
        """Retorna tipos de mídia suportados"""
        return ["image", "audio", "voice", "document", "pdf", "docx"]
    
    def is_enabled(self) -> bool:
        """Verifica se o processamento multimodal está habilitado"""
        return self.enabled