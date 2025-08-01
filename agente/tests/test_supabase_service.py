"""
Script de teste para o SupabaseService
Executa testes básicos de conectividade e operações CRUD
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

from agente.services.supabase_service import get_supabase_service
from agente.core.logger import get_logger

logger = get_logger("test_supabase")


async def test_supabase_service():
    """Testa as funcionalidades básicas do SupabaseService"""
    
    logger.info("🧪 Iniciando teste do SupabaseService...")
    
    try:
        # Obter instância do serviço
        supabase = get_supabase_service()
        
        # 1. Teste de saúde
        logger.info("\n1️⃣ Testando conexão com Supabase...")
        health_ok = await supabase.health_check()
        if health_ok:
            logger.info("✅ Conexão com Supabase está OK!")
        else:
            logger.error("❌ Falha na conexão com Supabase")
            return
        
        # 2. Teste de busca de lead
        logger.info("\n2️⃣ Testando busca de lead...")
        test_phone = "5511999999999"
        lead = await supabase.get_lead_by_phone(test_phone)
        if lead:
            logger.info(f"✅ Lead encontrado: {lead.name} ({lead.phone_number})")
        else:
            logger.info(f"ℹ️ Lead não encontrado para telefone: {test_phone}")
        
        # 3. Teste de busca de mensagens
        logger.info("\n3️⃣ Testando busca de mensagens...")
        messages = await supabase.get_last_messages(test_phone, limit=10)
        logger.info(f"✅ {len(messages)} mensagens encontradas")
        
        # 4. Teste de busca de follow-ups pendentes
        logger.info("\n4️⃣ Testando busca de follow-ups pendentes...")
        follow_ups = await supabase.get_pending_follow_ups(limit=5)
        logger.info(f"✅ {len(follow_ups)} follow-ups pendentes encontrados")
        
        # 5. Teste de busca de profile
        logger.info("\n5️⃣ Testando busca de profile...")
        profile = await supabase.get_profile_by_phone(test_phone)
        if profile:
            logger.info(f"✅ Profile encontrado: {profile.phone}")
        else:
            logger.info(f"ℹ️ Profile não encontrado para telefone: {test_phone}")
        
        logger.info("\n✅ Todos os testes concluídos com sucesso!")
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante os testes: {str(e)}")
        raise


if __name__ == "__main__":
    # Executar testes
    asyncio.run(test_supabase_service())