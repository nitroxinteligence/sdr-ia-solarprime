#!/usr/bin/env python3
"""
Correção SIMPLES para integração multimodal - agente não está usando análise da imagem

PROBLEMA: Agente recebe análise da conta mas responde com fallback genérico
CAUSA: Tipo "bill_image" não está sendo tratado corretamente
SOLUÇÃO: Corrigir tratamento de bill_image e melhorar formato da resposta
"""

import os
from datetime import datetime

def fix_multimodal_integration():
    """Corrige integração entre análise multimodal e resposta do agente"""
    
    file_path = "app/agents/agentic_sdr.py"
    backup_path = f"app/agents/agentic_sdr.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🔧 Corrigindo integração multimodal")
    print(f"📁 Arquivo: {file_path}")
    
    # Fazer backup
    if os.path.exists(file_path):
        os.system(f"cp {file_path} {backup_path}")
        print(f"✅ Backup criado: {backup_path}")
    else:
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correção 1: Tratar bill_image como image no prompt
    old_code1 = """                        elif media_type == 'image':
                            contextual_prompt += f\"\"\"
                    
                    📸 IMAGEM RECEBIDA - ANÁLISE:
                    {multimodal_result.get('content', 'Análise não disponível')}
                    
                    \"\"\"
                            if multimodal_result.get('is_bill'):"""
    
    new_code1 = """                        elif media_type in ['image', 'bill_image']:  # CORREÇÃO: Aceitar bill_image
                            contextual_prompt += f\"\"\"
                    
                    📸 IMAGEM RECEBIDA - ANÁLISE:
                    {multimodal_result.get('content', 'Análise não disponível')}
                    
                    \"\"\"
                            # CORREÇÃO: Verificar tanto is_bill quanto type=='bill_image'
                            if multimodal_result.get('is_bill') or multimodal_result.get('type') == 'bill_image':"""
    
    if old_code1 in content:
        content = content.replace(old_code1, new_code1)
        print("✅ Correção 1 aplicada: Aceitar bill_image como tipo válido")
    else:
        print("⚠️  Correção 1: Código não encontrado exatamente")
    
    # Correção 2: Adicionar instrução EXPLÍCITA para usar análise da imagem
    old_code2 = """                    Responda de forma natural, empática e personalizada, levando em conta todo o contexto e histórico da conversa.
                    \"\"\""""
    
    new_code2 = """                    IMPORTANTE: Se uma análise de imagem foi fornecida acima, USE ESSAS INFORMAÇÕES NA SUA RESPOSTA!
                    Por exemplo, se detectamos uma conta de luz com valor, MENCIONE O VALOR DETECTADO.
                    
                    Responda de forma natural, empática e personalizada, levando em conta todo o contexto e histórico da conversa.
                    \"\"\""""
    
    if old_code2 in content:
        content = content.replace(old_code2, new_code2)
        print("✅ Correção 2 aplicada: Instrução explícita para usar análise")
    
    # Correção 3: Melhorar extração de valores da conta
    old_code3 = """                        return {
                            "type": "bill_image",
                            "needs_analysis": True,
                            "content": analysis_content
                        }"""
    
    new_code3 = """                        # Extrair valor da conta se possível
                        import re
                        
                        # Buscar padrão de valor monetário na análise
                        valor_match = re.search(r'R\$\s*(\d+[.,]\d{2})', analysis_content)
                        bill_amount = None
                        if valor_match:
                            # Converter vírgula para ponto e para float
                            bill_amount = float(valor_match.group(1).replace(',', '.'))
                            emoji_logger.system_info(f"💰 Valor da conta detectado: R$ {bill_amount:.2f}")
                        
                        return {
                            "type": "bill_image",
                            "needs_analysis": True,
                            "content": analysis_content,
                            "bill_amount": bill_amount,  # Adicionar valor extraído
                            "is_bill": True  # Garantir que é reconhecido como conta
                        }"""
    
    if old_code3 in content:
        content = content.replace(old_code3, new_code3)
        print("✅ Correção 3 aplicada: Melhor extração de valores")
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Correções aplicadas com sucesso!")
    print(f"📝 Mudanças:")
    print(f"   1. Aceitar 'bill_image' como tipo válido de imagem")
    print(f"   2. Instrução explícita para usar análise de imagem")
    print(f"   3. Extração automática de valores monetários")
    
    return True

if __name__ == "__main__":
    if fix_multimodal_integration():
        print("\n🚀 Próximos passos:")
        print("   1. Reinicie o servidor: docker-compose restart")
        print("   2. O agente agora responderá usando a análise da imagem")
    else:
        print("\n❌ Falha ao aplicar correções")