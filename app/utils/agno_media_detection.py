"""
AGNO Framework - Media Detection Utility
Detecção robusta de tipos de mídia com fallbacks inteligentes
Baseado nos padrões oficiais do AGNO Framework
"""

from typing import Dict, Any, Optional, Tuple
from app.utils.logger import emoji_logger


class AGNOMediaDetector:
    """
    Detector de mídia baseado nos padrões AGNO Framework
    Suporta detecção robusta com fallbacks para formatos não reconhecidos
    """
    
    def __init__(self):
        """Initialize AGNO media patterns"""
        self.image_patterns = {
            b'\xff\xd8\xff': {'format': 'jpeg', 'agno_class': 'Image', 'confidence': 'high'},
            b'\x89PNG\r\n\x1a\n': {'format': 'png', 'agno_class': 'Image', 'confidence': 'high'},
            b'GIF87a': {'format': 'gif', 'agno_class': 'Image', 'confidence': 'high'},
            b'GIF89a': {'format': 'gif', 'agno_class': 'Image', 'confidence': 'high'},
            b'RIFF': {'format': 'webp', 'agno_class': 'Image', 'confidence': 'medium', 'extra_check': 'webp'},
            b'BM': {'format': 'bmp', 'agno_class': 'Image', 'confidence': 'high'},
            b'ftyp': {'format': 'heic', 'agno_class': 'Image', 'confidence': 'medium', 'extra_check': 'heic'},
            b'II*\x00': {'format': 'tiff', 'agno_class': 'Image', 'confidence': 'high'},
            b'MM\x00*': {'format': 'tiff', 'agno_class': 'Image', 'confidence': 'high'},
            b'\x00\x00\x01\x00': {'format': 'ico', 'agno_class': 'Image', 'confidence': 'medium'},
            b'\xff\xee': {'format': 'heic_alt', 'agno_class': 'Image', 'confidence': 'low'}
        }
        
        self.document_patterns = {
            b'%PDF': {'format': 'pdf', 'agno_class': 'PDFReader', 'confidence': 'high'},
            b'PK\x03\x04': {'format': 'docx', 'agno_class': 'DocxReader', 'confidence': 'medium', 'extra_check': 'zip'},
            b'\xd0\xcf\x11\xe0': {'format': 'doc', 'agno_class': 'LegacyDoc', 'confidence': 'high'},
        }
        
        self.audio_patterns = {
            b'ID3': {'format': 'mp3', 'agno_class': 'Audio', 'confidence': 'high'},
            b'\xff\xfb': {'format': 'mp3', 'agno_class': 'Audio', 'confidence': 'medium'},
            b'OggS': {'format': 'ogg', 'agno_class': 'Audio', 'confidence': 'high'},
            b'RIFF': {'format': 'wav', 'agno_class': 'Audio', 'confidence': 'medium', 'extra_check': 'wav'},
            b'fLaC': {'format': 'flac', 'agno_class': 'Audio', 'confidence': 'high'},
        }
    
    def is_encrypted_whatsapp(self, data_bytes: bytes) -> bool:
        """
        Detecta mídia criptografada do WhatsApp
        
        Args:
            data_bytes: Bytes do arquivo
            
        Returns:
            True se a mídia parece estar criptografada
        """
        # Padrões conhecidos de mídia criptografada do WhatsApp
        encrypted_patterns = [
            b'\xcf\xee\x6a\x4e',  # Imagem criptografada
            b'\x4c\x57\x18\x5d',  # PDF criptografado
            b'\xaa\x30\x3b\x02',  # Áudio criptografado
            b'\x03\xae\xae\x12',  # Outro padrão comum
            b'\xaf\x5c\x08\xb7',  # Áudio Opus criptografado
            b'\xa3\x03\x3b\x02',  # Variação de áudio
        ]
        
        if not data_bytes or len(data_bytes) < 4:
            return False
            
        # Verificar primeiros 4 bytes
        first_bytes = data_bytes[:4]
        for pattern in encrypted_patterns:
            if first_bytes.startswith(pattern):
                emoji_logger.system_warning(f"⚠️ Mídia criptografada detectada: {first_bytes.hex()}")
                return True
        
        # Verificar se não corresponde a nenhum formato conhecido
        # Se não é nenhum formato conhecido E não está vazio, pode ser criptografado
        if len(data_bytes) > 100:
            # Verificar entropia dos primeiros bytes (mídia criptografada tem alta entropia)
            unique_bytes = len(set(data_bytes[:100]))
            if unique_bytes > 90:  # Alta entropia sugere criptografia
                emoji_logger.system_warning(f"⚠️ Possível mídia criptografada (alta entropia): {data_bytes[:4].hex()}")
                return True
                
        return False
    
    def detect_media_type(self, data_bytes: bytes) -> Dict[str, Any]:
        """
        Detecta tipo de mídia usando padrões AGNO
        
        Args:
            data_bytes: Bytes do arquivo
            
        Returns:
            Informações sobre o tipo detectado
        """
        if not data_bytes:
            return {
                'detected': False,
                'error': 'Dados vazios'
            }
        
        # Verificar PRIMEIRO se está criptografado
        if self.is_encrypted_whatsapp(data_bytes):
            return {
                'detected': False,
                'format': 'encrypted',
                'is_encrypted': True,
                'agno_class': None,
                'confidence': 'none',
                'magic_bytes': data_bytes[:12].hex() if data_bytes else '',
                'error': 'Mídia criptografada do WhatsApp - necessita download completo',
                'fallback_suggestion': 'Baixar mídia completa via URL do WhatsApp'
            }
        
        # Extrair magic bytes (primeiros 20 bytes para análise completa)
        magic_bytes = data_bytes[:20] if len(data_bytes) >= 20 else data_bytes
        
        emoji_logger.system_info(f"AGNO Media Detection: {magic_bytes[:12].hex()}")
        
        # Tentar detectar imagem
        image_result = self._detect_image(magic_bytes, data_bytes)
        if image_result['detected']:
            return image_result
        
        # Tentar detectar documento
        document_result = self._detect_document(magic_bytes, data_bytes)
        if document_result['detected']:
            return document_result
        
        # Tentar detectar áudio
        audio_result = self._detect_audio(magic_bytes, data_bytes)
        if audio_result['detected']:
            return audio_result
        
        # Fallback: formato não reconhecido
        return {
            'detected': False,
            'format': 'unknown',
            'agno_class': None,
            'confidence': 'none',
            'magic_bytes': magic_bytes[:12].hex(),
            'fallback_suggestion': 'Use PIL/fallback detection ou converta para formato suportado'
        }
    
    def _detect_image(self, magic_bytes: bytes, full_data: bytes) -> Dict[str, Any]:
        """Detecta formato de imagem"""
        for pattern, info in self.image_patterns.items():
            if magic_bytes.startswith(pattern):
                # Verificações extras para alguns formatos
                if info.get('extra_check'):
                    if not self._verify_extra_check(magic_bytes, full_data, info['extra_check'], info['format']):
                        continue
                
                return {
                    'detected': True,
                    'media_type': 'image',
                    'format': info['format'],
                    'agno_class': info['agno_class'],
                    'confidence': info['confidence'],
                    'magic_bytes': magic_bytes[:12].hex(),
                    'recommended_params': self._get_image_params(info['format'])
                }
        
        return {'detected': False}
    
    def _detect_document(self, magic_bytes: bytes, full_data: bytes) -> Dict[str, Any]:
        """Detecta formato de documento"""
        for pattern, info in self.document_patterns.items():
            if magic_bytes.startswith(pattern):
                # Verificações extras para alguns formatos
                if info.get('extra_check'):
                    if not self._verify_extra_check(magic_bytes, full_data, info['extra_check'], info['format']):
                        continue
                
                return {
                    'detected': True,
                    'media_type': 'document',
                    'format': info['format'],
                    'agno_class': info['agno_class'],
                    'confidence': info['confidence'],
                    'magic_bytes': magic_bytes[:12].hex(),
                    'recommended_params': self._get_document_params(info['format'])
                }
        
        return {'detected': False}
    
    def _detect_audio(self, magic_bytes: bytes, full_data: bytes) -> Dict[str, Any]:
        """Detecta formato de áudio"""
        for pattern, info in self.audio_patterns.items():
            if magic_bytes.startswith(pattern):
                # Verificações extras para alguns formatos
                if info.get('extra_check'):
                    if not self._verify_extra_check(magic_bytes, full_data, info['extra_check'], info['format']):
                        continue
                
                return {
                    'detected': True,
                    'media_type': 'audio',
                    'format': info['format'],
                    'agno_class': info['agno_class'],
                    'confidence': info['confidence'],
                    'magic_bytes': magic_bytes[:12].hex(),
                    'recommended_params': self._get_audio_params(info['format'])
                }
        
        return {'detected': False}
    
    def _verify_extra_check(self, magic_bytes: bytes, full_data: bytes, check_type: str, format_name: str) -> bool:
        """Verificações extras para formatos que precisam de validação adicional"""
        if check_type == 'webp':
            # RIFF + WEBP signature
            return len(magic_bytes) >= 12 and magic_bytes[8:12] == b'WEBP'
        
        elif check_type == 'heic':
            # ftyp + heic variants
            if len(magic_bytes) >= 12:
                ftype = magic_bytes[8:12]
                return ftype in [b'heic', b'heix', b'hevc', b'mif1']
            return False
        
        elif check_type == 'wav':
            # RIFF + WAVE signature
            return len(magic_bytes) >= 12 and magic_bytes[8:12] == b'WAVE'
        
        elif check_type == 'zip':
            # Verificar se é realmente DOCX e não ZIP genérico
            # DOCX tem estrutura específica de pastas
            return True  # Por enquanto aceitar todos os ZIP como possível DOCX
        
        return True
    
    def _get_image_params(self, format_name: str) -> Dict[str, Any]:
        """Parâmetros recomendados para agno.media.Image"""
        base_params = {
            'detail': 'high',  # Para análise detalhada
        }
        
        if format_name in ['jpeg', 'jpg']:
            base_params['format'] = 'jpeg'
        elif format_name == 'png':
            base_params['format'] = 'png'
        elif format_name == 'gif':
            base_params['format'] = 'gif'
        elif format_name == 'webp':
            base_params['format'] = 'webp'
        else:
            base_params['format'] = 'jpeg'  # Default fallback
        
        return base_params
    
    def _get_document_params(self, format_name: str) -> Dict[str, Any]:
        """Parâmetros recomendados para AGNO document readers"""
        if format_name == 'pdf':
            return {
                'reader_class': 'PDFReader',
                'ocr_enabled': True,
                'max_pages': None
            }
        elif format_name == 'docx':
            return {
                'reader_class': 'DocxReader',
                'extract_tables': True,
                'extract_images': False
            }
        else:
            return {
                'reader_class': 'TextReader',
                'encoding': 'utf-8'
            }
    
    def _get_audio_params(self, format_name: str) -> Dict[str, Any]:
        """Parâmetros recomendados para agno.media.Audio"""
        return {
            'format': format_name,
            'transcription_enabled': True,
            'language': 'pt-BR'
        }
    
    def get_fallback_suggestion(self, magic_bytes_hex: str) -> str:
        """Fornece sugestão de fallback para formatos não reconhecidos"""
        common_issues = {
            'cfee6a4ee9379ab2': 'Formato proprietário - converta para JPEG/PNG',
            '424d': 'BMP detectado - use conversão para JPEG',
            '89504e47': 'PNG corrompido - reenvie o arquivo',
            'ffd8ffe0': 'JPEG sem marcadores completos - pode funcionar com fallback PIL'
        }
        
        return common_issues.get(magic_bytes_hex[:16], 
            'Formato não reconhecido - tente converter para JPEG, PNG ou PDF')


# Instância global
agno_media_detector = AGNOMediaDetector()