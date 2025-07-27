# 🚀 Guia Completo: Webhook SDR IA + Evolution API no EasyPanel

Este guia detalha como configurar o webhook do SDR IA SolarPrime para funcionar com a Evolution API no EasyPanel da Hostinger.

## 📋 Pré-requisitos

- ✅ VPS Hostinger com EasyPanel instalado
- ✅ Evolution API v2 rodando no EasyPanel
- ✅ WhatsApp conectado na Evolution API
- ✅ Redis rodando no EasyPanel
- ✅ Acesso ao código do SDR IA SolarPrime

## 🔍 Passo 1: Descobrir o Nome da Instância

Primeiro, precisamos descobrir o nome exato da instância criada na Evolution API:

```bash
# 1. Configure as variáveis no .env local
cp .env.example .env

# 2. Edite o .env e adicione:
EVOLUTION_API_URL=https://evoapi-evolution-api.fzvgou.easypanel.host
EVOLUTION_API_KEY=sua-api-key-aqui

# 3. Execute o script para listar instâncias
python scripts/list_evolution_instances.py
```

**Anote o nome da instância** que aparecerá na lista (ex: "solarprime", "whatsapp-bot", etc).

## 🔧 Passo 2: Configurar Comunicação Interna

No EasyPanel, os serviços se comunicam internamente usando nomes de serviço, não URLs externas.

### Arquitetura de Comunicação:
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Evolution API  │────▶│   SDR IA Bot     │────▶│    Redis    │
│ evolution-api   │     │    sdr-ia        │     │   redis     │
│   Porta: 8080   │     │   Porta: 8000    │     │ Porta: 6379 │
└─────────────────┘     └──────────────────┘     └─────────────┘
         │                        │
         │   Webhook Request      │
         └────────────────────────┘
         http://sdr-ia:8000/webhook/whatsapp
```

## 📝 Passo 3: Configurar o Webhook

Execute o script de configuração:

```bash
python scripts/configure_webhook_easypanel.py
```

O script irá:
1. Perguntar o nome do serviço SDR IA no EasyPanel (padrão: `sdr-ia`)
2. Configurar o webhook para usar comunicação interna
3. Salvar as configurações no `.env.easypanel`

## 🐳 Passo 4: Preparar para Deploy

### 4.1. Verificar `.env.easypanel`

O arquivo deve conter:

```env
# Evolution API - Comunicação Interna
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=sua-api-key
EVOLUTION_INSTANCE_NAME=nome-correto-da-instancia

# Webhook - URL Interna
WEBHOOK_BASE_URL=http://sdr-ia:8000

# Redis - Comunicação Interna
REDIS_URL=redis://redis:6379/0

# Outras configurações necessárias
GEMINI_API_KEY=sua-gemini-key
SUPABASE_URL=sua-supabase-url
SUPABASE_KEY=sua-supabase-key
```

### 4.2. Verificar Dockerfile

O Dockerfile já está otimizado para EasyPanel com:
- Multi-stage build
- Usuário não-root
- Health check endpoint
- Porta 8000 exposta

## 🌐 Passo 5: Deploy no EasyPanel

### 5.1. Criar o Serviço

1. Acesse o EasyPanel
2. Clique em "Create Service"
3. Escolha "App"
4. Configure:
   - **Service Name**: `sdr-ia`
   - **Source**: GitHub (conecte seu repositório)
   - **Build**: Dockerfile
   - **Port**: 8000

### 5.2. Configurar Variáveis de Ambiente

No EasyPanel, adicione todas as variáveis do `.env.easypanel`:

1. Vá em "Environment"
2. Adicione cada variável uma por uma
3. **IMPORTANTE**: Não use aspas nos valores!

### 5.3. Configurar Rede

1. Em "Advanced", certifique-se que:
   - O serviço está na mesma rede que Evolution API e Redis
   - A porta 8000 **NÃO** está exposta externamente
   - Apenas comunicação interna está habilitada

### 5.4. Deploy

1. Clique em "Deploy"
2. Aguarde o build e inicialização
3. Verifique os logs para confirmar que iniciou corretamente

## 🧪 Passo 6: Testar a Integração

### 6.1. Teste Local (antes do deploy)

```bash
# Inicie a API localmente
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Em outro terminal, execute o teste
python scripts/test_easypanel_integration.py
```

### 6.2. Teste no EasyPanel (após deploy)

1. Verifique os logs do serviço `sdr-ia` no EasyPanel
2. Envie uma mensagem no WhatsApp conectado
3. Observe os logs para ver o processamento

## 🚨 Troubleshooting

### Problema: "Instância não encontrada"

**Solução**:
```bash
# 1. Liste as instâncias disponíveis
python scripts/list_evolution_instances.py

# 2. Atualize EVOLUTION_INSTANCE_NAME no .env.easypanel
# 3. Faça novo deploy
```

### Problema: "Webhook não recebe mensagens"

**Checklist**:
1. ✅ Evolution API está com status "open" (conectada)?
2. ✅ Webhook está configurado e ativo?
3. ✅ Serviços estão na mesma rede no EasyPanel?
4. ✅ Nome dos serviços estão corretos nas URLs internas?

**Debug**:
```bash
# Verificar configuração do webhook
curl -X GET https://evoapi.easypanel.host/webhook/find/sua-instancia \
  -H "apikey: sua-api-key"
```

### Problema: "Connection refused"

**Solução**:
- Use nomes de serviço, não `localhost`
- ❌ Errado: `http://localhost:8080`
- ✅ Correto: `http://evolution-api:8080`

### Verificar Conectividade Interna

No console do EasyPanel, execute no container `sdr-ia`:

```bash
# Testar Evolution API
curl http://evolution-api:8080/instance/fetchInstances -H "apikey: sua-key"

# Testar Redis
redis-cli -h redis ping
```

## 📊 Monitoramento

### Logs em Tempo Real

No EasyPanel:
1. Vá ao serviço `sdr-ia`
2. Clique em "Logs"
3. Ative "Follow logs"

### Métricas

Monitore:
- CPU e Memória do serviço
- Taxa de sucesso dos webhooks
- Tempo de resposta do agente IA

## ✅ Checklist Final

- [ ] Nome da instância correto no `.env.easypanel`
- [ ] URLs usando nomes de serviço internos
- [ ] Webhook configurado na Evolution API
- [ ] Serviços na mesma rede no EasyPanel
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado com sucesso
- [ ] Logs mostrando "Webhook endpoint ready"
- [ ] Teste de mensagem funcionando

## 🎉 Pronto!

Se todos os passos foram seguidos corretamente, seu SDR IA agora está:
- ✅ Recebendo mensagens do WhatsApp via webhook
- ✅ Processando com IA (Gemini)
- ✅ Respondendo automaticamente
- ✅ Salvando conversas no Supabase
- ✅ Funcionando 100% no EasyPanel!

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs detalhados
2. Execute o script de diagnóstico
3. Confirme todas as configurações
4. Teste cada componente isoladamente

---

**Dica Pro**: Sempre teste localmente antes de fazer deploy. Use o script `test_easypanel_integration.py` para validar toda a configuração!