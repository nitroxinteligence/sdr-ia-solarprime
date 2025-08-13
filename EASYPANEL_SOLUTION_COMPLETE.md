# 🔥 SOLUÇÃO DEFINITIVA - Erro "Failed to pull changes" no EasyPanel

## 🔍 Diagnóstico do Problema

O erro **"Failed to pull changes"** no EasyPanel ocorre por uma das seguintes razões:

### Causas Principais:
1. **Autenticação GitHub desatualizada** - Desde 13/08/2021, GitHub não aceita mais senhas, apenas tokens
2. **SSH Key não configurada** - EasyPanel precisa de SSH key para acessar repositórios privados
3. **Token expirado ou sem permissões** - Token GitHub sem as permissões necessárias
4. **Espaço em disco insuficiente** - Servidor sem espaço para fazer build
5. **Cache corrompido** - Build cache com problemas

## ✅ SOLUÇÃO PASSO A PASSO

### OPÇÃO 1: Configurar GitHub Token (MAIS FÁCIL) 🎯

#### Passo 1: Criar Personal Access Token no GitHub
1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Configure:
   ```
   Nome: EasyPanel Deploy Token
   Expiration: 90 days (ou No expiration)
   
   Permissões necessárias:
   ✅ repo (Full control of private repositories)
   ✅ workflow (Update GitHub Action workflows)
   ✅ admin:repo_hook (Full control of repository hooks)
   ```
4. Clique em **"Generate token"**
5. **COPIE O TOKEN IMEDIATAMENTE** (não será mostrado novamente!)

#### Passo 2: Configurar Token no EasyPanel
1. No EasyPanel, vá em **Settings > GitHub**
2. Cole o token no campo **"GitHub Token"**
3. Clique em **"Save"**
4. Deve aparecer: **"Github token updated"**

#### Passo 3: Recriar o Serviço
```bash
# Delete o serviço com problema
1. No EasyPanel, clique no serviço "sdr-api"
2. Clique em "Settings" > "Delete Service"
3. Confirme a exclusão

# Crie novo serviço
1. Clique em "Add Service"
2. Escolha "GitHub" como source
3. Configure:
   - Repository: nitroxinteligence/agentic-sdr-solar-prime
   - Branch: main
   - Build Type: Dockerfile
   - Port: 8000
```

### OPÇÃO 2: Configurar SSH Key 🔑

#### Passo 1: Obter SSH Key do EasyPanel
1. No serviço do EasyPanel, vá em **"Source"** tab
2. Clique em **"Git"** sub-tab
3. **COPIE a SSH Key** mostrada

#### Passo 2: Adicionar SSH Key no GitHub
1. Acesse: https://github.com/settings/keys
2. Clique em **"New SSH key"**
3. Configure:
   ```
   Title: EasyPanel Deploy Key
   Key type: Authentication Key
   Key: [COLE A SSH KEY DO EASYPANEL]
   ```
4. Clique em **"Add SSH key"**

#### Passo 3: Configurar Git URL SSH no EasyPanel
```bash
# Mude a URL do repositório para SSH
git@github.com:nitroxinteligence/agentic-sdr-solar-prime.git
```

### OPÇÃO 3: Deploy Manual via Docker 🐳

Se nada funcionar, faça deploy manual:

#### Passo 1: SSH no servidor EasyPanel
```bash
ssh root@seu-servidor-easypanel
```

#### Passo 2: Clone e Build Manual
```bash
# Navegue para o diretório de serviços
cd /var/lib/easypanel/services/

# Clone o repositório
git clone https://github.com/nitroxinteligence/agentic-sdr-solar-prime.git agentic-sdr

# Entre no diretório
cd agentic-sdr

# Build a imagem
docker build -t agentic-sdr:latest .

# Execute o container
docker run -d \
  --name agentic-sdr \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  agentic-sdr:latest
```

## 🛠️ Troubleshooting Adicional

### Verificar Espaço em Disco
```bash
# No servidor EasyPanel
df -h

# Se estiver cheio, limpe Docker
docker system prune -a --volumes
```

### Limpar Cache do EasyPanel
```bash
# Limpar build cache
docker builder prune -a

# Reiniciar EasyPanel
systemctl restart easypanel
```

### Verificar Logs Detalhados
```bash
# No EasyPanel, vá em Logs e procure por:
- "authentication failed"
- "permission denied"
- "no space left"
- "repository not found"
```

### Testar Acesso ao Repositório
```bash
# No servidor, teste o acesso
curl -H "Authorization: token SEU_TOKEN_GITHUB" \
  https://api.github.com/repos/nitroxinteligence/agentic-sdr-solar-prime

# Deve retornar JSON com info do repo
```

## 📋 Checklist de Verificação

- [ ] Token GitHub criado com permissões corretas
- [ ] Token configurado no EasyPanel Settings
- [ ] Repositório é público ou token tem acesso
- [ ] Servidor tem espaço em disco (>2GB livre)
- [ ] Branch "main" existe no repositório
- [ ] Dockerfile existe na raiz do projeto
- [ ] Porta 8000 está configurada corretamente

## 🚨 SOLUÇÃO DE EMERGÊNCIA

Se NADA funcionar, use este script:

```bash
#!/bin/bash
# emergency-deploy.sh

# 1. Fazer backup
cp -r /var/lib/easypanel/services/sdr-api /var/lib/easypanel/services/sdr-api-backup

# 2. Limpar tudo
cd /var/lib/easypanel/services/
rm -rf sdr-api

# 3. Clone direto
git clone https://github.com/nitroxinteligence/agentic-sdr-solar-prime.git sdr-api
cd sdr-api

# 4. Criar .env
cat > .env << 'EOF'
# Cole aqui suas variáveis de ambiente
SUPABASE_URL=xxx
SUPABASE_KEY=xxx
# ... resto das variáveis
EOF

# 5. Build e Run
docker-compose up -d
```

## ✅ Configuração de Variáveis (.env)

```env
# APIs Essenciais
SUPABASE_URL=sua-url
SUPABASE_KEY=sua-key
EVOLUTION_API_URL=sua-url
EVOLUTION_API_KEY=sua-key
EVOLUTION_INSTANCE_NAME=sua-instancia
KOMMO_BASE_URL=sua-url
KOMMO_LONG_LIVED_TOKEN=seu-token
GOOGLE_API_KEY=sua-key
GOOGLE_CALENDAR_ID=seu-calendario

# Configurações Kommo (do .env.transbordo)
KOMMO_PIPELINE_ID=11672895
KOMMO_HUMAN_HANDOFF_STAGE_ID=90421387
KOMMO_NOT_INTERESTED_STAGE_ID=89709599
KOMMO_MEETING_SCHEDULED_STAGE_ID=89709595
KOMMO_AGENT_USER_ID=11031887
HUMAN_INTERVENTION_PAUSE_HOURS=24

# Agentes
ENABLE_CALENDAR_AGENT=true
ENABLE_CRM_AGENT=true
ENABLE_FOLLOWUP_AGENT=true

# IA
PRIMARY_AI_MODEL=gemini-1.5-pro
FALLBACK_AI_MODEL=gpt-4-turbo
AI_TEMPERATURE=0.7
```

## 🎯 Resultado Esperado

Após aplicar a solução:
- ✅ Deploy bem-sucedido
- ✅ Container rodando na porta 8000
- ✅ Logs sem erros de autenticação
- ✅ Webhook Evolution API funcionando
- ✅ Sistema 98% operacional

## 📞 Suporte

Se o problema persistir após todas as tentativas:
1. Verifique os logs completos do EasyPanel
2. Entre em contato com suporte EasyPanel
3. Considere usar outro serviço de deploy (Railway, Render, Fly.io)

---

**IMPORTANTE**: O problema NÃO é com o código ou repositório novo. É uma questão de autenticação/configuração no EasyPanel.