# ⚠️ GUIA URGENTE DE CONFIGURAÇÃO - SDR IA SolarPrime V2

## ❌ PROBLEMAS IDENTIFICADOS

1. **Conexão Supabase Falhando**: "Tenant or user not found"
2. **OpenAI API sem créditos**: "insufficient_quota"

## 🚨 AÇÕES NECESSÁRIAS IMEDIATAS

### 1. Corrigir Conexão Supabase

#### Opção A: Obter Connection String Correta (RECOMENDADO)

1. Acesse: https://supabase.com/dashboard/project/rcjcpwqezmlhenmhrski
2. Vá em **Settings** > **Database**
3. Em **Connection string**, selecione:
   - **Connection pooling** ✅
   - **Mode**: Transaction
4. Copie a connection string completa
5. A string deve ser similar a:
   ```
   postgres://postgres.rcjcpwqezmlhenmhrski:[YOUR-PASSWORD]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
   ```
6. Extraia a senha/service key da connection string e atualize no `.env`:
   ```
   SUPABASE_SERVICE_KEY=[YOUR-PASSWORD]
   ```

#### Opção B: Verificar Região do Projeto

Se o erro persistir, o projeto pode estar em outra região:

1. No Dashboard do Supabase, verifique a região em **Settings** > **General**
2. Se não for `South America (São Paulo)`, a URL do pooler será diferente:
   - US East: `aws-0-us-east-1.pooler.supabase.com`
   - EU Central: `aws-0-eu-central-1.pooler.supabase.com`
   - Etc.

### 2. Corrigir OpenAI API

A API key atual está sem créditos. Você precisa:

1. Acesse: https://platform.openai.com/api-keys
2. Crie uma nova API key ou adicione créditos
3. Atualize no `.env`:
   ```
   OPENAI_API_KEY=sk-proj-...sua-nova-key-aqui...
   ```

### 3. Solução Temporária (Sem OpenAI)

Se não tiver OpenAI disponível, posso criar um fallback usando apenas Gemini:

```bash
# Execute este comando para usar modo fallback
python scripts/migrate_to_v2.py --no-embeddings
```

## 📋 CHECKLIST DE CONFIGURAÇÃO

- [ ] Obter connection string correta do Supabase
- [ ] Atualizar SUPABASE_SERVICE_KEY no .env
- [ ] Verificar região do projeto Supabase
- [ ] Obter nova API key do OpenAI com créditos
- [ ] Atualizar OPENAI_API_KEY no .env
- [ ] Executar SQL no Supabase (create_knowledge_base_tables.sql)

## 🔧 TESTE RÁPIDO

Após atualizar as configurações:

```bash
# Testar conexão
python scripts/test_supabase_connection.py

# Se funcionar, executar migração
python scripts/migrate_to_v2.py
```

## 💡 ALTERNATIVAS

### Usar Supabase Client ao invés de Connection Direct

Se a connection string continuar falhando, posso refatorar para usar o cliente Supabase Python ao invés de conexão direta PostgreSQL. Isso seria mais simples e confiável.

### Usar Gemini Embeddings

Posso modificar o sistema para usar embeddings do Gemini ao invés do OpenAI, eliminando a dependência.

## 📞 PRÓXIMOS PASSOS

1. **Prioridade 1**: Obter connection string correta do Supabase Dashboard
2. **Prioridade 2**: Resolver OpenAI API ou implementar fallback
3. **Prioridade 3**: Executar testes completos

Me avise qual opção prefere seguir e posso implementar a solução!