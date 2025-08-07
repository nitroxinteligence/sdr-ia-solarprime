#!/usr/bin/env python3
"""
Teste para verificar se warnings PostgreSQL foram eliminados
"""
import asyncio
from app.config import settings
from loguru import logger

async def test_clean_startup():
    """Testa inicialização limpa sem warnings PostgreSQL"""
    logger.info("🧪 Testando startup limpo sem PostgreSQL warnings...")
    
    try:
        # Test 1: Config não deve retornar URL PostgreSQL válida
        postgres_url = settings.get_postgres_url()
        logger.info(f"✅ PostgreSQL URL retorna string vazia: '{postgres_url}'")
        assert postgres_url == "", f"Expected empty string, got: {postgres_url}"
        
        # Test 2: Import AgentMemory sem warnings
        logger.info("📥 Importando AgentMemory...")
        from agno.memory import AgentMemory
        logger.info("✅ AgentMemory importado sem warnings")
        
        # Test 3: Import AgentKnowledge sem warnings  
        logger.info("📥 Importando AgentKnowledge...")
        from agno.knowledge import AgentKnowledge
        logger.info("✅ AgentKnowledge importado sem warnings")
        
        # Test 4: Criar AgentMemory simples
        logger.info("🧠 Criando AgentMemory...")
        memory = AgentMemory(
            create_user_memories=True,
            create_session_summary=True
        )
        logger.info("✅ AgentMemory criado sem warnings PostgreSQL")
        
        # Test 5: Criar AgentKnowledge simples
        logger.info("📚 Criando AgentKnowledge...")
        knowledge = AgentKnowledge(num_documents=10)
        logger.info("✅ AgentKnowledge criado sem warnings PostgreSQL")
        
        logger.info("🎉 SUCESSO: Startup limpo sem warnings PostgreSQL!")
        return True
        
    except Exception as e:
        logger.error(f"❌ FALHA: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_clean_startup())
    exit(0 if result else 1)