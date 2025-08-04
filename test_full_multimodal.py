#!/usr/bin/env python3
"""
Teste completo do sistema multimodal após todas as correções
"""
import sys
import os
sys.path.insert(0, '.')

def test_webhooks_import():
    """Testa se o webhook pode ser importado sem erros"""
    print("\n🔍 Testando import do webhook...")
    try:
        from app.api import webhooks
        print("✅ Webhook importado com sucesso")
        
        # Verificar se as funções existem
        assert hasattr(webhooks, 'detect_media_format'), "Função detect_media_format não existe"
        assert hasattr(webhooks, 'agno_detector'), "agno_detector não existe"
        print("✅ Funções críticas existem")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao importar webhook: {e}")
        return False

def test_detect_media_format():
    """Testa a função detect_media_format com casos reais"""
    print("\n🔍 Testando detect_media_format...")
    
    try:
        from app.api.webhooks import detect_media_format
        
        # Teste 1: Base64 real do WhatsApp (thumbnail)
        whatsapp_thumbnail = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHB"
        result = detect_media_format(whatsapp_thumbnail)
        assert result == 'base64', f"WhatsApp thumbnail deveria ser base64, mas foi {result}"
        print(f"✅ WhatsApp thumbnail detectado como: {result}")
        
        # Teste 2: String curta (não base64)
        short_string = "hello"
        result = detect_media_format(short_string)
        assert result == 'unknown', f"String curta deveria ser unknown, mas foi {result}"
        print(f"✅ String curta detectada como: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Erro em detect_media_format: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agno_detector():
    """Testa o AGNOMediaDetector com dados reais"""
    print("\n🔍 Testando AGNOMediaDetector...")
    
    try:
        from app.api.webhooks import agno_detector
        
        # Teste com JPEG real (magic bytes)
        jpeg_data = bytes.fromhex("ffd8ffe000104a464946")
        result = agno_detector.detect_media_type(jpeg_data)
        
        assert result.get('detected') == True, "JPEG deveria ser detectado"
        assert result.get('format') == 'jpeg', f"Formato deveria ser jpeg, mas foi {result.get('format')}"
        print(f"✅ JPEG detectado: {result.get('format')}")
        
        # Teste com dados desconhecidos (WhatsApp encrypted)
        unknown_data = bytes.fromhex("03aeae12a76938c8")
        result = agno_detector.detect_media_type(unknown_data)
        
        assert result.get('detected') == False, "Dados desconhecidos não deveriam ser detectados"
        print(f"✅ Dados desconhecidos tratados corretamente")
        
        return True
    except Exception as e:
        print(f"❌ Erro no AGNOMediaDetector: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base64_operations():
    """Testa se as operações base64 funcionam corretamente"""
    print("\n🔍 Testando operações base64...")
    
    try:
        # Simular o contexto do webhook
        import base64 as b64_module
        
        # Teste de encode
        test_bytes = b"Hello World"
        encoded = b64_module.b64encode(test_bytes).decode('utf-8')
        print(f"✅ Encode funcionando: {len(encoded)} chars")
        
        # Teste de decode
        decoded = b64_module.b64decode(encoded)
        assert decoded == test_bytes, "Decode falhou"
        print(f"✅ Decode funcionando: {len(decoded)} bytes")
        
        return True
    except Exception as e:
        print(f"❌ Erro nas operações base64: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 TESTE COMPLETO DO SISTEMA MULTIMODAL")
    print("=" * 60)
    
    all_passed = True
    
    # Executar testes
    tests = [
        test_webhooks_import,
        test_detect_media_format,
        test_agno_detector,
        test_base64_operations
    ]
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para deploy")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️ Revisar os erros acima")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)