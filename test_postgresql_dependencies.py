#!/usr/bin/env python3
"""
Teste de dependências PostgreSQL
Verifica se todas as dependências necessárias estão instaladas corretamente
"""
import sys
from loguru import logger

def test_dependencies():
    """Testa todas as dependências PostgreSQL"""
    logger.info("🧪 Testando dependências PostgreSQL...")
    
    # Teste 1: psycopg2
    try:
        import psycopg2
        logger.info(f"✅ psycopg2 disponível: versão {psycopg2.__version__}")
    except ImportError as e:
        logger.error(f"❌ psycopg2 não encontrado: {e}")
        return False
    
    # Teste 2: SQLAlchemy
    try:
        import sqlalchemy
        logger.info(f"✅ SQLAlchemy disponível: versão {sqlalchemy.__version__}")
    except ImportError as e:
        logger.error(f"❌ SQLAlchemy não encontrado: {e}")
        return False
    
    # Teste 3: Plugin PostgreSQL do SQLAlchemy
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.dialects import postgresql
        logger.info(f"✅ Plugin PostgreSQL do SQLAlchemy disponível")
    except ImportError as e:
        logger.error(f"❌ Plugin PostgreSQL do SQLAlchemy não encontrado: {e}")
        return False
    
    # Teste 4: Teste básico de engine
    try:
        engine = create_engine("postgresql://test:test@localhost:5432/test", strategy='mock', executor=lambda sql, *_: None)
        logger.info(f"✅ Engine PostgreSQL criada com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar engine PostgreSQL: {e}")
        return False
    
    # Teste 5: AGNO Storage
    try:
        from agno.storage.postgres import PostgresStorage
        logger.info(f"✅ AGNO PostgresStorage disponível")
    except ImportError as e:
        logger.error(f"❌ AGNO PostgresStorage não encontrado: {e}")
        logger.error(f"💡 Verifique se agno==1.7.6 está instalado corretamente")
        return False
    
    logger.info("🎉 Todas as dependências PostgreSQL estão funcionando!")
    return True

def test_connection():
    """Testa conexão real com PostgreSQL usando as configurações do .env"""
    logger.info("🔌 Testando conexão real...")
    
    try:
        from app.config import settings
        logger.info(f"✅ Configurações carregadas")
        
        db_url = settings.get_postgres_url()
        # Remove senha do log por segurança
        safe_url = db_url.split('@')[1] if '@' in db_url else db_url
        logger.info(f"🔗 URL: ...@{safe_url}")
        
        # Teste básico de conexão
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"✅ Conexão PostgreSQL bem-sucedida!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro de conexão: {str(e)[:200]}...")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE DEPENDÊNCIAS POSTGRESQL")
    print("=" * 60)
    
    deps_ok = test_dependencies()
    
    if deps_ok:
        print("\n" + "=" * 60)
        print("🔌 TESTE DE CONEXÃO REAL")
        print("=" * 60)
        connection_ok = test_connection()
        
        if connection_ok:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            sys.exit(0)
        else:
            print("\n⚠️ Dependências OK, mas conexão falhou")
            sys.exit(1)
    else:
        print("\n❌ DEPENDÊNCIAS COM PROBLEMA")
        print("💡 Execute: pip install -r requirements.txt")
        sys.exit(1)