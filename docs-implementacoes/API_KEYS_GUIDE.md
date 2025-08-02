# 📚 Guia de Obtenção das API Keys

Este documento explica como obter todas as API keys necessárias para o SDR IA SolarPrime.

## 🔑 Google Gemini 2.5 Pro

### Como obter:

1. **Acesse o Google AI Studio**
   - URL: https://makersuite.google.com/app/apikey
   - Faça login com sua conta Google

2. **Crie um novo projeto (se necessário)**
   - Clique em "Create Project"
   - Nome: "SDR SolarPrime"

3. **Gere a API Key**
   - Clique em "Create API Key"
   - Selecione o projeto criado
   - Copie a chave gerada

4. **Configure no .env**
   ```env
   GEMINI_API_KEY="sua_chave_aqui"
   ```

### Limites e Custos:
- **Free Tier**: 60 requisições por minuto
- **Paid**: Aumenta para 1000 requisições por minuto
- **Custo**: $0.0025 por 1K tokens (input) / $0.01 por 1K tokens (output)

---

## 🗄️ Supabase

### Como obter:

1. **Crie uma conta no Supabase**
   - URL: https://supabase.com
   - Use login com GitHub para facilitar

2. **Crie um novo projeto**
   - Nome: "sdr-solarprime"
   - Senha do banco: Anote em local seguro!
   - Região: São Paulo (sa-east-1)

3. **Obtenha as credenciais**
   - Vá em Settings → API
   - Copie:
     - Project URL
     - anon public key
     - service_role key (MANTER SEGURA!)

4. **Configure no .env**
   ```env
   SUPABASE_URL="https://xxxxx.supabase.co"
   SUPABASE_ANON_KEY="eyJhbGc..."
   SUPABASE_SERVICE_KEY="eyJhbGc..."
   ```

5. **Database URL**
   - Vá em Settings → Database
   - Copie a Connection String
   ```env
   SUPABASE_DB_URL="postgresql://postgres:[SUA-SENHA]@db.xxxxx.supabase.co:5432/postgres"
   ```

### Limites Free Tier:
- 500MB database
- 1GB file storage
- 2GB bandwidth
- 50,000 requisições por mês

---

## 📱 Evolution API

### Como obter:

1. **Instale a Evolution API**
   ```bash
   # Via Docker
   docker run -d \
     --name evolution \
     -p 8080:8080 \
     -e AUTHENTICATION_API_KEY=sua_chave_secreta \
     evolution-api/evolution-api:latest
   ```

2. **Configure a instância**
   - Acesse: http://localhost:8080
   - Crie uma nova instância
   - Nome: "solarprime"
   - Gere o token da instância

3. **Configure no .env**
   ```env
   EVOLUTION_API_URL="http://localhost:8080"
   EVOLUTION_API_KEY="sua_chave_de_autenticacao"
   EVOLUTION_INSTANCE_NAME="solarprime"
   EVOLUTION_INSTANCE_TOKEN="token_da_instancia"
   ```

4. **Conecte o WhatsApp**
   - Obtenha o QR Code via API ou interface
   - Escaneie com WhatsApp Business
   - Aguarde confirmação

### Notas:
- Use WhatsApp Business (não pessoal)
- Mantenha o celular sempre conectado
- Configure webhook para receber mensagens

---

## 💼 Kommo CRM

### Como obter:

1. **Crie conta no Kommo**
   - URL: https://www.kommo.com
   - Use plano com API habilitada

2. **Crie uma aplicação OAuth2**
   - Vá em: Configurações → Integrações → API
   - Clique em "Criar aplicação"
   - Preencha:
     - Nome: "SDR IA SolarPrime"
     - Redirect URI: `https://seu_dominio.com.br/auth/callback`
     - Tipo: Server-side application

3. **Obtenha as credenciais**
   ```env
   KOMMO_CLIENT_ID="seu_client_id"
   KOMMO_CLIENT_SECRET="seu_client_secret"
   KOMMO_SUBDOMAIN="sua_empresa"
   ```

4. **Configure o Pipeline**
   - Crie um pipeline "SolarPrime"
   - Anote o ID do pipeline
   - Configure os estágios conforme documentação

### Limites:
- API: 7 requisições por segundo
- Webhooks: Ilimitados
- Armazenamento: Conforme plano

---

## 🔐 Gerando Chaves Secretas

### Execute o script helper:

```bash
cd /home/solarprime/sdr-solarprime
python scripts/generate_secrets.py
```

Isso gerará:
- SECRET_KEY
- JWT_SECRET_KEY
- REDIS_PASSWORD
- KOMMO_WEBHOOK_TOKEN

### Copie e cole no .env:
```env
SECRET_KEY="chave_gerada_aqui"
JWT_SECRET_KEY="outra_chave_gerada"
REDIS_PASSWORD="senha_forte_gerada"
```

---

## 🚨 Segurança Importante

### ⚠️ NUNCA:
- Commitar o arquivo .env no Git
- Compartilhar API keys publicamente
- Usar as mesmas keys em dev/prod
- Deixar keys no código fonte

### ✅ SEMPRE:
- Use variáveis de ambiente
- Mantenha backups seguros das keys
- Rotacione keys periodicamente
- Use secrets managers em produção

---

## 📝 Checklist de Configuração

- [ ] Google Gemini API key obtida e testada
- [ ] Supabase projeto criado e credenciais copiadas
- [ ] Evolution API instalada e WhatsApp conectado
- [ ] Kommo CRM app OAuth2 configurada
- [ ] Redis senha forte gerada
- [ ] Chaves secretas (SECRET_KEY, JWT) geradas
- [ ] Arquivo .env preenchido completamente
- [ ] .env adicionado ao .gitignore
- [ ] Backup seguro das credenciais feito

---

## 🆘 Troubleshooting

### Gemini API não funciona:
- Verifique se a API está habilitada no Google Cloud Console
- Confirme os limites de quota
- Teste com: `curl -X POST "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=SUA_KEY"`

### Supabase connection refused:
- Verifique se o projeto está ativo
- Confirme a senha do PostgreSQL
- Teste a conexão com psql

### Evolution API não conecta WhatsApp:
- Verifique se o container está rodando
- Confirme que está usando WhatsApp Business
- Verifique logs: `docker logs evolution`

### Kommo OAuth erro:
- Confirme o redirect_uri está exato
- Verifique se o subdomínio está correto
- Teste primeiro no Postman

---

## 📞 Suporte

Se tiver problemas para obter alguma API key:

1. **Gemini**: https://cloud.google.com/support
2. **Supabase**: https://supabase.com/docs/support
3. **Evolution API**: https://github.com/EvolutionAPI/evolution-api
4. **Kommo**: https://www.kommo.com/support/

---

**💡 Dica**: Comece testando cada integração individualmente antes de integrar tudo!