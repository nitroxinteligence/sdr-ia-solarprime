# 🚀 Deploy SDR IA SolarPrime no Easypanel (Hostinger VPS)

## 📋 Visão Geral

Como você já tem Evolution API e Redis rodando no Easypanel, vamos adicionar o SDR IA como mais um serviço, conectando tudo internamente!

## 🎯 Arquitetura no Easypanel

```
┌─────────────────────────── Easypanel ───────────────────────────┐
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │ Evolution API │◄───│   SDR IA     │───►│     Redis       │  │
│  │  (Existente) │    │  (FastAPI)   │    │  (Existente)    │  │
│  └──────────────┘    └──────────────┘    └─────────────────┘  │
│         ▲                    │                                   │
│         │                    ▼                                   │
│         │            ┌──────────────┐                          │
│         └────────────│   Supabase   │                          │
│                      │  (Externo)   │                          │
│                      └──────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

## 🔧 Passo a Passo

### 1️⃣ Prepare o Repositório

Crie um `Dockerfile` na raiz do projeto:

```dockerfile
# Dockerfile para Easypanel
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### 2️⃣ Configure o docker-compose.yml (Opcional)

```yaml
version: '3.8'

services:
  sdr-ia:
    build: .
    container_name: sdr-ia-solarprime
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379/0
    networks:
      - easypanel
    restart: unless-stopped

networks:
  easypanel:
    external: true
```

### 3️⃣ Acesse o Easypanel

1. Abra seu navegador e acesse:
   ```
   http://SEU_IP_HOSTINGER:3000
   ```

2. Faça login com suas credenciais

### 4️⃣ Crie um Novo Projeto

1. Clique em **"New Project"**
2. Nome: `sdr-ia-solarprime`
3. Clique em **"Create"**

### 5️⃣ Adicione o Serviço App

1. No projeto, clique em **"+ Service"**
2. Escolha **"App"**
3. Configure:

#### Configuração Básica:
- **Name**: `sdr-ia`
- **Source**: GitHub (conecte seu repositório)
  - Ou use **Docker Image** se preferir

#### Build Configuration:
- **Builder**: Dockerfile
- **Build Path**: `/` (raiz do projeto)
- **Dockerfile Path**: `Dockerfile`

#### Deploy Configuration:
- **Port**: `8000`
- **Health Check Path**: `/health`

### 6️⃣ Configure Variáveis de Ambiente

Clique em **"Environment"** e adicione:

```env
# Ambiente
ENVIRONMENT=production
DEBUG=False

# Gemini AI
GEMINI_API_KEY=AIzaSyDD3iJzp0XRuinxlO48vD7iR15IOqBxBT8
GEMINI_MODEL=gemini-2.5-pro

# Evolution API (use nome do serviço interno)
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=336B531BEA18-41AE-B5E9-ADC8BE525431
EVOLUTION_INSTANCE_NAME=Teste-Agente

# Redis (use nome do serviço interno)
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# Supabase
SUPABASE_URL=https://rcjcpwqezmlhenmhrski.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Webhook (será configurado após deploy)
WEBHOOK_BASE_URL=https://sdr-ia.seudominio.com
```

### 7️⃣ Configure Domínio

1. Na aba **"Domains"**, adicione:
   - Domain: `sdr-ia.seudominio.com`
   - Ou use o domínio fornecido pelo Easypanel

2. Marque **"Enable HTTPS"** (SSL automático)

### 8️⃣ Configure Rede Interna

Na aba **"Advanced"**:
- **Network**: Selecione a mesma rede que Evolution API e Redis estão usando
- Isso permite comunicação interna entre serviços

### 9️⃣ Deploy

1. Clique em **"Deploy"**
2. Acompanhe os logs de build
3. Aguarde o status ficar **"Running"**

### 🔟 Configure o Webhook

Após o deploy, atualize o webhook na Evolution API:

```bash
# Use o terminal do Easypanel ou SSH
curl -X POST "http://evolution-api:8080/webhook/set/Teste-Agente" \
  -H "apikey: 336B531BEA18-41AE-B5E9-ADC8BE525431" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "url": "https://sdr-ia.seudominio.com/webhook/whatsapp",
      "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "CONNECTION_UPDATE"],
      "webhookByEvents": false,
      "webhookBase64": false
    }
  }'
```

## 🔌 Conexões Internas no Easypanel

### Vantagem: Comunicação Interna

No Easypanel, os serviços podem se comunicar internamente sem expor portas públicas:

- **Evolution API**: `http://evolution-api:8080`
- **Redis**: `redis://redis:6379`
- **SDR IA**: `http://sdr-ia:8000`

### Script para Verificar Conexões

Crie um script de health check:

```python
# scripts/check_internal_connections.py
import httpx
import asyncio
import redis
import os

async def check_connections():
    print("🔍 Verificando conexões internas no Easypanel...")
    
    # Verificar Redis
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))
        r.ping()
        print("✅ Redis: Conectado")
    except Exception as e:
        print(f"❌ Redis: {e}")
    
    # Verificar Evolution API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('EVOLUTION_API_URL')}/instance/fetchInstances",
                headers={"apikey": os.getenv("EVOLUTION_API_KEY")}
            )
            if response.status_code == 200:
                print("✅ Evolution API: Conectado")
            else:
                print(f"❌ Evolution API: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Evolution API: {e}")

if __name__ == "__main__":
    asyncio.run(check_connections())
```

## 📊 Monitoramento no Easypanel

### Logs em Tempo Real
1. Acesse o serviço `sdr-ia`
2. Clique na aba **"Logs"**
3. Veja logs em tempo real

### Métricas
- CPU Usage
- Memory Usage
- Network I/O
- Disk Usage

### Health Checks
O Easypanel fará health checks automáticos em `/health`

## 🚀 Auto Deploy com GitHub

1. Na aba **"Build"**, ative:
   - **Auto Deploy**: ON
   - **Branch**: main (ou sua branch)

2. Cada push no GitHub fará deploy automático!

## 🔧 Otimizações para Easypanel

### 1. Dockerfile Otimizado

```dockerfile
# Multi-stage build para imagem menor
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Persistência de Dados

Na aba **"Mounts"**, adicione volumes se necessário:
- `/app/data` → Para SQLite storage do AGnO
- `/app/logs` → Para logs persistentes

### 3. Recursos

Na aba **"Resources"**, ajuste:
- **Memory**: 1-2 GB
- **CPU**: 0.5-1 core

## ✅ Checklist de Deploy

- [ ] Dockerfile criado e testado
- [ ] Repositório GitHub conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Domínio configurado com HTTPS
- [ ] Rede interna configurada
- [ ] Deploy bem-sucedido
- [ ] Webhook atualizado na Evolution API
- [ ] Health check respondendo
- [ ] Logs sem erros
- [ ] Auto deploy ativado

## 🎯 Vantagens do Easypanel

1. **Interface Visual**: Não precisa de linha de comando
2. **SSL Automático**: Let's Encrypt integrado
3. **Auto Deploy**: Push to deploy do GitHub
4. **Logs Centralizados**: Veja todos os logs em um lugar
5. **Backup Fácil**: Snapshots do projeto
6. **Rede Interna**: Comunicação segura entre serviços
7. **Monitoramento**: Métricas em tempo real

## 🆘 Troubleshooting

### Problema: Não conecta com Redis/Evolution
- Verifique se estão na mesma rede
- Use nomes de serviço internos, não localhost

### Problema: Build falha
- Verifique o Dockerfile
- Veja logs de build completos

### Problema: Webhook não funciona
- Confirme que o domínio está acessível
- Teste com curl externo

## 🎉 Pronto!

Agora você tem:
- ✅ SDR IA rodando no Easypanel
- ✅ Conectado com Evolution API e Redis internamente
- ✅ Webhook público funcionando
- ✅ Deploy automático do GitHub
- ✅ SSL/HTTPS configurado
- ✅ Logs e monitoramento

Tudo gerenciado visualmente pelo Easypanel!