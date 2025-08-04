#!/usr/bin/env python3
"""
Teste do sistema de detecção de mídia criptografada do WhatsApp
"""
import sys
import os
sys.path.insert(0, '.')

def test_encrypted_detection():
    """Testa detecção de mídia criptografada"""
    print("\n" + "="*60)
    print("🔒 TESTE DE DETECÇÃO DE MÍDIA CRIPTOGRAFADA")
    print("="*60)
    
    from app.utils.agno_media_detection import agno_media_detector
    
    # Padrões conhecidos de mídia criptografada do WhatsApp (dos logs)
    encrypted_samples = [
        bytes.fromhex("cfee6a4ee9379ab2dbdcd2dc"),  # Imagem criptografada
        bytes.fromhex("4c57185dbd36f3b9ab4c2492"),  # PDF criptografado
        bytes.fromhex("aa303b02f755fa93b25abdcb"),  # Áudio criptografado
        bytes.fromhex("03aeae12a76938c893465655"),  # Outro padrão
    ]
    
    # Padrões de mídia válida
    valid_samples = [
        bytes.fromhex("ffd8ffe000104a464946"),  # JPEG válido
        bytes.fromhex("89504e470d0a1a0a"),  # PNG válido
        bytes.fromhex("255044462d"),  # PDF válido (%PDF-)
    ]
    
    print("\n📊 Testando mídia criptografada:")
    print("-" * 40)
    
    for i, sample in enumerate(encrypted_samples, 1):
        result = agno_media_detector.detect_media_type(sample)
        
        print(f"\nAmostra {i} (hex: {sample[:4].hex()}):")
        print(f"  • Detectado: {result.get('detected')}")
        print(f"  • Formato: {result.get('format')}")
        print(f"  • Criptografado: {result.get('is_encrypted', False)}")
        print(f"  • Magic bytes: {result.get('magic_bytes', 'N/A')}")
        
        if result.get('is_encrypted'):
            print("  ✅ Corretamente identificado como criptografado!")
        elif not result.get('detected'):
            print("  ⚠️ Não detectado mas não marcado como criptografado")
        else:
            print("  ❌ ERRO: Deveria ser detectado como criptografado!")
    
    print("\n📊 Testando mídia válida:")
    print("-" * 40)
    
    for i, sample in enumerate(valid_samples, 1):
        result = agno_media_detector.detect_media_type(sample)
        
        print(f"\nAmostra válida {i} (hex: {sample[:4].hex()}):")
        print(f"  • Detectado: {result.get('detected')}")
        print(f"  • Formato: {result.get('format')}")
        print(f"  • Criptografado: {result.get('is_encrypted', False)}")
        
        if result.get('detected') and not result.get('is_encrypted'):
            print("  ✅ Corretamente identificado como mídia válida!")
        else:
            print("  ❌ ERRO: Deveria ser detectado como mídia válida!")
    
    print("\n" + "="*60)
    print("📊 RESUMO DO TESTE")
    print("="*60)

def test_webhook_detection():
    """Testa a função detect_media_format do webhook"""
    print("\n📋 Testando detect_media_format:")
    print("-" * 40)
    
    from app.api.webhooks import detect_media_format
    
    # Testar diferentes formatos
    test_cases = [
        ("", "unknown"),
        (None, "unknown"),
        ("data:image/png;base64,iVBORw0KG", "data_url"),
        ("https://example.com/image.jpg", "url"),
        ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", "base64"),
        ("hello world", "unknown"),
    ]
    
    for input_data, expected in test_cases:
        result = detect_media_format(input_data)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: {str(input_data)[:30]}... → {result} (esperado: {expected})")
    
    print("\n✅ Teste de detect_media_format concluído!")

def main():
    """Executa todos os testes"""
    try:
        test_encrypted_detection()
        test_webhook_detection()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        print("\n💡 Próximos passos:")
        print("1. Fazer commit das alterações")
        print("2. Fazer push para o GitHub")
        print("3. Testar em produção com mídia real do WhatsApp")
        print("4. Monitorar logs para confirmar que mídia criptografada é detectada")
        
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)