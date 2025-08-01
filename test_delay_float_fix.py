#!/usr/bin/env python3
"""
Teste da correção de delay float para send_text_message
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_delay_float_validation():
    """Testa se send_text_message aceita delay float"""
    print("🧪 TESTE CORREÇÃO DELAY FLOAT")
    print("=" * 35)
    
    try:
        # Import da tool corrigida
        from agente.tools.whatsapp.send_text_message import send_text_message
        import inspect
        
        # AGnO wraps functions, get the actual function
        actual_function = send_text_message
        if hasattr(send_text_message, 'entrypoint'):
            actual_function = send_text_message.entrypoint
            print("   Using AGnO entrypoint function")
        
        # Verificar signature da função
        sig = inspect.signature(actual_function)
        delay_param = sig.parameters.get('delay')
        
        print("1. Verificando assinatura da função...")
        print(f"   delay parameter: {delay_param}")
        
        if delay_param:
            print(f"   delay annotation: {delay_param.annotation}")  
            print(f"   delay default: {delay_param.default}")
            
            # Verificar se é Optional[float]
            annotation_str = str(delay_param.annotation)
            is_float_type = 'float' in annotation_str and ('Optional' in annotation_str or 'Union' in annotation_str)
            
            if is_float_type:
                print("   ✅ delay aceita float corretamente!")
                result = True
            else:
                print("   ❌ delay ainda não aceita float")
                result = False
        else:
            print("   ❌ parâmetro delay não encontrado")
            result = False
            
    except Exception as e:
        print(f"   ❌ Erro no teste: {str(e)}")
        import traceback
        print(f"   Stack trace: {traceback.format_exc()}")
        result = False
    
    print("\n" + "=" * 35)
    if result:
        print("🎉 CORREÇÃO VALIDADA COM SUCESSO!")
        print("✅ send_text_message agora aceita delay float")
        print("✅ AGnO Agent pode passar valores como 1.5, 0.8")
        print("✅ Erro de validation resolvido!")
    else:
        print("❌ CORREÇÃO AINDA PENDENTE")
        
    return result

def test_type_annotation_details():
    """Testa detalhes das type annotations"""
    print("\n🔍 ANÁLISE DETALHADA DAS TYPE ANNOTATIONS")
    print("=" * 45)
    
    try:
        from agente.tools.whatsapp.send_text_message import send_text_message
        import inspect
        from typing import get_type_hints
        
        # AGnO wraps functions, get the actual function
        actual_function = send_text_message
        if hasattr(send_text_message, 'entrypoint'):
            actual_function = send_text_message.entrypoint
            print("   Using AGnO entrypoint function")
        
        # Get type hints
        hints = get_type_hints(actual_function)
        print(f"Type hints: {hints}")
        
        # Verificar especificamente o delay
        delay_hint = hints.get('delay')
        print(f"delay type hint: {delay_hint}")
        
        # Testar se aceita float
        import typing
        if hasattr(typing, '_GenericAlias'):
            # Python 3.9+
            origin = getattr(delay_hint, '__origin__', None)
            args = getattr(delay_hint, '__args__', ())
            print(f"delay origin: {origin}")
            print(f"delay args: {args}")
            
            if origin is typing.Union and float in args:
                print("✅ delay aceita float (Union com float)")
                return True
            elif delay_hint is float:
                print("✅ delay é float direto")
                return True
        
        # Fallback: verificar string representation
        delay_str = str(delay_hint)
        print(f"delay string representation: {delay_str}")
        
        if 'float' in delay_str:
            print("✅ delay contém float na representação")
            return True
        else:
            print("❌ delay não parece aceitar float")
            return False
            
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")
        return False

def main():
    """Executa todos os testes"""
    print("🔧 VALIDAÇÃO DA CORREÇÃO DELAY FLOAT")
    print("=" * 50)
    
    try:
        test1 = test_delay_float_validation()
        test2 = test_type_annotation_details()
        
        print("\n" + "=" * 50)
        print("📋 RESULTADO FINAL:")
        print(f"   Teste 1 (Signature): {'✅ PASSOU' if test1 else '❌ FALHOU'}")
        print(f"   Teste 2 (Type Hints): {'✅ PASSOU' if test2 else '❌ FALHOU'}")
        
        if test1 and test2:
            print("\n🎉 CORREÇÃO DELAY FLOAT VALIDADA!")
            print("🚀 AGnO Agent deve funcionar corretamente agora!")
            print("✅ Erro 'Input should be a valid integer' resolvido")
        else:
            print("\n❌ CORREÇÃO AINDA INCOMPLETA")
            
        return test1 and test2
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)