# 📝 Como Executar o SQL no Supabase Dashboard

Como a conexão direta ao PostgreSQL está sendo recusada, siga estes passos para executar o SQL diretamente no Supabase Dashboard:

## 🚀 Passo a Passo

### 1. Acesse o SQL Editor do Supabase
1. Faça login em: https://app.supabase.com
2. Selecione seu projeto
3. No menu lateral, clique em **"SQL Editor"** (ícone de código)

### 2. Crie uma Nova Query
1. Clique no botão **"New query"** (ou **"Nova consulta"**)
2. Uma nova aba será aberta com um editor SQL vazio

### 3. Cole o Script SQL
1. Abra o arquivo: `scripts/supabase_complete_setup.sql`
2. Copie TODO o conteúdo do arquivo
3. Cole no editor SQL do Supabase

### 4. Execute o Script
1. Clique no botão **"Run"** (ou **"Executar"**) - geralmente é um botão verde
2. Aguarde a execução (pode levar alguns segundos)
3. Verifique se aparece a mensagem de sucesso

### 5. Verifique as Tabelas Criadas
1. No menu lateral, vá em **"Table Editor"**
2. Você deve ver as seguintes tabelas:
   - `knowledge_base`
   - `agent_sessions`
   - `embeddings`
   - `profiles`
   - `conversations`
   - `messages`
   - `leads`
   - `follow_ups`
   - `tasks`
   - `reports`
   - `analytics_events`

## ⚠️ Possíveis Erros e Soluções

### Erro: "relation already exists"
- **Significado**: A tabela já existe
- **Solução**: Ignorar - o script usa `IF NOT EXISTS`

### Erro: "extension not found"
- **Significado**: Extensão não disponível
- **Solução**: 
  1. Vá em Database → Extensions
  2. Habilite a extensão `vector`
  3. Execute o script novamente

### Erro: "permission denied"
- **Significado**: Sem permissão
- **Solução**: Certifique-se de estar usando um projeto com permissões adequadas

## 📊 Depois de Executar

### Inserir Dados Iniciais
1. Ainda no SQL Editor, crie uma nova query
2. Cole o conteúdo da seção "INSERIR DADOS INICIAIS" do script
3. Execute para popular a base de conhecimento

### Verificar se Funcionou
Execute esta query de teste:
```sql
SELECT COUNT(*) as total FROM knowledge_base;
```

Deve retornar pelo menos 19 registros.

## 🔧 Alternativa: Usar o Supabase CLI

Se preferir usar a linha de comando:

```bash
# Instalar Supabase CLI
brew install supabase/tap/supabase

# Login
supabase login

# Executar SQL
supabase db push --db-url "postgresql://postgres:85Gfts34Lp4ss@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres"
```

---

💡 **Dica**: Salve o script SQL no próprio Supabase clicando em "Save query" para reutilizar no futuro!