# 🔌 Guia: Como Obter a Connection String do Supabase

Este guia mostra passo a passo como encontrar sua connection string do Supabase para usar com PgVector.

## 📍 Onde Encontrar a Connection String

### Passo 1: Acesse o Dashboard do Supabase
1. Faça login em: https://app.supabase.com
2. Selecione seu projeto "SDR IA SolarPrime" (ou o nome do seu projeto)

### Passo 2: Navegue até as Configurações do Banco
Existem duas formas de chegar lá:

**Método 1 - Botão Connect (Mais Rápido):**
- No topo da página do projeto, clique no botão **"Connect"**

**Método 2 - Via Menu:**
1. No menu lateral, clique em **"Settings"** (ícone de engrenagem)
2. Depois clique em **"Database"**
3. Por fim, clique em **"Connection string"**

### Passo 3: Escolha o Tipo de Connection String

Você verá diferentes opções de conexão:

1. **URI** (Recomendado para AGnO/PgVector):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

2. **Connection pooling** (Para alta concorrência):
   - **Transaction mode**: Para queries únicas
   - **Session mode**: Para conexões persistentes

### Passo 4: Copie a Connection String Correta

Para o AGnO Framework com PgVector, use a **URI direta (Direct connection)**.

⚠️ **IMPORTANTE**: A connection string já vem com um placeholder `[YOUR-PASSWORD]`. Você precisa substituir isso pela senha real do seu banco de dados.

## 🔐 Onde Encontrar a Senha do Banco

Se você não lembra a senha do banco de dados:

1. Vá em **Settings** → **Database**
2. Na seção **Database password**, você pode:
   - Ver a senha atual (se você salvou)
   - Resetar a senha clicando em **"Reset database password"**

## 📝 Exemplo de Connection String Completa

```
postgresql://postgres:SuaSenhaAqui123@db.rcjcpwqezmlhenmhrski.supabase.co:5432/postgres
```

## 🔧 Configurando no Projeto

Após obter a connection string, adicione no seu `.env`:

```env
# Connection string para PgVector/AGnO
SUPABASE_DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Suas outras configurações existentes
SUPABASE_URL=https://rcjcpwqezmlhenmhrski.supabase.co
SUPABASE_ANON_KEY=eyJ...
```

## ✅ Verificando se PgVector está Habilitado

1. No Supabase Dashboard, vá em **Database** → **Extensions**
2. Procure por **"vector"**
3. Se não estiver habilitado, clique em **"Enable"**

## 🚨 Troubleshooting

### Connection String não Aparece?
- Certifique-se de estar logado no projeto correto
- Tente usar um navegador diferente ou modo incógnito
- Limpe o cache do navegador

### Erro de Conexão?
- Verifique se substituiu `[YOUR-PASSWORD]` pela senha real
- Confirme que o PgVector está habilitado
- Teste a conexão usando `psql` ou outro cliente PostgreSQL

### IPv6 vs IPv4
- A conexão direta do Supabase usa IPv6 por padrão
- Se precisar IPv4, use o connection pooler

## 🎯 Próximos Passos

1. Copie a connection string do seu dashboard
2. Substitua a senha
3. Adicione ao `.env` como `SUPABASE_DATABASE_URL`
4. Teste a conexão executando o script de setup do banco

---

💡 **Dica**: Guarde a connection string em um gerenciador de senhas seguro!