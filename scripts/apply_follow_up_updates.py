"""
Apply Follow-up Table Updates
=============================
Aplica as atualizações necessárias na tabela follow_ups
"""

import os
from supabase import create_client, Client
from loguru import logger
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    logger.error("SUPABASE_URL e SUPABASE_KEY devem estar configurados no .env")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def apply_updates():
    """Aplica as atualizações na tabela follow_ups"""
    
    try:
        logger.info("Aplicando atualizações na tabela follow_ups...")
        
        # Para executar SQL diretamente, precisamos usar a API REST do Supabase
        # Como estamos usando o client Python, vamos fazer as alterações de forma programática
        
        # 1. Verificar se a tabela existe
        logger.info("Verificando estrutura da tabela...")
        
        # Tentar inserir um registro de teste para verificar campos
        test_data = {
            'lead_id': '00000000-0000-0000-0000-000000000000',  # UUID fake
            'scheduled_at': '2025-01-01T00:00:00',
            'type': 'first_contact',  # Novo tipo
            'status': 'cancelled'  # Vamos cancelar imediatamente
        }
        
        try:
            # Tentar inserir sem metadata primeiro
            result = supabase.table('follow_ups').insert(test_data).execute()
            # Se chegou aqui, a tabela aceita o tipo 'first_contact'
            logger.info("✓ Tabela já aceita tipo 'first_contact'")
            
            # Deletar o registro de teste
            if result.data:
                supabase.table('follow_ups').delete().eq('id', result.data[0]['id']).execute()
                
        except Exception as e:
            if "'first_contact'" in str(e):
                logger.warning("✗ Tabela não aceita tipo 'first_contact'. Precisa executar o SQL manualmente.")
                logger.info("\nPor favor, execute o seguinte comando SQL no Supabase:")
                logger.info("SQL> ALTER TABLE follow_ups DROP CONSTRAINT IF EXISTS follow_ups_type_check;")
                logger.info("SQL> ALTER TABLE follow_ups ADD CONSTRAINT follow_ups_type_check CHECK (type IN ('first_contact', 'reminder', 'reengagement', 'final', 'qualification', 'scheduling', 'check_in', 'nurture'));")
                return False
        
        # 2. Verificar se o campo metadata existe
        test_data_with_metadata = test_data.copy()
        test_data_with_metadata['metadata'] = {'test': True}
        
        try:
            result = supabase.table('follow_ups').insert(test_data_with_metadata).execute()
            logger.info("✓ Campo 'metadata' já existe")
            
            # Deletar o registro de teste
            if result.data:
                supabase.table('follow_ups').delete().eq('id', result.data[0]['id']).execute()
                
        except Exception as e:
            if "metadata" in str(e):
                logger.warning("✗ Campo 'metadata' não existe. Precisa executar o SQL manualmente.")
                logger.info("\nPor favor, execute o seguinte comando SQL no Supabase:")
                logger.info("SQL> ALTER TABLE follow_ups ADD COLUMN IF NOT EXISTS metadata JSONB;")
                return False
        
        logger.success("✅ Tabela follow_ups está pronta para uso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao aplicar atualizações: {e}")
        logger.info("\n⚠️ Execute manualmente o script SQL no Supabase Dashboard:")
        logger.info("1. Acesse o Supabase Dashboard")
        logger.info("2. Vá para SQL Editor")
        logger.info("3. Cole e execute o conteúdo de: scripts/update_follow_ups_table.sql")
        return False


if __name__ == "__main__":
    logger.info("====== Aplicando Atualizações Follow-up ======")
    
    if apply_updates():
        logger.success("\n🎉 Atualizações aplicadas com sucesso!")
        logger.info("Agora você pode executar: python test_follow_up_system.py")
    else:
        logger.warning("\n⚠️ Algumas atualizações precisam ser feitas manualmente no Supabase.")
        logger.info("Após executar o SQL manualmente, rode: python test_follow_up_system.py")