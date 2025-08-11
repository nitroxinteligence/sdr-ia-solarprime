#!/usr/bin/env python3
"""
Script de teste para verificar o fluxo completo de qualificação de leads
"""

import asyncio
from datetime import datetime
from loguru import logger

# Configurar logging detalhado
logger.add("test_qualification_flow.log", rotation="10 MB", level="DEBUG")

async def test_qualification_flow():
    """Testa o fluxo completo de qualificação"""
    
    logger.info("=== INICIANDO TESTE DE FLUXO DE QUALIFICAÇÃO ===")
    
    # Simulação de dados do lead
    lead_data = {
        "id": "test-lead-123",
        "phone_number": "+5511999999999",
        "name": "Cliente Teste Qualificado",
        "bill_value": 5000,  # R$ 5.000 - qualifica como LEAD_QUENTE
        "is_decision_maker": True,
        "has_solar_system": False,
        "current_stage": None,  # Será definido pelo agente
        "qualification_status": None,
        "qualification_score": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    logger.info(f"📋 Lead de teste criado: {lead_data}")
    
    # Passo 1: Verificar lógica de qualificação do agente
    logger.info("\n=== PASSO 1: LÓGICA DE QUALIFICAÇÃO DO AGENTE ===")
    
    # Simulação da lógica do agente (baseado no código real)
    bill_value = lead_data["bill_value"]
    is_decision_maker = lead_data["is_decision_maker"]
    has_solar_system = lead_data["has_solar_system"]
    
    qualificado = False
    qualification_reason = []
    
    # Critérios de qualificação
    if bill_value >= 200 and is_decision_maker and not has_solar_system:
        qualificado = True
        qualification_reason.append("Conta >= R$ 200")
        qualification_reason.append("É tomador de decisão")
        qualification_reason.append("Não tem sistema solar")
        
        # Determinar categoria
        if bill_value >= 600:
            categoria = "LEAD_QUENTE"
        elif bill_value >= 400:
            categoria = "IDEAL"
        else:
            categoria = "QUALIFICADO"
    else:
        categoria = "BAIXO"
        if bill_value < 200:
            qualification_reason.append("Conta < R$ 200")
        if not is_decision_maker:
            qualification_reason.append("Não é tomador de decisão")
        if has_solar_system:
            qualification_reason.append("Já tem sistema solar")
    
    novo_stage = "QUALIFICADO" if qualificado else "EM_QUALIFICACAO"
    
    logger.info(f"✅ Qualificado: {qualificado}")
    logger.info(f"📊 Categoria: {categoria}")
    logger.info(f"🎯 Novo stage: {novo_stage}")
    logger.info(f"📝 Razões: {', '.join(qualification_reason)}")
    
    # Passo 2: Atualização no banco de dados
    logger.info("\n=== PASSO 2: ATUALIZAÇÃO NO BANCO DE DADOS ===")
    
    update_data = {
        "current_stage": novo_stage,
        "qualification_status": "QUALIFIED" if qualificado else None,
        "qualification_score": 80 if qualificado else None,  # Score simulado
        "updated_at": datetime.now().isoformat()
    }
    
    logger.info(f"📤 Dados para atualização: {update_data}")
    logger.info("💾 [SIMULADO] supabase_client.update_lead() chamado")
    
    # Passo 3: Sincronização com Kommo
    logger.info("\n=== PASSO 3: SINCRONIZAÇÃO COM KOMMO ===")
    
    # Simulação do mapeamento de stages
    stage_mapping = {
        "QUALIFICADO": "qualificado"
    }
    
    kommo_stage = stage_mapping.get(novo_stage)
    logger.info(f"🔄 Mapeamento: {novo_stage} → {kommo_stage}")
    
    # Simulação dos IDs de stages do pipeline
    pipeline_stages = {
        "novo_lead": 12345678,
        "em_negociacao": 12345679,
        "em_qualificacao": 12345680,
        "qualificado": 12345681,  # Este ID deve existir no Kommo
        "reuniao_agendada": 12345682,
        "reuniao_finalizada": 12345683,
        "nao_interessado": 12345684
    }
    
    stage_id = pipeline_stages.get(kommo_stage)
    logger.info(f"🔢 ID do stage no Kommo: {stage_id}")
    
    if stage_id:
        logger.info(f"✅ Stage ID encontrado: {stage_id}")
        logger.info("📡 [SIMULADO] move_card_to_pipeline() seria chamado com:")
        logger.info(f"   - lead_id: {lead_data.get('kommo_lead_id', 'XXXXX')}")
        logger.info(f"   - pipeline_id: 1234567 (do settings)")
        logger.info(f"   - stage_id: {stage_id}")
    else:
        logger.error(f"❌ Stage ID não encontrado para: {kommo_stage}")
    
    # Passo 4: Verificar possíveis pontos de falha
    logger.info("\n=== PASSO 4: ANÁLISE DE POSSÍVEIS FALHAS ===")
    
    potential_issues = []
    
    # Verificação 1: Stage mapping
    if novo_stage not in stage_mapping:
        potential_issues.append(f"Stage '{novo_stage}' não está no stage_mapping")
    
    # Verificação 2: Pipeline stages
    if kommo_stage and kommo_stage not in pipeline_stages:
        potential_issues.append(f"Stage '{kommo_stage}' não tem ID no pipeline_stages")
    
    # Verificação 3: Nome do stage no Kommo
    logger.info("\n🔍 Verificando configuração do Kommo:")
    logger.info("   O pipeline do Kommo deve ter um stage chamado exatamente 'Qualificado'")
    logger.info("   para que o mapeamento funcione corretamente")
    
    # Verificação 4: Lead tem kommo_lead_id?
    if not lead_data.get("kommo_lead_id"):
        potential_issues.append("Lead não tem kommo_lead_id - precisa ser criado primeiro no Kommo")
    
    if potential_issues:
        logger.warning("\n⚠️ POSSÍVEIS PROBLEMAS ENCONTRADOS:")
        for issue in potential_issues:
            logger.warning(f"   - {issue}")
    else:
        logger.info("\n✅ Nenhum problema óbvio encontrado no fluxo")
    
    # Resumo final
    logger.info("\n=== RESUMO DO FLUXO ===")
    logger.info(f"1. Agente identifica como: {novo_stage}")
    logger.info(f"2. Salva no banco como: current_stage = '{novo_stage}'")
    logger.info(f"3. Sincronização mapeia para: '{kommo_stage}'")
    logger.info(f"4. Pipeline tem ID {stage_id} para '{kommo_stage}'")
    logger.info(f"5. API do Kommo é chamada para mover o lead")
    
    logger.info("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    asyncio.run(test_qualification_flow())