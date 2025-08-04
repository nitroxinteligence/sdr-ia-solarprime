#!/usr/bin/env python3
"""
Teste completo das correções do sistema multimodal
"""
import base64
import sys
sys.path.insert(0, '.')

def test_agno_detector():
    """Testa o AGNOMediaDetector"""
    print("\n🔍 Testando AGNOMediaDetector...")
    
    from app.utils.agno_media_detection import AGNOMediaDetector
    detector = AGNOMediaDetector()
    
    # Teste 1: JPEG magic bytes
    jpeg_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    result = detector.detect_media_type(jpeg_bytes)
    assert result['detected'] == True, "JPEG não detectado"
    assert result['format'] == 'jpeg', f"Formato incorreto: {result['format']}"
    print(f"✅ JPEG detectado corretamente: {result}")
    
    # Teste 2: PNG magic bytes
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    result = detector.detect_media_type(png_bytes)
    assert result['detected'] == True, "PNG não detectado"
    assert result['format'] == 'png', f"Formato incorreto: {result['format']}"
    print(f"✅ PNG detectado corretamente: {result}")
    
    # Teste 3: PDF magic bytes
    pdf_bytes = b'%PDF-1.4\n%\xd3\xeb\xe9\xe1'
    result = detector.detect_media_type(pdf_bytes)
    assert result['detected'] == True, "PDF não detectado"
    assert result['format'] == 'pdf', f"Formato incorreto: {result['format']}"
    print(f"✅ PDF detectado corretamente: {result}")
    
    # Teste 4: Áudio OGG
    ogg_bytes = b'OggS\x00\x02\x00\x00\x00\x00\x00\x00'
    result = detector.detect_media_type(ogg_bytes)
    assert result['detected'] == True, "OGG não detectado"
    assert result['format'] == 'ogg', f"Formato incorreto: {result['format']}"
    print(f"✅ OGG detectado corretamente: {result}")
    
    # Teste 5: Formato desconhecido
    unknown_bytes = b'\x03\xae\xae\x12\xa7\x69\x38\xc8'
    result = detector.detect_media_type(unknown_bytes)
    assert result['detected'] == False, "Formato desconhecido deveria falhar"
    print(f"✅ Formato desconhecido tratado corretamente: {result}")
    
    print("✅ Todos os testes do AGNOMediaDetector passaram!")
    return True

def test_detect_media_format():
    """Testa a função detect_media_format"""
    print("\n🔍 Testando detect_media_format...")
    
    from app.api.webhooks import detect_media_format
    
    # Teste 1: Base64 válido
    test_base64 = base64.b64encode(b"Hello World" * 10).decode('utf-8')
    result = detect_media_format(test_base64)
    assert result == 'base64', f"Base64 não detectado: {result}"
    print(f"✅ Base64 detectado: {result}")
    
    # Teste 2: Data URL
    data_url = "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
    result = detect_media_format(data_url)
    assert result == 'data_url', f"Data URL não detectada: {result}"
    print(f"✅ Data URL detectada: {result}")
    
    # Teste 3: URL HTTP
    http_url = "https://example.com/image.jpg"
    result = detect_media_format(http_url)
    assert result == 'url', f"URL não detectada: {result}"
    print(f"✅ URL detectada: {result}")
    
    # Teste 4: Bytes
    byte_data = b"Some binary data"
    result = detect_media_format(byte_data)
    assert result == 'bytes', f"Bytes não detectados: {result}"
    print(f"✅ Bytes detectados: {result}")
    
    # Teste 5: None
    result = detect_media_format(None)
    assert result == 'unknown', f"None deveria ser unknown: {result}"
    print(f"✅ None tratado corretamente: {result}")
    
    print("✅ Todos os testes de detect_media_format passaram!")
    return True

def test_webhook_integration():
    """Testa integração no webhook"""
    print("\n🔍 Testando integração no webhook...")
    
    # Importar e verificar se os métodos existem
    from app.api.webhooks import agno_detector
    
    # Verificar método correto
    assert hasattr(agno_detector, 'detect_media_type'), "Método detect_media_type não existe"
    assert not hasattr(agno_detector, 'detect'), "Método detect incorreto ainda existe"
    
    print("✅ Integração no webhook está correta!")
    return True

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 TESTE COMPLETO DAS CORREÇÕES MULTIMODAIS")
    print("=" * 60)
    
    try:
        # Executar testes
        test_agno_detector()
        test_detect_media_format()
        test_webhook_integration()
        
        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 60)
        print("\n✅ O sistema está pronto para produção!")
        print("✅ Os erros foram corrigidos:")
        print("   1. Problema do base64 na detect_media_format")
        print("   2. Método detect() mudado para detect_media_type()")
        print("   3. Tratamento correto do retorno (dict)")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)