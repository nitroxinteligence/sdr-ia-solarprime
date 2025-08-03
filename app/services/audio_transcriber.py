"""
Audio Transcription Service - Transcreve áudios do WhatsApp usando SpeechRecognition
"""
import speech_recognition as sr
from pydub import AudioSegment
import io
import base64
from typing import Dict, Optional, Any
from loguru import logger
from app.utils.logger import emoji_logger
import tempfile
import os

class AudioTranscriber:
    """
    Serviço de transcrição de áudio usando SpeechRecognition.
    Suporta múltiplos formatos e tem fallback para diferentes engines.
    """
    
    def __init__(self):
        """Inicializa o reconhecedor de fala"""
        self.recognizer = sr.Recognizer()
        # Ajustar threshold de energia para melhor detecção
        self.recognizer.energy_threshold = 300
        # Ajustar tempo de pausa
        self.recognizer.pause_threshold = 0.8
        
        emoji_logger.system_info("AudioTranscriber inicializado com SpeechRecognition")
        
    async def transcribe_from_base64(
        self, 
        audio_base64: str, 
        mimetype: str = "audio/ogg",
        language: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Transcreve áudio de base64 para texto
        
        Args:
            audio_base64: Áudio codificado em base64
            mimetype: Tipo MIME do áudio (audio/ogg, audio/mp3, etc)
            language: Idioma para transcrição (padrão: pt-BR)
            
        Returns:
            Dict com texto transcrito e metadados
        """
        if not audio_base64:
            return {
                "text": "",
                "status": "error",
                "error": "Áudio vazio ou não fornecido"
            }
            
        try:
            emoji_logger.system_info(f"Iniciando transcrição de áudio ({mimetype})")
            
            # 1. Decodificar base64
            try:
                audio_bytes = base64.b64decode(audio_base64)
                emoji_logger.system_debug(f"Áudio decodificado: {len(audio_bytes)} bytes")
            except Exception as e:
                logger.error(f"Erro ao decodificar base64: {e}")
                return {
                    "text": "",
                    "status": "error",
                    "error": f"Erro ao decodificar áudio: {str(e)}"
                }
            
            # 2. Converter para formato que o SpeechRecognition aceita (WAV)
            try:
                # Detectar formato do áudio
                audio_format = mimetype.split("/")[1] if "/" in mimetype else "ogg"
                
                # Criar arquivo temporário para o áudio original
                with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_audio:
                    temp_audio.write(audio_bytes)
                    temp_audio_path = temp_audio.name
                
                # Carregar áudio com pydub
                emoji_logger.system_debug(f"Carregando áudio do formato: {audio_format}")
                
                # Tentar diferentes formatos se o especificado falhar
                audio = None
                formats_to_try = [audio_format, "ogg", "mp3", "m4a", "wav"]
                
                for fmt in formats_to_try:
                    try:
                        if fmt == "ogg":
                            # OGG precisa de codec específico
                            audio = AudioSegment.from_ogg(temp_audio_path)
                        else:
                            audio = AudioSegment.from_file(temp_audio_path, format=fmt)
                        emoji_logger.system_debug(f"Áudio carregado com sucesso usando formato: {fmt}")
                        break
                    except Exception as e:
                        logger.debug(f"Formato {fmt} falhou: {e}")
                        continue
                
                if audio is None:
                    raise Exception("Não foi possível carregar o áudio em nenhum formato")
                
                # Converter para WAV em memória
                wav_io = io.BytesIO()
                audio.export(wav_io, format="wav")
                wav_io.seek(0)
                
                # Obter duração do áudio
                duration_seconds = len(audio) / 1000.0
                emoji_logger.system_info(f"Áudio convertido para WAV: {duration_seconds:.1f} segundos")
                
            except Exception as e:
                logger.error(f"Erro ao converter áudio: {e}")
                return {
                    "text": "",
                    "status": "error", 
                    "error": f"Erro ao processar formato de áudio: {str(e)}"
                }
            finally:
                # Limpar arquivo temporário
                try:
                    if 'temp_audio_path' in locals():
                        os.unlink(temp_audio_path)
                except:
                    pass
            
            # 3. Transcrever com SpeechRecognition
            try:
                with sr.AudioFile(wav_io) as source:
                    # Ajustar para ruído ambiente
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Gravar o áudio
                    audio_data = self.recognizer.record(source)
                    
                    emoji_logger.system_info("Enviando áudio para Google Speech Recognition...")
                    
                    # Tentar transcrever com Google Speech Recognition
                    try:
                        text = self.recognizer.recognize_google(
                            audio_data, 
                            language=language,
                            show_all=False
                        )
                        
                        emoji_logger.system_success(f"Transcrição concluída: {len(text)} caracteres")
                        
                        return {
                            "text": text,
                            "status": "success",
                            "duration": duration_seconds,
                            "language": language,
                            "engine": "google"
                        }
                        
                    except sr.UnknownValueError:
                        # Áudio não compreendido
                        emoji_logger.system_warning("Google Speech não conseguiu entender o áudio")
                        
                        # Tentar com Sphinx como fallback (offline)
                        try:
                            text = self.recognizer.recognize_sphinx(
                                audio_data,
                                language=language
                            )
                            
                            return {
                                "text": text,
                                "status": "success",
                                "duration": duration_seconds,
                                "language": language,
                                "engine": "sphinx",
                                "note": "Transcrição offline (qualidade pode ser menor)"
                            }
                        except:
                            return {
                                "text": "[Áudio não compreendido]",
                                "status": "unclear",
                                "duration": duration_seconds,
                                "language": language
                            }
                            
                    except sr.RequestError as e:
                        # Erro na API
                        logger.error(f"Erro na API do Google Speech: {e}")
                        
                        # Tentar Sphinx offline como fallback
                        try:
                            text = self.recognizer.recognize_sphinx(
                                audio_data,
                                language=language
                            )
                            
                            return {
                                "text": text,
                                "status": "success",
                                "duration": duration_seconds,
                                "language": language,
                                "engine": "sphinx",
                                "note": "API indisponível, usando transcrição offline"
                            }
                        except Exception as sphinx_error:
                            logger.error(f"Sphinx também falhou: {sphinx_error}")
                            return {
                                "text": "",
                                "status": "error",
                                "error": "Serviço de transcrição indisponível",
                                "duration": duration_seconds
                            }
                            
            except Exception as e:
                logger.error(f"Erro na transcrição: {e}")
                return {
                    "text": "",
                    "status": "error",
                    "error": f"Erro ao transcrever: {str(e)}"
                }
                
        except Exception as e:
            logger.exception(f"Erro crítico no AudioTranscriber: {e}")
            return {
                "text": "",
                "status": "error",
                "error": f"Erro crítico: {str(e)}"
            }
    
    async def transcribe_from_file(
        self,
        file_path: str,
        language: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Transcreve áudio de um arquivo
        
        Args:
            file_path: Caminho do arquivo de áudio
            language: Idioma para transcrição
            
        Returns:
            Dict com texto transcrito e metadados
        """
        try:
            with open(file_path, 'rb') as f:
                audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
            # Detectar mimetype pelo arquivo
            extension = os.path.splitext(file_path)[1].lower()
            mimetype_map = {
                '.ogg': 'audio/ogg',
                '.mp3': 'audio/mp3',
                '.wav': 'audio/wav',
                '.m4a': 'audio/m4a',
                '.opus': 'audio/opus'
            }
            mimetype = mimetype_map.get(extension, 'audio/ogg')
            
            return await self.transcribe_from_base64(audio_base64, mimetype, language)
            
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            return {
                "text": "",
                "status": "error",
                "error": f"Erro ao ler arquivo: {str(e)}"
            }

# Singleton global
audio_transcriber = AudioTranscriber()