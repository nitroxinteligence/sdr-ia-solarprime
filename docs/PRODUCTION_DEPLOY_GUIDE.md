# 🚀 SDR IA SolarPrime v0.2 - Helen Core Agent - Guia de Deploy em Produção

## 📋 Pré-requisitos

✅ **Serviços já configurados no EasyPanel:**
- Evolution API funcionando
- Instância WhatsApp ativa
- Supabase configurado
- Redis disponível
- Todas as credenciais no .env

## 🏗️ Arquitetura de Produção

```
┌─────────────────────────────────────┐
│           EASYPANEL VPS              │
├─────────────────────────────────────┤
│  🌐 Nginx (SSL + Rate Limiting)     │
│  📦 Helen Core Agent Container       │
│  🔄 Evolution API Container          │
│  💾 Redis Container                  │
│  🔗 Supabase (External)             │
└─────────────────────────────────────┘
```

## 🚀 Deploy Passo a Passo

### **1. Preparação dos Arquivos**

```bash
# Arquivos necessários para produção:
VPS/
├── Dockerfile                    # ✅ Container otimizado Helen Core
├── easypanel.yml                 # ✅ Configuração EasyPanel
├── docker-compose.production.yml # Para referência
└── nginx/sdr-solarprime.conf     # Configuração Nginx
```

### **2. Configuração no EasyPanel**

#### 2.1 Criar Nova Aplicação
1. Acesse seu painel EasyPanel
2. Clique em **"Create Service"** → **"App"**
3. Nome: `sdr-helen-core`
4. Selecione **"Build from Source"**

#### 2.2 Configurar Build
```yaml
Build Method: Dockerfile
Repository: Seu repositório Git
Branch: main
Dockerfile Path: VPS/Dockerfile
```

#### 2.3 Configurar Recursos
```yaml
CPU Limit: 2000m (2 cores)
Memory Limit: 4096Mi (4GB)
CPU Request: 1000m (1 core)  
Memory Request: 2048Mi (2GB)
```

#### 2.4 Configurar Volumes Persistentes
```yaml
Volumes:
- Name: data
  Path: /app/data
  Size: 10GB
  
- Name: logs  
  Path: /app/logs
  Size: 2GB
  
- Name: media
  Path: /app/media
  Size: 5GB
  
- Name: temp
  Path: /app/temp
  Size: 3GB
```

#### 2.5 Configurar Variáveis de Ambiente

**Copie TODAS as variáveis do arquivo `.env.production`:**

```bash
# Helen Core Agent Específicas
HELEN_CORE_MODE=production
CONTEXT_ANALYSIS_ENABLED=true
REASONING_ENABLED=true
MULTIMODAL_ENABLED=true

# APIs Essenciais  
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIzaSy...
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=3ECB607589F3-...

# Supabase
SUPABASE_URL=https://rcjcpwqez...
SUPABASE_SERVICE_KEY=eyJhbGci...

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=85Gfts3

# URLs da aplicação (AJUSTAR COM SEU DOMÍNIO)
API_BASE_URL=https://SEU-DOMINIO.easypanel.host
WEBHOOK_BASE_URL=https://SEU-DOMINIO.easypanel.host
```

#### 2.6 Configurar Health Check
```yaml
Health Check Path: /health
Interval: 30s
Timeout: 10s
Retries: 3
```

#### 2.7 Configurar Rede
```yaml
Port: 8000
Domain: Seu domínio customizado (opcional)
SSL: Habilitado (Let's Encrypt automático)
```

### **3. Deploy da Aplicação**

#### 3.1 Build e Deploy
1. Clique em **"Create App"**
2. EasyPanel iniciará o build automático
3. Aguarde o deploy completar (5-10 minutos)

#### 3.2 Verificar Status
```bash
# Status esperado:
✅ Build completed
✅ Container running  
✅ Health check passing
✅ SSL certificate active
```

### **4. Configuração Nginx (Opcional)**

Se você quiser usar nginx customizado:

```bash
# 1. Acesse seu servidor via SSH
# 2. Copie a configuração
sudo cp VPS/nginx/sdr-solarprime.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/sdr-solarprime.conf /etc/nginx/sites-enabled/

# 3. Ajuste o domínio no arquivo
sudo nano /etc/nginx/sites-available/sdr-solarprime.conf
# Altere: server_name api.seudominio.com.br;

# 4. Teste e reload
sudo nginx -t
sudo systemctl reload nginx
```

### **5. Configuração SSL Automática**

EasyPanel configurará SSL automaticamente, mas se usar nginx customizado:

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d api.seudominio.com.br

# Configurar renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Configurações Avançadas

### **Performance Otimizada**

```yaml
# Para alta demanda (ajustar conforme necessário)
CPU Limit: 4000m (4 cores)
Memory Limit: 8192Mi (8GB)
Replicas: 2 (apenas se necessário)
```

### **Monitoramento**

```yaml
# Logs centralizados
Log Driver: json-file
Max Size: 10m
Max Files: 3

# Métricas
METRICS_ENABLED=true
PERFORMANCE_MONITORING=true
```

### **Backup Automático**

```bash
# Configurar backup dos volumes no EasyPanel
# Ou script personalizado para Supabase
```

## 📊 Verificação de Deploy

### **1. Health Checks**

```bash
# Verificar aplicação
curl https://SEU-DOMINIO.easypanel.host/health

# Resposta esperada:
{
  "status": "healthy",
  "services": {
    "redis": "connected",
    "supabase": "connected", 
    "team": "ready"
  }
}
```

### **2. Teste Helen Core**

```bash
# Testar endpoint principal
curl https://SEU-DOMINIO.easypanel.host/

# Resposta esperada:
{
  "name": "SDR IA Solar Prime",
  "version": "0.2.0",
  "status": "operational"
}
```

### **3. Teste Webhook**

```bash
# Configurar webhook no Evolution API para:
https://SEU-DOMINIO.easypanel.host/webhook/evolution

# Enviar mensagem teste via WhatsApp
# Verificar logs no EasyPanel
```

## 🚨 Troubleshooting

### **Problemas Comuns**

#### Build Fails
```bash
# Verificar logs no EasyPanel
# Problemas comuns:
- Dependências faltando → Verificar requirements.txt
- Timeout → Aumentar timeout de build
- Memória insuficiente → Aumentar resources
```

#### Helen Core Não Responde
```bash
# Verificar variáveis de ambiente:
HELEN_CORE_MODE=production
CONTEXT_ANALYSIS_ENABLED=true

# Verificar logs:
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

#### Webhook Falha
```bash
# Verificar URL no Evolution API
# Verificar SSL válido
# Verificar rate limiting no nginx
```

#### Performance Baixa
```bash
# Aumentar recursos:
CPU: 2000m → 4000m
Memory: 4096Mi → 8192Mi

# Verificar variáveis:
UVICORN_WORKERS=1 (manter 1 para Helen Core)
CONTEXT_ANALYSIS_BATCH_SIZE=10
```

## 📈 Monitoramento

### **Métricas Importantes**

```yaml
CPU Usage: < 70%
Memory Usage: < 80%
Response Time: < 500ms
Error Rate: < 1%
Health Check: 100% uptime
```

### **Logs para Monitorar**

```bash
# Helen Core Agent
/app/logs/helen-core.log

# Aplicação principal  
/app/logs/app.log

# Nginx (se usar)
/var/log/nginx/sdr-solarprime.access.log
/var/log/nginx/sdr-solarprime.error.log
```

### **Alertas Recomendados**

```yaml
- CPU > 80% por 5 minutos
- Memory > 90% por 2 minutos  
- Health check failing por 1 minuto
- Error rate > 5% por 5 minutos
- Response time > 1s por 5 minutos
```

## 🎯 Resultado Esperado

Após o deploy bem-sucedido:

✅ **Helen Core Agent funcionando em produção**
✅ **90% das conversas resolvidas automaticamente**
✅ **Análise contextual inteligente das últimas 100 mensagens**
✅ **Reasoning ativado para casos complexos**
✅ **Processamento multimodal (imagem, áudio, documentos)**
✅ **Integração com SDR Team para casos especializados**
✅ **SSL automático e alta disponibilidade**

## 🔄 Atualizações

### **Deploy Automático**

```yaml
# Configure no EasyPanel:
Auto Deploy: Enabled
Branch: main
Webhook: GitHub/GitLab webhook
```

### **Deploy Manual**

```bash
# 1. Push para repositório
git add .
git commit -m "Update Helen Core Agent"
git push origin main

# 2. No EasyPanel clique "Rebuild"
# 3. Aguarde deploy (5-10 minutos)
# 4. Verificar health check
```

## 🎉 Deploy Finalizado!

**Helen Core Agent agora está rodando em produção no EasyPanel!**

- 🔗 **URL Principal**: https://SEU-DOMINIO.easypanel.host
- 📱 **Webhook WhatsApp**: https://SEU-DOMINIO.easypanel.host/webhook/evolution  
- 📊 **Health Check**: https://SEU-DOMINIO.easypanel.host/health
- 📚 **Documentação**: https://SEU-DOMINIO.easypanel.host/docs

**Sistema pronto para receber leads e converter em clientes!** 🚀