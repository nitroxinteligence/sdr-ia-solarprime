"""
Audio Transcription Service - Transcreve áudios do WhatsApp
Prioridade: 1º Google Speech (gratuito), 2º OpenAI Whisper-1 (barato: $0.006/min)
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
import subprocess
from app.config import settings

def validate_audio_base64(audio_data: str) -> tuple[bool, str]:
    """
    Valida se o áudio está em formato base64 válido
    
    Returns:
        (is_valid, format_type)
    """
    if not audio_data:
        return False, "empty"
    
    # Verificar se é data URL
    if audio_data.startswith("data:"):
        if ";base64," in audio_data:
            # Extrair apenas o base64
            audio_data = audio_data.split(";base64,")[1]
            return True, "data_url_extracted"
        return False, "invalid_data_url"
    
    # Verificar se é URL (não deveria chegar aqui)
    if audio_data.startswith(("http://", "https://")):
        return False, "url_not_base64"
    
    # Tentar validar base64
    try:
        if len(audio_data) > 50:
            # Tenta decodificar uma amostra
            test = base64.b64decode(audio_data[:100] if len(audio_data) >= 100 else audio_data)
            return True, "base64"
        else:
            return False, "too_short"
    except:
        return False, "invalid_base64"

class AudioTranscriber:
    """
    Serviço de transcrição de áudio usando SpeechRecognition.
    Suporta múltiplos formatos e tem fallback para diferentes engines.
    """
    
    def __init__(self):
        """Inicializa o transcriber com Google e OpenAI como fallback"""
        self.recognizer = sr.Recognizer()
        # Ajustar threshold de energia para melhor detecção
        self.recognizer.energy_threshold = 300
        # Ajustar tempo de pausa
        self.recognizer.pause_threshold = 0.8
        
        # Verificar se OpenAI está disponível como fallback
        self.openai_available = False
        try:
            if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                self.openai_available = True
                emoji_logger.system_info("✅ AudioTranscriber com Google Speech + OpenAI Whisper fallback")
            else:
                emoji_logger.system_info("AudioTranscriber usando apenas Google Speech (sem OpenAI fallback)")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI não disponível para fallback: {e}")
            emoji_logger.system_info("AudioTranscriber usando apenas Google Speech")
        
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
            
            # 1. Validar formato antes de decodificar
            is_valid, format_type = validate_audio_base64(audio_base64)
            
            if not is_valid:
                logger.error(f"Formato de áudio inválido: {format_type}")
                return {
                    "text": "",
                    "status": "error",
                    "error": f"Formato de áudio inválido: {format_type}"
                }
            
            # Se era data URL, extrair o base64
            if format_type == "data_url_extracted":
                audio_base64 = audio_base64.split(";base64,")[1]
                logger.info("📊 Base64 extraído de data URL")
            
            logger.info(f"✅ Formato de áudio validado: {format_type}")
            emoji_logger.system_info(f"✅ Formato de áudio validado: {format_type}")
            
            # 2. Decodificar base64 (agora sabemos que é válido)
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
                
                # IMPORTANTE: Áudio do WhatsApp pode vir criptografado
                # Verificar se é áudio criptografado do WhatsApp (não começa com magic bytes conhecidos)
                is_encrypted = False
                if len(audio_bytes) > 4:
                    # Verificar magic bytes comuns de áudio
                    magic = audio_bytes[:4]
                    known_formats = [
                        b'OggS',  # Ogg
                        b'RIFF',  # WAV
                        b'\xff\xfb', b'\xff\xf3', b'\xff\xf2',  # MP3
                        b'ftyp',  # MP4/M4A
                        b'ID3'   # MP3 with ID3
                    ]
                    is_encrypted = not any(magic.startswith(fmt) for fmt in known_formats)
                    
                    if is_encrypted:
                        logger.warning(f"⚠️ Áudio parece estar criptografado (magic: {magic.hex()})")
                        # Para áudio criptografado do WhatsApp, usar extensão opus
                        audio_format = "opus"  # WhatsApp usa Opus codec
                
                # Criar arquivo temporário para o áudio original
                with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_audio:
                    temp_audio.write(audio_bytes)
                    temp_audio_path = temp_audio.name
                
                # Carregar áudio com pydub
                emoji_logger.system_debug(f"Carregando áudio do formato: {audio_format}")
                
                # Para áudio do WhatsApp (Opus ou criptografado), usar ffmpeg diretamente
                audio = None
                
                # Verificar se é áudio do WhatsApp (Opus) ou criptografado
                if "opus" in mimetype.lower() or audio_format == "ogg" or is_encrypted:
                    try:
                        # Usar ffmpeg para converter para WAV
                        logger.info("🎵 Detectado áudio Opus/criptografado do WhatsApp, usando ffmpeg...")
                        
                        # Criar arquivo temporário para o WAV
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                            temp_wav_path = temp_wav.name
                        
                        # Comando ffmpeg para converter para WAV
                        # Para áudio criptografado/Opus do WhatsApp, usar configurações específicas
                        cmd = [
                            'ffmpeg',
                            '-i', temp_audio_path,
                            '-acodec', 'pcm_s16le',  # Forçar codec PCM para WAV
                            '-ar', '16000',  # Taxa de amostragem 16kHz
                            '-ac', '1',      # Mono
                            '-f', 'wav',
                            '-loglevel', 'error',  # Mostrar apenas erros
                            '-y',            # Sobrescrever arquivo
                            temp_wav_path
                        ]
                        
                        # Executar ffmpeg
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0:
                            # Verificar se o arquivo foi criado e tem conteúdo
                            if os.path.exists(temp_wav_path) and os.path.getsize(temp_wav_path) > 0:
                                # Carregar o WAV convertido
                                audio = AudioSegment.from_wav(temp_wav_path)
                                emoji_logger.system_debug(f"✅ Áudio convertido com sucesso via ffmpeg")
                            else:
                                raise Exception("ffmpeg criou arquivo vazio")
                            
                            # Limpar arquivo temporário
                            try:
                                os.unlink(temp_wav_path)
                            except:
                                pass
                        else:
                            # Se ffmpeg falhou, pode ser que o formato não foi reconhecido
                            logger.error(f"ffmpeg retornou erro: {result.stderr}")
                            
                            # Tentar com probe primeiro para detectar formato
                            probe_cmd = ['ffprobe', '-v', 'error', '-show_format', '-show_streams', temp_audio_path]
                            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                            logger.debug(f"ffprobe output: {probe_result.stdout}")
                            
                            raise Exception(f"ffmpeg falhou ao converter: {result.stderr}")
                            
                    except subprocess.TimeoutExpired:
                        logger.error("ffmpeg timeout após 30 segundos")
                        raise Exception("ffmpeg demorou muito para processar o áudio")
                    except Exception as e:
                        logger.error(f"Erro ao converter com ffmpeg: {e}")
                        # Tentar fallback com pydub
                        
                # Se não é Opus ou ffmpeg falhou, tentar com pydub
                if audio is None:
                    formats_to_try = [audio_format, "ogg", "mp3", "m4a", "wav"]
                    
                    for fmt in formats_to_try:
                        try:
                            if fmt == "ogg":
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
                        
                        emoji_logger.system_info(f"✅ Transcrição concluída: {len(text)} caracteres")
                        
                        return {
                            "text": text,
                            "status": "success",
                            "duration": duration_seconds,
                            "language": language,
                            "engine": "google"
                        }
                        
                    except sr.UnknownValueError:
                        # Google não conseguiu entender - tentar OpenAI Whisper
                        emoji_logger.system_warning("Google Speech não entendeu, tentando OpenAI Whisper...")
                        
                        if self.openai_available and os.path.exists(wav_path):
                            try:
                                # Usar OpenAI Whisper-1 como fallback
                                with open(wav_path, "rb") as audio_file:
                                    transcription = self.openai_client.audio.transcriptions.create(
                                        model="whisper-1",
                                        file=audio_file,
                                        language="pt"
                                    )
                                
                                text = transcription.text
                                emoji_logger.system_info(f"✅ Whisper-1 transcreveu: {len(text)} chars")
                                
                                return {
                                    "text": text,
                                    "status": "success",
                                    "duration": duration_seconds,
                                    "language": language,
                                    "engine": "whisper-1",
                                    "note": "Transcrito com OpenAI Whisper ($0.006/min)"
                                }
                            except Exception as whisper_error:
                                logger.error(f"Whisper também falhou: {whisper_error}")
                        
                        return {
                            "text": "[Áudio não compreendido]",
                            "status": "unclear",
                            "duration": duration_seconds,
                            "language": language
                        }
                            
                    except sr.RequestError as e:
                        # Google API falhou - tentar OpenAI Whisper
                        logger.error(f"Erro Google Speech: {e}")
                        emoji_logger.system_warning("🔄 Google falhou, tentando OpenAI Whisper...")
                        
                        if self.openai_available and os.path.exists(wav_path):
                            try:
                                with open(wav_path, "rb") as audio_file:
                                    transcription = self.openai_client.audio.transcriptions.create(
                                        model="whisper-1",
                                        file=audio_file,
                                        language="pt"
                                    )
                                
                                text = transcription.text
                                emoji_logger.system_info(f"✅ Whisper-1 salvou o dia: {len(text)} chars")
                                
                                return {
                                    "text": text,
                                    "status": "success",
                                    "duration": duration_seconds,
                                    "language": language,
                                    "engine": "whisper-1-fallback",
                                    "note": "Google falhou, usado Whisper ($0.006/min)"
                                }
                            except Exception as whisper_error:
                                logger.error(f"Whisper também falhou: {whisper_error}")
                        
                        return {
                            "text": "",
                            "status": "error",
                            "error": "Serviços de transcrição indisponíveis",
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