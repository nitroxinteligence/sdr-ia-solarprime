"""
Validador de Imagens
====================
Utilitário para validar imagens antes de processar com APIs
"""

import base64
import io
from typing import Optional, Dict, Any, Tuple
from PIL import Image
import magic
from loguru import logger


class ImageValidator:
    """Classe para validar imagens antes de enviar para APIs"""
    
    # Formatos suportados pelas APIs
    SUPPORTED_FORMATS = {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/gif': ['.gif'],
        'image/webp': ['.webp']
    }
    
    # Tamanhos máximos (em MB)
    MAX_SIZE_MB = 20  # Gemini suporta até 20MB
    
    # Dimensões máximas
    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096
    
    @classmethod
    def validate_image_data(cls, image_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Valida dados de imagem antes de processar
        
        Returns:
            Tuple[bool, Optional[str], Optional[Dict[str, Any]]]: 
            - bool: Se a imagem é válida
            - str: Mensagem de erro se inválida
            - dict: Metadados da imagem se válida
        """
        try:
            # Determinar origem dos dados
            image_bytes = None
            source_type = None
            
            if 'base64' in image_data:
                # Decodificar base64
                try:
                    image_bytes = base64.b64decode(image_data['base64'])
                    source_type = 'base64'
                except Exception as e:
                    return False, "Erro ao decodificar base64: dados inválidos", None
                    
            elif 'path' in image_data:
                # Ler arquivo
                try:
                    with open(image_data['path'], 'rb') as f:
                        image_bytes = f.read()
                    source_type = 'file'
                except Exception as e:
                    return False, f"Erro ao ler arquivo: {e}", None
                    
            elif 'url' in image_data:
                # URLs são validadas pelas APIs
                return True, None, {
                    'source_type': 'url',
                    'url': image_data['url']
                }
            else:
                return False, "Nenhuma fonte de imagem válida encontrada (base64, path ou url)", None
            
            # Validar se realmente é uma imagem
            if not image_bytes:
                return False, "Dados de imagem vazios", None
            
            # Verificar tamanho
            size_mb = len(image_bytes) / (1024 * 1024)
            if size_mb > cls.MAX_SIZE_MB:
                return False, f"Imagem muito grande: {size_mb:.1f}MB (máximo: {cls.MAX_SIZE_MB}MB)", None
            
            # Verificar formato usando python-magic
            try:
                mime = magic.Magic(mime=True)
                detected_mime = mime.from_buffer(image_bytes)
                
                if detected_mime not in cls.SUPPORTED_FORMATS:
                    return False, f"Formato não suportado: {detected_mime}. Use: {', '.join(cls.SUPPORTED_FORMATS.keys())}", None
                    
            except Exception as e:
                logger.warning(f"python-magic não disponível, tentando com PIL: {e}")
                detected_mime = None
            
            # Validar com PIL
            try:
                img = Image.open(io.BytesIO(image_bytes))
                
                # Verificar formato
                format_map = {
                    'JPEG': 'image/jpeg',
                    'PNG': 'image/png',
                    'GIF': 'image/gif',
                    'WEBP': 'image/webp'
                }
                
                pil_format = format_map.get(img.format)
                if not pil_format:
                    return False, f"Formato PIL não suportado: {img.format}", None
                
                # Usar formato detectado pelo PIL se magic falhou
                if not detected_mime:
                    detected_mime = pil_format
                
                # Verificar dimensões
                width, height = img.size
                if width > cls.MAX_WIDTH or height > cls.MAX_HEIGHT:
                    return False, f"Imagem muito grande: {width}x{height} (máximo: {cls.MAX_WIDTH}x{cls.MAX_HEIGHT})", None
                
                # Coletar metadados
                metadata = {
                    'source_type': source_type,
                    'mime_type': detected_mime,
                    'format': img.format,
                    'size_mb': size_mb,
                    'width': width,
                    'height': height,
                    'mode': img.mode
                }
                
                logger.info(f"Imagem válida: {detected_mime} {width}x{height} ({size_mb:.2f}MB)")
                return True, None, metadata
                
            except Exception as e:
                return False, f"Dados não são uma imagem válida: {e}", None
                
        except Exception as e:
            logger.error(f"Erro inesperado ao validar imagem: {e}")
            return False, f"Erro ao validar imagem: {e}", None
    
    @classmethod
    def create_test_image(cls, width: int = 800, height: int = 600, format: str = 'PNG') -> bytes:
        """
        Cria uma imagem de teste válida
        
        Args:
            width: Largura da imagem
            height: Altura da imagem
            format: Formato da imagem (PNG, JPEG)
            
        Returns:
            bytes: Dados da imagem
        """
        # Criar imagem com PIL
        img = Image.new('RGB', (width, height), color='white')
        
        # Adicionar algum conteúdo para simular conta de luz
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Adicionar texto
        try:
            # Tentar usar fonte padrão
            font = ImageFont.load_default()
        except:
            font = None
            
        draw.text((50, 50), "CONTA DE LUZ", fill='black', font=font)
        draw.text((50, 100), "Valor: R$ 850,00", fill='black', font=font)
        draw.text((50, 150), "Consumo: 450 kWh", fill='black', font=font)
        draw.text((50, 200), "Vencimento: 15/01/2025", fill='black', font=font)
        
        # Converter para bytes
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        return buffer.getvalue()
    
    @classmethod
    def fix_image_orientation(cls, image_bytes: bytes) -> bytes:
        """
        Corrige orientação da imagem baseado em EXIF
        
        Args:
            image_bytes: Bytes da imagem
            
        Returns:
            bytes: Imagem com orientação corrigida
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Verificar e corrigir orientação EXIF
            if hasattr(img, '_getexif') and img._getexif():
                exif = img._getexif()
                orientation_key = 274  # Orientation tag
                
                if orientation_key in exif:
                    orientation = exif[orientation_key]
                    
                    # Rotacionar baseado na orientação
                    rotations = {
                        3: 180,
                        6: 270,
                        8: 90
                    }
                    
                    if orientation in rotations:
                        img = img.rotate(rotations[orientation], expand=True)
                        
                        # Salvar imagem corrigida
                        buffer = io.BytesIO()
                        img.save(buffer, format=img.format or 'JPEG')
                        return buffer.getvalue()
            
            return image_bytes
            
        except Exception as e:
            logger.warning(f"Erro ao corrigir orientação: {e}")
            return image_bytes