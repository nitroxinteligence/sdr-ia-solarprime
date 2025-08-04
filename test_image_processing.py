#!/usr/bin/env python3
"""
Script de teste para validar o processamento de imagens corrigido
"""

import base64
import tempfile
import os
from pathlib import Path

# Simular dados de teste
def create_test_image_base64():
    """Cria uma imagem JPEG de teste em base64"""
    # Este é um JPEG 1x1 pixel vermelho válido em base64
    jpeg_base64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
    return jpeg_base64

def test_agno_image_with_bytes():
    """Testa se AgnoImage aceita bytes"""
    try:
        from agno.media import Image as AgnoImage
        
        # Criar base64 de teste
        test_base64 = create_test_image_base64()
        
        # Decodificar para bytes
        image_bytes = base64.b64decode(test_base64)
        
        # Tentar criar AgnoImage com bytes
        print("✅ Testando AgnoImage com bytes...")
        agno_image = AgnoImage(
            content=image_bytes,
            format='jpeg',
            detail='high'
        )
        print("✅ AgnoImage criado com sucesso usando bytes!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar AgnoImage com bytes: {e}")
        return False

def test_agno_image_with_filepath():
    """Testa se AgnoImage aceita filepath"""
    try:
        from agno.media import Image as AgnoImage
        
        # Criar base64 de teste
        test_base64 = create_test_image_base64()
        
        # Decodificar para bytes
        image_bytes = base64.b64decode(test_base64)
        
        # Salvar em arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(image_bytes)
            temp_path = tmp_file.name
        
        try:
            # Tentar criar AgnoImage com filepath
            print("✅ Testando AgnoImage com filepath...")
            agno_image = AgnoImage(
                filepath=temp_path,
                format='jpeg',
                detail='high'
            )
            print("✅ AgnoImage criado com sucesso usando filepath!")
            return True
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"❌ Erro ao criar AgnoImage com filepath: {e}")
        return False

def test_agno_image_with_base64():
    """Testa se AgnoImage aceita base64 string"""
    try:
        from agno.media import Image as AgnoImage
        
        # Criar base64 de teste
        test_base64 = create_test_image_base64()
        
        # Tentar criar AgnoImage com base64
        print("✅ Testando AgnoImage com base64 string...")
        agno_image = AgnoImage(
            content=test_base64,
            format='jpeg',
            detail='high'
        )
        print("✅ AgnoImage criado com sucesso usando base64 string!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar AgnoImage com base64: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTE DE PROCESSAMENTO DE IMAGEM AGNO")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Bytes
    print("\n📋 Teste 1: AgnoImage com bytes")
    results.append(("Bytes", test_agno_image_with_bytes()))
    
    # Teste 2: Filepath
    print("\n📋 Teste 2: AgnoImage com filepath")
    results.append(("Filepath", test_agno_image_with_filepath()))
    
    # Teste 3: Base64
    print("\n📋 Teste 3: AgnoImage com base64 string")
    results.append(("Base64", test_agno_image_with_base64()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:15} : {status}")
    
    # Conclusão
    successful_methods = [name for name, success in results if success]
    if successful_methods:
        print(f"\n✅ Métodos funcionais: {', '.join(successful_methods)}")
        print("🎯 A correção implementada deve funcionar!")
    else:
        print("\n❌ Nenhum método funcionou. Verifique a instalação do AGNO.")

if __name__ == "__main__":
    main()