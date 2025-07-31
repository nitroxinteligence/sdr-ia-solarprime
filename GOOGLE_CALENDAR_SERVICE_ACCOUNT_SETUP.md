# 🚀 Google Calendar com Service Account - Guia Definitivo 2025

## Por que Service Account?

Service Account é a **melhor solução** para servidores em produção porque:
- ✅ **Sem navegador necessário** - funciona em servidores headless
- ✅ **Sem interação humana** - autenticação 100% automatizada
- ✅ **Sem expiração** - não precisa renovar tokens
- ✅ **Mais seguro** - usa chaves criptografadas
- ✅ **Mais simples** - configuração única

## Passo a Passo Completo

### 1. Criar Service Account no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Selecione ou crie um projeto
3. Vá em **IAM & Admin** > **Service Accounts**
4. Clique em **CREATE SERVICE ACCOUNT**
5. Preencha:
   - Service account name: `sdr-calendar-service`
   - Service account ID: será gerado automaticamente
   - Description: `Service Account para SDR Calendar Integration`
6. Clique em **CREATE AND CONTINUE**
7. Em **Grant this service account access**, pule (clique em **CONTINUE**)
8. Em **Grant users access**, pule (clique em **DONE**)

### 2. Criar e Baixar a Chave JSON

1. Na lista de Service Accounts, clique no que você criou
2. Vá na aba **KEYS**
3. Clique em **ADD KEY** > **Create new key**
4. Escolha **JSON** e clique em **CREATE**
5. O arquivo será baixado automaticamente

### 3. Habilitar Google Calendar API

1. No Google Cloud Console, vá em **APIs & Services** > **Library**
2. Pesquise por "Google Calendar API"
3. Clique e depois em **ENABLE**

### 4. Compartilhar Calendário com Service Account

**IMPORTANTE**: Service accounts não têm calendários próprios!

1. Abra o Google Calendar (do usuário que terá os eventos)
2. Vá em **Configurações** ⚙️
3. Na barra lateral, encontre o calendário desejado
4. Clique em **Compartilhar com pessoas específicas**
5. Clique em **Adicionar pessoas**
6. Cole o email do service account (está no arquivo JSON como `client_email`)
   - Exemplo: `sdr-calendar-service@seu-projeto.iam.gserviceaccount.com`
7. Defina a permissão: **Fazer alterações em eventos**
8. Clique em **Enviar**

### 5. Configurar Variáveis de Ambiente

Abra o arquivo JSON baixado e extraia as informações:

```bash
# Configuração do Service Account
GOOGLE_USE_SERVICE_ACCOUNT=true
GOOGLE_SERVICE_ACCOUNT_EMAIL=sdr-calendar@projeto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_PROJECT_ID=seu-projeto-id
GOOGLE_PRIVATE_KEY_ID=chave-id-aqui
GOOGLE_CLIENT_ID=123456789

# ID do calendário (use o email do usuário ou ID específico)
GOOGLE_CALENDAR_ID=usuario@suaempresa.com.br

# Opcional - apenas para Google Workspace
# GOOGLE_CALENDAR_OWNER_EMAIL=admin@suaempresa.com.br

# Para desabilitar temporariamente
DISABLE_GOOGLE_CALENDAR=false
```

### 6. Como Extrair Valores do JSON

O arquivo JSON baixado tem esta estrutura:

```json
{
  "type": "service_account",
  "project_id": "SEU_PROJECT_ID",
  "private_key_id": "SEU_PRIVATE_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "SERVICE_ACCOUNT_EMAIL",
  "client_id": "CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "URL_DO_CERTIFICADO"
}
```

**IMPORTANTE sobre GOOGLE_PRIVATE_KEY**:
- Copie exatamente como está, incluindo `\n`
- No arquivo .env, coloque entre aspas
- O sistema converterá `\n` em quebras de linha automaticamente

## Funcionamento Automático

Com as variáveis configuradas, o sistema:

1. Detecta que está em produção
2. Cria automaticamente o arquivo JSON do service account
3. Autentica usando o service account
4. Conecta ao calendário configurado
5. Pronto! Sem necessidade de navegador ou interação

## Troubleshooting

### Erro: "Calendar not found"
- Verifique se compartilhou o calendário com o email do service account
- Use o email do usuário como GOOGLE_CALENDAR_ID

### Erro: "Insufficient permissions"
- Verifique se deu permissão "Fazer alterações em eventos" ao compartilhar

### Erro: "Invalid private key"
- Verifique se copiou a chave privada completa, incluindo BEGIN/END
- Certifique-se que está entre aspas no .env

### Para Google Workspace
Se sua empresa usa Google Workspace e precisa acessar calendários de múltiplos usuários:

1. Configure Domain-Wide Delegation no admin console
2. Use `GOOGLE_CALENDAR_OWNER_EMAIL` para impersonar usuários

## Migração do OAuth para Service Account

Se você estava usando OAuth antes:

1. Adicione as novas variáveis de ambiente
2. Defina `GOOGLE_USE_SERVICE_ACCOUNT=true`
3. O sistema migrará automaticamente
4. Pode deletar os arquivos antigos de token

## Vantagens em Produção

- **Zero manutenção**: Configure uma vez e esqueça
- **Alta disponibilidade**: Sem tokens expirando
- **Segurança**: Chaves criptografadas, sem senhas de usuário
- **Performance**: Autenticação mais rápida
- **Escalabilidade**: Funciona com múltiplos calendários

## Exemplo de Uso

```python
# O sistema detecta automaticamente e usa service account
calendar_service = GoogleCalendarService(config)

# Criar evento funciona normalmente
event = await calendar_service.create_event(
    title="Reunião com Cliente",
    start_datetime=datetime.now() + timedelta(days=1),
    description="Discussão sobre proposta solar"
)
```

## Próximos Passos

1. Configure as variáveis de ambiente no EasyPanel
2. Faça o deploy
3. O sistema criará tudo automaticamente
4. Pronto! Google Calendar funcionando em produção 🎉