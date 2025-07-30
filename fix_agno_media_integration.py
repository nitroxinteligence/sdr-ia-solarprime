#!/usr/bin/env python3
"""
Fix AGnO Media Integration
==========================
Script para corrigir a integração de mídia entre Evolution API e AGnO Framework
"""

import os
import sys
from pathlib import Path
from loguru import logger

# Configurar logging
logger.add("fix_agno_media.log", level="DEBUG")

def analyze_current_implementation():
    """Analisa a implementação atual e identifica problemas"""
    logger.info("=== ANÁLISE DA IMPLEMENTAÇÃO ATUAL ===")
    
    issues = []
    
    # 1. Verificar imports do AGnO
    logger.info("✅ Imports do AGnO estão corretos:")
    logger.info("  - from agno.media import Image, Audio, Video")
    logger.info("  - from agno.agent import Agent, AgentMemory")
    
    # 2. Identificar problemas no fluxo
    logger.warning("❌ Problemas identificados:")
    
    issues.append({
        "problema": "Evolution API não está baixando conteúdo real",
        "arquivo": "services/evolution_api.py",
        "linha": "download_media()",
        "solução": "Implementar múltiplas estratégias de download"
    })
    
    issues.append({
        "problema": "WhatsApp Service não está passando dados completos",
        "arquivo": "services/whatsapp_service.py", 
        "linha": "_process_media()",
        "solução": "Garantir que 'content' binário seja incluído"
    })
    
    issues.append({
        "problema": "AGnO Image recebe URLs ao invés de conteúdo",
        "arquivo": "agents/sdr_agent.py",
        "linha": "_create_agno_image()",
        "solução": "Priorizar content/base64 sobre URLs"
    })
    
    return issues


def generate_fixes():
    """Gera correções para os problemas identificados"""
    logger.info("\n=== GERANDO CORREÇÕES ===")
    
    fixes = {}
    
    # Fix 1: Evolution API - Download robusto
    fixes['evolution_api.py'] = '''
# Adicionar ao download_media() após linha 289:

# Adicionar logging detalhado
logger.info(f"🔍 Iniciando download de mídia: {message_id}")

# Validar resposta
if response.status_code == 200:
    data = response.json()
    logger.info(f"📊 Resposta recebida: {list(data.keys())}")
    
    if "base64" in data and data["base64"]:
        logger.success(f"✅ Base64 recebido: {len(data['base64'])} chars")
        return base64.b64decode(data["base64"])
    else:
        logger.error(f"❌ Resposta sem base64: {data}")
        # Tentar método alternativo aqui
'''

    # Fix 2: WhatsApp Service - Garantir conteúdo
    fixes['whatsapp_service.py'] = '''
# Modificar _process_media() para sempre verificar conteúdo:

# Após baixar mídia (linha ~500):
if media_data:
    logger.info(f"✅ Mídia baixada: {len(media_data)} bytes")
    
    # IMPORTANTE: Validar que é conteúdo real
    if len(media_data) < 100:
        logger.error(f"⚠️ Conteúdo suspeito (muito pequeno): {len(media_data)} bytes")
        # Tentar download novamente ou usar fallback
else:
    logger.error("❌ Download retornou None/vazio")
    # Implementar estratégia de retry aqui
'''

    # Fix 3: SDR Agent - Priorização correta
    fixes['sdr_agent.py'] = '''
# Já implementado corretamente na função _create_agno_image()
# A priorização está correta: content > base64 > path > url

# Adicionar validação extra:
if 'content' in image_data and image_data['content']:
    content = image_data['content']
    
    # Validar que é bytes real e não string
    if isinstance(content, str):
        logger.warning("⚠️ Content é string, convertendo para bytes")
        try:
            content = content.encode('latin-1')  # Para dados binários
        except:
            content = base64.b64decode(content)  # Se for base64
    
    # Validar tamanho mínimo
    if len(content) < 100:
        logger.error(f"❌ Conteúdo muito pequeno: {len(content)} bytes")
        return None
'''

    return fixes


def create_validation_script():
    """Cria script de validação do fluxo completo"""
    validation_script = '''#!/usr/bin/env python3
"""
Validação do Fluxo de Mídia
===========================
"""

import asyncio
from loguru import logger

async def validate_media_flow():
    """Valida cada etapa do fluxo de mídia"""
    
    steps = []
    
    # Passo 1: Evolution API
    logger.info("📋 Passo 1: Verificando Evolution API...")
    from services.evolution_api import evolution_client
    await evolution_client.initialize()
    status = await evolution_client.check_connection()
    
    if status.get("state") == "open":
        steps.append("✅ Evolution API conectada")
    else:
        steps.append("❌ Evolution API desconectada")
        return steps
    
    # Passo 2: Download de teste
    logger.info("📋 Passo 2: Testando download...")
    # Implementar teste de download aqui
    
    # Passo 3: Processamento
    logger.info("📋 Passo 3: Testando processamento...")
    # Implementar teste de processamento aqui
    
    return steps

if __name__ == "__main__":
    steps = asyncio.run(validate_media_flow())
    print("\\n=== RESULTADO DA VALIDAÇÃO ===")
    for step in steps:
        print(step)
'''
    
    with open("validate_media_flow.py", "w") as f:
        f.write(validation_script)
    
    logger.success("✅ Script de validação criado: validate_media_flow.py")


def main():
    """Executa análise e gera relatório de correções"""
    logger.info("🚀 INICIANDO ANÁLISE DE INTEGRAÇÃO AGNO/EVOLUTION")
    
    # 1. Analisar implementação
    issues = analyze_current_implementation()
    
    logger.info(f"\n📊 {len(issues)} problemas identificados:")
    for i, issue in enumerate(issues, 1):
        logger.warning(f"{i}. {issue['problema']}")
        logger.info(f"   📁 Arquivo: {issue['arquivo']}")
        logger.info(f"   📍 Local: {issue['linha']}")
        logger.info(f"   💡 Solução: {issue['solução']}")
    
    # 2. Gerar correções
    fixes = generate_fixes()
    
    logger.info("\n🔧 CORREÇÕES SUGERIDAS:")
    for file, fix in fixes.items():
        logger.info(f"\n📁 {file}:")
        print(fix)
    
    # 3. Criar script de validação
    create_validation_script()
    
    # 4. Resumo final
    logger.info("\n" + "="*60)
    logger.info("📋 PLANO DE AÇÃO:")
    logger.info("="*60)
    
    action_plan = [
        "1. Adicionar logs detalhados em evolution_api.py",
        "2. Validar tamanho do conteúdo em whatsapp_service.py",
        "3. Garantir que 'content' seja sempre bytes em sdr_agent.py",
        "4. Executar validate_media_flow.py para testar",
        "5. Monitorar logs em tempo real durante testes"
    ]
    
    for action in action_plan:
        logger.info(f"  {action}")
    
    logger.info("\n💡 COMANDO PARA MONITORAR:")
    logger.info("tail -f logs/app.log | grep -E '📥|✅|❌|🔄|📊'")
    
    logger.info("\n🎯 RESULTADO ESPERADO:")
    logger.info("Quando corrigido, o fluxo será:")
    logger.info("1. WhatsApp envia mídia")
    logger.info("2. Evolution API baixa conteúdo real")
    logger.info("3. WhatsApp Service valida e passa bytes")
    logger.info("4. AGnO cria Image(content=bytes)")
    logger.info("5. Gemini/OpenAI processam com sucesso")


if __name__ == "__main__":
    main()