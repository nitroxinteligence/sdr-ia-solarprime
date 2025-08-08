#!/usr/bin/env python3
"""
Diagnóstico do problema de soma incorreta de valores

O agente está somando R$ 350,81 + R$ 7.850,00 = R$ 8.200,81
Mas só detectamos R$ 350,81 na imagem.

Possíveis causas:
1. O agente está alucinando um valor anterior
2. Há um valor hardcoded ou exemplo no prompt
3. O contexto está sendo interpretado incorretamente
4. O agente está seguindo um exemplo do prompt literalmente
"""

import re
import json

def analisar_problema():
    print("=== ANÁLISE DO PROBLEMA DE SOMA INCORRETA ===\n")
    
    # Valores observados
    valor_detectado = 350.81
    valor_resposta = 8200.81
    valor_implicito = valor_resposta - valor_detectado
    
    print(f"Valor detectado na imagem: R$ {valor_detectado:.2f}")
    print(f"Valor mencionado na resposta: R$ {valor_resposta:.2f}")
    print(f"Valor implícito (diferença): R$ {valor_implicito:.2f}")
    print(f"\nO agente está assumindo que existe uma conta anterior de R$ {valor_implicito:.2f}")
    
    # Verificar se o valor 7850 aparece em algum lugar do código
    print("\n=== BUSCANDO VALOR 7850 NO CÓDIGO ===")
    
    arquivos_para_verificar = [
        "app/prompts/prompt-agente.md",
        "app/agents/agentic_sdr.py",
        "logs-console.md"
    ]
    
    for arquivo in arquivos_para_verificar:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                if '7850' in conteudo or '7.850' in conteudo:
                    print(f"❌ ENCONTRADO '7850' em {arquivo}")
                    # Encontrar contexto
                    linhas = conteudo.split('\n')
                    for i, linha in enumerate(linhas):
                        if '7850' in linha or '7.850' in linha:
                            print(f"  Linha {i+1}: {linha.strip()}")
                else:
                    print(f"✅ Valor 7850 NÃO encontrado em {arquivo}")
        except Exception as e:
            print(f"⚠️  Erro ao ler {arquivo}: {e}")
    
    # Verificar se há exemplos no prompt que mencionem 8200
    print("\n=== BUSCANDO VALOR 8200 NO PROMPT ===")
    
    try:
        with open("app/prompts/prompt-agente.md", 'r', encoding='utf-8') as f:
            prompt = f.read()
            
        # Buscar por 8200 ou 8.200
        matches = re.finditer(r'8[,.]?200', prompt, re.IGNORECASE)
        for match in matches:
            # Pegar contexto ao redor
            start = max(0, match.start() - 100)
            end = min(len(prompt), match.end() + 100)
            contexto = prompt[start:end]
            print(f"\n📍 Encontrado '8200' no prompt:")
            print(f"   Contexto: ...{contexto}...")
    
    except Exception as e:
        print(f"⚠️  Erro ao analisar prompt: {e}")
    
    print("\n=== HIPÓTESES ===")
    print("1. O agente pode estar seguindo um exemplo do prompt que menciona 'duas contas'")
    print("2. O agente pode estar alucinando baseado no contexto de 'múltiplas contas'")
    print("3. Pode haver uma instrução no prompt para sempre assumir múltiplas contas")
    
    print("\n=== RECOMENDAÇÕES ===")
    print("1. Verificar se o prompt tem exemplos com valores específicos")
    print("2. Garantir que o agente só mencione valores que foram explicitamente detectados")
    print("3. Adicionar validação para prevenir alucinações de valores")
    print("4. Instruir o agente a NUNCA inventar valores não mencionados")

if __name__ == "__main__":
    analisar_problema()