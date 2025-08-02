# Configuração Supabase para Produção - SDR IA SolarPrime V2

## 1. Pré-requisitos

### 1.1 Extensões PostgreSQL
Execute no Supabase SQL Editor:

```sql
-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
```

### 1.2 Verificar Extensões
```sql
SELECT * FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector');
```

## 2. Executar Scripts SQL

### 2.1 Criar Estrutura Principal
Execute o conteúdo completo de `/scripts/create_knowledge_base_tables.sql`:

1. Acesse: https://supabase.com/dashboard/project/rcjcpwqezmlhenmhrski/sql/new
2. Cole todo o conteúdo do arquivo SQL
3. Execute (F5 ou botão "Run")

### 2.2 Criar Tabelas de Monitoramento (Opcional)
Execute o conteúdo de `/scripts/create_monitoring_tables.sql` se quiser monitoramento de performance.

## 3. Configuração de Conexão

### 3.1 URLs de Conexão
O sistema está configurado para usar o pooler do Supabase na região São Paulo:

```
Host: aws-0-sa-east-1.pooler.supabase.com
Port: 6543
Database: postgres
User: postgres.rcjcpwqezmlhenmhrski
Password: [SUPABASE_SERVICE_KEY]
```

### 3.2 Pooler vs Conexão Direta
- **Pooler (6543)**: Recomendado para aplicações, gerencia conexões automaticamente
- **Direto (5432)**: Apenas para ferramentas administrativas

## 4. Configuração do PgVector

### 4.1 Tabela de Embeddings
O AGnO criará automaticamente a tabela `embeddings`, mas já pré-criamos no SQL com:
- Coluna `embedding` tipo `vector(1536)` para OpenAI embeddings
- Índice IVFFlat para busca eficiente
- Função `match_documents` para busca por similaridade

### 4.2 Performance
Para melhor performance com muitos documentos:

```sql
-- Ajustar parâmetros do índice IVFFlat
ALTER INDEX embeddings_embedding_idx SET (lists = 1000);

-- Vacuum e analyze após inserções em massa
VACUUM ANALYZE embeddings;
```

## 5. Segurança

### 5.1 Row Level Security (RLS)
O script já configura RLS apropriadamente:
- `knowledge_base`: Leitura pública, escrita apenas service role
- `agent_sessions`: Acesso total apenas service role
- `embeddings`: Será gerenciada pelo AGnO

### 5.2 API Keys
- **ANON_KEY**: Para operações públicas (leitura)
- **SERVICE_KEY**: Para operações administrativas (escrita)

## 6. Troubleshooting

### 6.1 Erro de Conexão Timeout
Se encontrar timeout ao conectar:
1. Verifique se está usando a URL do pooler (porta 6543)
2. Confirme que o SERVICE_KEY está correto
3. Verifique limites de conexão no dashboard

### 6.2 Erro "vector type does not exist"
Execute novamente:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6.3 Erro na Busca Vetorial
Verifique se a função `match_documents` foi criada:
```sql
SELECT proname FROM pg_proc WHERE proname = 'match_documents';
```

## 7. Dados Iniciais

Os dados da knowledge_base já foram inseridos pelo script SQL. Para verificar:

```sql
SELECT COUNT(*) FROM knowledge_base;
-- Deve retornar 19 registros

SELECT category, COUNT(*) 
FROM knowledge_base 
GROUP BY category;
-- Mostra distribuição por categoria
```

## 8. Monitoramento

### 8.1 Queries Úteis
```sql
-- Ver últimas sessões do agente
SELECT * FROM agent_sessions 
ORDER BY updated_at DESC 
LIMIT 10;

-- Estatísticas de uso da knowledge base
SELECT 
    category,
    COUNT(*) as total,
    MAX(updated_at) as last_update
FROM knowledge_base
GROUP BY category;

-- Tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename IN ('knowledge_base', 'agent_sessions', 'embeddings')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 9. Backup e Manutenção

### 9.1 Backup Automático
Supabase faz backup automático diário. Para backup manual:

```bash
# Via Supabase CLI
supabase db dump -f backup.sql

# Ou pg_dump direto
pg_dump postgresql://postgres.[PROJECT-REF]:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres > backup.sql
```

### 9.2 Manutenção Regular
```sql
-- Executar semanalmente
VACUUM ANALYZE knowledge_base;
VACUUM ANALYZE embeddings;
VACUUM ANALYZE agent_sessions;

-- Reindexar mensalmente se houver muitas mudanças
REINDEX TABLE embeddings;
```

## 10. Próximos Passos

1. ✅ Execute os SQLs no Supabase
2. ✅ Verifique as extensões habilitadas
3. ✅ Confirme que as tabelas foram criadas
4. ⚠️ Configure uma API Key válida do OpenAI no .env
5. 🚀 Execute o sistema V2

### Comando para Testar:
```bash
python scripts/migrate_to_v2.py
```

Se tudo estiver correto, você verá:
- ✅ Base de conhecimento carregada com sucesso!
- Exemplo de busca mostrando resultados

### Para Iniciar o Sistema:
```bash
python -m uvicorn api.main_v2:app --reload
```