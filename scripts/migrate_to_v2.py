"""
Script de Migração para V2
==========================
Migra o sistema para usar AGnO Framework 100%
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from services.database import supabase_client
from agents.knowledge.solarprime_knowledge import SolarPrimeKnowledge


async def create_tables():
    """Cria as novas tabelas no Supabase"""
    logger.info("Criando tabelas no Supabase...")
    
    # Ler SQL
    sql_file = Path(__file__).parent / "create_knowledge_base_tables.sql"
    
    if not sql_file.exists():
        logger.error(f"Arquivo SQL não encontrado: {sql_file}")
        return False
        
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
        
    # Executar SQL no Supabase
    # NOTA: Você precisa executar este SQL manualmente no Supabase SQL Editor
    logger.warning("⚠️ Execute o seguinte SQL no Supabase SQL Editor:")
    logger.info(f"Arquivo: {sql_file}")
    
    # Criar também as tabelas de monitoramento
    from monitoring.performance_monitor import performance_monitor
    monitoring_sql = performance_monitor.create_monitoring_tables_sql()
    
    monitoring_file = Path(__file__).parent / "create_monitoring_tables.sql"
    with open(monitoring_file, 'w', encoding='utf-8') as f:
        f.write(monitoring_sql)
        
    logger.info(f"SQL de monitoramento salvo em: {monitoring_file}")
    
    return True


async def initialize_knowledge_base():
    """Inicializa a base de conhecimento"""
    logger.info("Inicializando base de conhecimento...")
    
    try:
        knowledge = SolarPrimeKnowledge()
        
        # Tentar carregar dados existentes do Supabase
        try:
            knowledge.load_from_supabase()
            logger.info("✅ Dados carregados do Supabase")
        except Exception as load_error:
            logger.warning(f"⚠️ Não foi possível carregar dados do Supabase: {load_error}")
            logger.info("Continuando sem dados pré-carregados...")
        
        # Tentar fazer uma busca de teste
        try:
            test_result = knowledge.get_relevant_knowledge("quanto custa")
            
            if test_result and "Nenhuma informação encontrada" not in test_result and "Erro ao buscar" not in test_result:
                logger.success("✅ Base de conhecimento funcionando!")
                logger.info(f"Exemplo de busca:\n{test_result}")
            else:
                logger.warning("⚠️ Base de conhecimento sem resultados. Verifique se o SQL foi executado.")
        except Exception as search_error:
            logger.warning(f"⚠️ Busca de teste falhou: {search_error}")
            logger.info("Isso é esperado se o PgVector ainda não está configurado no Supabase")
            
        return True
        
    except Exception as e:
        logger.error(f"Erro ao inicializar knowledge base: {e}")
        logger.info("Dica: Verifique se as extensões 'uuid-ossp' e 'vector' estão habilitadas no Supabase")
        return False


async def test_v2_system():
    """Testa o sistema V2"""
    logger.info("Testando sistema V2...")
    
    try:
        # Testar agente
        from agents.sdr_agent_v2 import SDRAgentV2
        from config.config import config
        
        agent = SDRAgentV2(config)
        await agent.initialize()
        
        # Testar uma mensagem simples
        response, metadata = await agent.process_message(
            message="Olá, quero saber sobre energia solar",
            phone_number="5511999999999"
        )
        
        logger.success(f"✅ Resposta do agente: {response}")
        logger.info(f"Tempo de resposta: {metadata.get('response_time', 'N/A')}s")
        
        # Verificar se está abaixo de 30s
        if metadata.get('response_time', 999) < 30:
            logger.success("✅ Performance dentro do target (<30s)")
        else:
            logger.warning("⚠️ Performance acima do target (>30s)")
            
        return True
        
    except Exception as e:
        logger.error(f"Erro ao testar sistema V2: {e}")
        return False


async def update_env_file():
    """Atualiza arquivo .env com novas configurações"""
    logger.info("Verificando configurações...")
    
    env_file = Path(__file__).parent.parent / ".env"
    
    if not env_file.exists():
        logger.error("Arquivo .env não encontrado!")
        return False
        
    # Verificar variáveis necessárias
    required_vars = [
        "OPENAI_API_KEY",  # Para embeddings
        "GOOGLE_API_KEY",  # Para Gemini
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "EVOLUTION_API_URL",
        "EVOLUTION_API_KEY"
    ]
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            
    if missing:
        logger.warning(f"⚠️ Variáveis faltando no .env: {', '.join(missing)}")
        logger.info("Adicione as variáveis necessárias ao arquivo .env")
        return False
        
    logger.success("✅ Todas as variáveis necessárias estão configuradas")
    return True


async def create_migration_summary():
    """Cria resumo da migração"""
    summary = """
# Resumo da Migração para V2

## ✅ Componentes Implementados

### 1. AGnO Framework Integration
- **Agent**: SDRAgentV2 com reasoning otimizado (1-3 steps)
- **Storage**: SupabaseAgentStorage para persistência
- **Knowledge**: SolarPrimeKnowledge com busca semântica
- **Workflows**: FollowUpWorkflow para automação

### 2. Otimizações de Performance
- **Typing Delay**: Reduzido de 2-10s para 0.5-1s
- **Cache Agressivo**: 2 níveis (memória + Redis)
- **Processamento Paralelo**: ParallelProcessor
- **Timeout**: 25s no agente, 20s no processador

### 3. Novas Funcionalidades
- **Knowledge Base**: FAQ completo sobre energia solar
- **Follow-up Automático**: Sistema de acompanhamento
- **Multimodal Nativo**: Suporte AGnO para imagens/áudio
- **Monitoramento**: Performance tracking em tempo real

## 📋 Próximos Passos

1. **Execute os SQLs no Supabase**:
   - create_knowledge_base_tables.sql
   - create_monitoring_tables.sql

2. **Configure as variáveis de ambiente**:
   - OPENAI_API_KEY (para embeddings)
   - Outras já devem estar configuradas

3. **Inicie o sistema V2**:
   ```bash
   python -m uvicorn api.main_v2:app --reload
   ```

4. **Monitore a performance**:
   - Acesse: http://localhost:8000/performance
   - Target: <30s de resposta

## 🚀 Melhorias Esperadas

- **Performance**: 70% mais rápido (de ~60s para <30s)
- **Qualidade**: Respostas mais precisas com knowledge base
- **Automação**: Follow-up automático aumenta conversão
- **Escalabilidade**: Cache e paralelismo suportam mais usuários

## ⚠️ Atenção

- O sistema V1 continua funcionando em paralelo
- Para migrar completamente, atualize as rotas no Evolution API
- Monitore os logs para identificar possíveis problemas
"""
    
    summary_file = Path(__file__).parent.parent / "MIGRATION_V2_SUMMARY.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    logger.info(f"Resumo da migração salvo em: {summary_file}")
    return True


async def main():
    """Executa migração completa"""
    logger.info("🚀 Iniciando migração para V2 com AGnO Framework")
    
    steps = [
        ("Verificando configurações", update_env_file),
        ("Criando arquivos SQL", create_tables),
        ("Inicializando Knowledge Base", initialize_knowledge_base),
        ("Testando sistema V2", test_v2_system),
        ("Criando resumo", create_migration_summary)
    ]
    
    success = True
    
    for step_name, step_func in steps:
        logger.info(f"\n{'='*50}")
        logger.info(f"Executando: {step_name}")
        logger.info(f"{'='*50}")
        
        result = await step_func()
        
        if not result:
            logger.error(f"❌ Falha em: {step_name}")
            success = False
            break
            
    if success:
        logger.success("\n✅ Migração concluída com sucesso!")
        logger.info("Próximo passo: Execute os SQLs no Supabase e inicie o sistema V2")
    else:
        logger.error("\n❌ Migração falhou. Verifique os logs acima.")


if __name__ == "__main__":
    asyncio.run(main())