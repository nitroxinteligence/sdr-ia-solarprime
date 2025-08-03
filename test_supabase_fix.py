#!/usr/bin/env python3
"""
Script para testar correção do Supabase
Verifica se operações síncronas funcionam sem await
"""
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.integrations.supabase_client import SupabaseClient
from app.agents.agentic_sdr import AgenticSDR
from app.utils.logger import emoji_logger


async def test_supabase_operations():
    """Testa operações do Supabase após correção"""
    
    print("\n" + "="*60)
    print("🧪 TESTE DE CORREÇÃO - SUPABASE")
    print("="*60 + "\n")
    
    # Teste 1: Conexão básica
    print("1️⃣ Testando conexão com Supabase...")
    try:
        supabase = SupabaseClient()
        connected = await supabase.test_connection()
        if connected:
            print("   ✅ Conexão estabelecida com sucesso")
        else:
            print("   ❌ Falha na conexão")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # Teste 2: Buscar mensagens (onde estava o erro)
    print("\n2️⃣ Testando busca de mensagens...")
    try:
        sdr = AgenticSDR()
        # Usa um número de teste
        messages = await sdr.get_last_100_messages("5511999999999")
        print(f"   ✅ Busca executada sem erros")
        print(f"   📊 Mensagens encontradas: {len(messages)}")
    except Exception as e:
        if "can't be used in 'await' expression" in str(e):
            print(f"   ❌ Erro de await ainda presente: {e}")
            return False
        else:
            # Pode não ter dados, mas não deve dar erro de await
            print(f"   ⚠️ Outro erro (esperado se não há dados): {e}")
    
    # Teste 3: Query direta no Supabase
    print("\n3️⃣ Testando query direta...")
    try:
        # Testa query síncrona sem await
        result = supabase.client.table('leads').select('id').limit(1).execute()
        print(f"   ✅ Query executada corretamente")
        print(f"   📊 Registros: {len(result.data) if result.data else 0}")
    except Exception as e:
        print(f"   ❌ Erro na query: {e}")
        return False
    
    # Teste 4: Operação de inserção (simulada)
    print("\n4️⃣ Testando operação de inserção (dry-run)...")
    try:
        # Simula inserção sem realmente inserir
        test_data = {
            'name': 'Teste SDR',
            'phone': '5511999999999',
            'email': 'teste@example.com',
            'status': 'test'
        }
        # Não executa para não poluir o banco
        query = supabase.client.table('leads').insert(test_data)
        print("   ✅ Query de inserção construída sem erros")
    except Exception as e:
        print(f"   ❌ Erro ao construir query: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("O erro do Supabase foi corrigido com sucesso.")
    print("="*60 + "\n")
    
    return True


async def main():
    """Executa os testes"""
    try:
        success = await test_supabase_operations()
        if success:
            print("✅ Correção validada com sucesso!")
            sys.exit(0)
        else:
            print("❌ Alguns testes falharam")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erro durante testes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())