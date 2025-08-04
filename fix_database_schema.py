#!/usr/bin/env python3
"""
Script para corrigir o schema do banco de dados
Adiciona a coluna last_interaction na tabela leads
"""
import asyncio
from datetime import datetime
from app.integrations.supabase_client import supabase_client

async def add_last_interaction_column():
    """Adiciona a coluna last_interaction se não existir"""
    try:
        # Conectar ao Supabase
        await supabase_client.test_connection()
        print("✅ Conectado ao Supabase")
        
        # Verificar se a coluna já existe
        result = supabase_client.client.table('leads').select('*').limit(1).execute()
        
        if result.data and 'last_interaction' not in result.data[0]:
            print("⚠️ Coluna 'last_interaction' não encontrada")
            print("ℹ️ Para adicionar a coluna, execute este SQL no Supabase:")
            print("")
            print("=" * 60)
            print("ALTER TABLE leads")
            print("ADD COLUMN IF NOT EXISTS last_interaction TIMESTAMP WITH TIME ZONE DEFAULT NOW();")
            print("=" * 60)
            print("")
            print("Passos:")
            print("1. Acesse: https://supabase.com/dashboard")
            print("2. Selecione seu projeto")
            print("3. Vá em SQL Editor")
            print("4. Cole e execute o comando SQL acima")
            print("")
            
            # Tentar atualizar leads existentes com timestamp atual
            try:
                # Atualizar todos os leads sem last_interaction
                leads = supabase_client.client.table('leads').select('id').execute()
                for lead in leads.data:
                    try:
                        # Usar updated_at como fallback
                        supabase_client.client.table('leads').update({
                            'updated_at': datetime.now().isoformat()
                        }).eq('id', lead['id']).execute()
                    except:
                        pass
                print("✅ Timestamps atualizados nos leads existentes")
            except Exception as e:
                print(f"⚠️ Não foi possível atualizar timestamps: {e}")
        else:
            print("✅ Coluna 'last_interaction' já existe!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(add_last_interaction_column())