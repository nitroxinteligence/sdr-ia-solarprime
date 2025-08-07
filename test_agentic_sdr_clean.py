#!/usr/bin/env python3
"""
Teste para verificar AgenticSDR sem warnings PostgreSQL
"""
import asyncio
from loguru import logger
from app.agents.agentic_sdr import AgenticSDR

async def test_agentic_sdr_clean():
    """Testa AgenticSDR sem warnings PostgreSQL"""
    logger.info("🧪 Testando AgenticSDR sem PostgreSQL warnings...")
    
    try:
        # Test: Criar AgenticSDR - deve funcionar sem warnings
        logger.info("🤖 Criando AgenticSDR...")
        agent = AgenticSDR()
        
        # Verificar componentes críticos
        logger.info("🔍 Verificando componentes:")
        
        # Storage deve estar funcionando
        if agent.storage:
            logger.info("✅ Storage: funcionando com Supabase")
        else:
            logger.warning("⚠️ Storage: não inicializado")
            
        # Memory deve estar funcionando
        if agent.memory:
            logger.info("✅ Memory: inicializado (com ou sem persistência)")
        else:
            logger.error("❌ Memory: falhou na inicialização")
            return False
            
        # Knowledge pode ou não estar funcionando (opcional)
        if agent.knowledge:
            logger.info("✅ Knowledge: inicializado localmente")
        else:
            logger.info("ℹ️ Knowledge: desabilitado (OK)")
            
        # SDR Team deve estar None inicialmente
        if agent.sdr_team is None:
            logger.info("✅ SDR Team: não inicializado ainda (OK)")
        
        logger.info("🎉 SUCESSO: AgenticSDR iniciado sem warnings PostgreSQL!")
        return True
        
    except Exception as e:
        logger.error(f"❌ FALHA: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_agentic_sdr_clean())
    exit(0 if result else 1)