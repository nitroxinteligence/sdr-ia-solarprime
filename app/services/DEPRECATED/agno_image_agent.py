#!/usr/bin/env python3
"""
AGNO ImageEnhancementAgent - Sub-agente modular para processamento de imagens
Baseado nos padrões AGNO Framework Image() class

FILOSOFIA: ZERO COMPLEXIDADE - O SIMPLES FUNCIONA
- Wrappeia o código existente sem breaking changes
- Adiciona metadata e confidence scoring AGNO
- Decorator pattern para modularidade
"""

import base64
from io import BytesIO
from typing import Dict, Any, Optional, Callable
from PIL import Image as PILImage
from app.utils.logger import emoji_logger


class AGNOImageProcessor:
    """
    Processador de imagens baseado no padrão AGNO Image()
    Mantém compatibilidade com código existente + adiciona capabilities AGNO
    """
    
    def __init__(self):
        """Initialize com padrões AGNO"""
        # Magic bytes expandidos baseados no AGNO Framework
        self.agno_formats = {
            b'\xff\xd8\xff': {'format': 'jpeg', 'confidence': 'high', 'agno_class': 'Image'},
            b'\x89PNG\r\n\x1a\n': {'format': 'png', 'confidence': 'high', 'agno_class': 'Image'},
            b'GIF87a': {'format': 'gif', 'confidence': 'high', 'agno_class': 'Image'},
            b'GIF89a': {'format': 'gif', 'confidence': 'high', 'agno_class': 'Image'},
            b'RIFF': {'format': 'webp', 'confidence': 'medium', 'agno_class': 'Image'},
            b'BM': {'format': 'bmp', 'confidence': 'high', 'agno_class': 'Image'},
            b'ftyp': {'format': 'heic', 'confidence': 'medium', 'agno_class': 'Image'},
            b'II*\x00': {'format': 'tiff', 'confidence': 'high', 'agno_class': 'Image'},
            b'MM\x00*': {'format': 'tiff', 'confidence': 'high', 'agno_class': 'Image'},
            b'\x00\x00\x01\x00': {'format': 'ico', 'confidence': 'medium', 'agno_class': 'Image'},
            b'AVIF': {'format': 'avif', 'confidence': 'medium', 'agno_class': 'Image'},
            b'\xff\xee': {'format': 'heic_alt', 'confidence': 'low', 'agno_class': 'Image'}
        }
    
    def enhance_image_validation(self, image_bytes: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced validation com AGNO metadata
        
        Args:
            image_bytes: Bytes da imagem
            filename: Nome do arquivo (opcional)
            
        Returns:
            Dict com validation result + AGNO metadata
        """
        try:
            # Detectar formato usando AGNO patterns
            agno_detection = self._detect_agno_format(image_bytes)
            
            # Tentar validação PIL (mantém lógica existente)
            pil_validation = self._validate_with_pil(image_bytes)
            
            # Combinar resultados AGNO + PIL
            return {
                'agno_format': agno_detection,
                'pil_validation': pil_validation,
                'filename': filename,
                'combined_confidence': self._calculate_confidence(agno_detection, pil_validation),
                'agno_compatible': True,
                'processing_method': 'agno_enhanced_pil'
            }
            
        except Exception as e:
            emoji_logger.system_error("AGNO Image Enhancement", str(e))
            return {
                'error': f"AGNO image enhancement failed: {str(e)}",
                'agno_compatible': False
            }
    
    def _detect_agno_format(self, image_bytes: bytes) -> Dict[str, Any]:
        """Detecta formato usando padrões AGNO"""
        magic_bytes = image_bytes[:20]
        
        for agno_magic, format_info in self.agno_formats.items():
            if magic_bytes.startswith(agno_magic):
                return {
                    'detected': True,
                    'format': format_info['format'],
                    'confidence': format_info['confidence'],
                    'agno_class': format_info['agno_class'],
                    'magic_bytes': magic_bytes[:12].hex()
                }
        
        return {
            'detected': False,
            'format': 'unknown',
            'confidence': 'none',
            'agno_class': None,
            'magic_bytes': magic_bytes[:12].hex()
        }
    
    def _validate_with_pil(self, image_bytes: bytes) -> Dict[str, Any]:
        """Validação PIL (mantém lógica existente)"""
        try:
            test_img = PILImage.open(BytesIO(image_bytes))
            test_img.verify()
            
            # Reabrir para obter informações
            img = PILImage.open(BytesIO(image_bytes))
            
            return {
                'valid': True,
                'format': img.format,
                'size': img.size,
                'mode': img.mode,
                'validation_method': 'pil_verify'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'validation_method': 'pil_verify'
            }
    
    def _calculate_confidence(self, agno_detection: Dict, pil_validation: Dict) -> str:
        """Calcula confidence combinado AGNO + PIL"""
        if agno_detection['detected'] and pil_validation['valid']:
            if agno_detection['confidence'] == 'high':
                return 'very_high'
            return 'high'
        elif pil_validation['valid']:
            return 'medium'
        elif agno_detection['detected']:
            return 'low'
        else:
            return 'none'


# Instância global do processador AGNO
agno_image_processor = AGNOImageProcessor()


def agno_image_enhancer(func: Callable) -> Callable:
    """
    Decorator AGNO para enhanced image processing
    Wrappeia método existente + adiciona AGNO capabilities
    
    ZERO COMPLEXIDADE: Mantém código existente funcionando
    """
    def wrapper(*args, **kwargs):
        # Chama método original (mantém funcionalidade existente)
        original_result = func(*args, **kwargs)
        
        emoji_logger.system_info(f"AGNO Image Decorator: processando resultado original - tipo: {original_result.get('type')}, erro: {bool(original_result.get('error'))}")
        
        # Se processamento original foi bem-sucedido, adicionar AGNO enhancements
        if (isinstance(original_result, dict) and 
            original_result.get('type') == 'image' and 
            not original_result.get('error')):
            
            try:
                # Extrair image_bytes do contexto (assumindo que está em args)
                if len(args) >= 2 and isinstance(args[1], str):
                    # args[1] provavelmente é media_data (base64)
                    image_bytes = base64.b64decode(args[1])
                    
                    # Aplicar AGNO enhancements
                    agno_metadata = agno_image_processor.enhance_image_validation(image_bytes)
                    
                    # Adicionar metadata AGNO ao resultado original
                    original_result['agno_metadata'] = agno_metadata
                    original_result['enhanced_with_agno'] = True
                    
                    emoji_logger.system_info(
                        f"AGNO Image enhanced: {agno_metadata['agno_format']['format']} "
                        f"confidence {agno_metadata['combined_confidence']}"
                    )
                    
            except Exception as e:
                emoji_logger.system_warning(f"AGNO enhancement failed (non-critical): {e}")
                # Não falha - apenas não adiciona metadata
                original_result['agno_enhancement_error'] = str(e)
        
        # CORREÇÃO CRÍTICA: Se é imagem mas processamento original falhou, tentar AGNO fallback
        elif (isinstance(original_result, dict) and 
              original_result.get('type') == 'image' and 
              original_result.get('error')):
            
            emoji_logger.system_info("AGNO Image Decorator: detectado erro original, tentando fallback AGNO")
            
            try:
                if len(args) >= 2 and isinstance(args[1], str):
                    # args[1] provavelmente é media_data (base64)
                    image_bytes = base64.b64decode(args[1])
                    filename = kwargs.get('filename') or original_result.get('filename')
                    
                    # Tentar AGNO fallback
                    agno_fallback = agno_fallback_processor(image_bytes, filename)
                    
                    # Se AGNO conseguiu processar onde o original falhou
                    if agno_fallback.get('status') == 'success':
                        agno_fallback['fallback_from_original'] = True
                        agno_fallback['original_error'] = original_result.get('error')
                        
                        emoji_logger.system_info(f"AGNO Image fallback successful for: {filename}")
                        return agno_fallback
                    else:
                        emoji_logger.system_warning(f"AGNO Image fallback também falhou: {agno_fallback.get('error')}")
                        
            except Exception as e:
                emoji_logger.system_warning(f"AGNO Image fallback failed: {e}")
        
        return original_result
    
    return wrapper


def agno_fallback_processor(image_bytes: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Processador fallback AGNO para casos que o código original não consegue lidar
    Usado quando magic bytes são desconhecidos mas queremos tentar AGNO patterns
    """
    try:
        agno_result = agno_image_processor.enhance_image_validation(image_bytes, filename)
        
        if agno_result['combined_confidence'] in ['high', 'very_high', 'medium']:
            return {
                'type': 'image',
                'status': 'success',
                'processing_method': 'agno_fallback',
                'agno_metadata': agno_result,
                'fallback': 'AGNO pattern recognition successful'
            }
        else:
            return {
                'type': 'image',
                'error': 'Formato de imagem não suportado pelo AGNO',
                'status': 'error',
                'agno_metadata': agno_result,
                'fallback': 'Por favor, envie a imagem em formato comum (JPEG, PNG, GIF, etc.)'
            }
            
    except Exception as e:
        emoji_logger.system_error("AGNO Fallback Processor", str(e))
        return {
            'type': 'image',
            'error': f'Erro no processamento AGNO: {str(e)}',
            'status': 'error'
        }