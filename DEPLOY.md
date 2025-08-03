# 🚀 Guia de Deploy - SDR IA SolarPrime v0.2

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Conta no Supabase configurada
- Evolution API configurada
- Redis disponível
- Chaves de API (OpenAI/Google)

## 🔧 Configuração Rápida

### 1. Clone o repositório
```bash
git clone https://github.com/nitroxinteligence/sdr-ia-solarprime.git
cd sdr-ia-solarprime
git checkout deploy
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
nano .env  # Edite com suas chaves
```

### 3. Crie a pasta de credenciais (se usar Google Calendar)
```bash
mkdir credentials
# Adicione seus arquivos JSON de credenciais do Google
```

## 🐳 Deploy com Docker

### Opção 1: Docker Compose (Recomendado)
```bash
# Desenvolvimento
docker-compose up -d

# Produção
docker-compose -f prod/docker-compose.production.yml up -d
```

### Opção 2: Docker Manual
```bash
# Build da imagem
docker build -t sdr-ia-solarprime:v0.2 -f prod/Dockerfile .

# Executar container
docker run -d \
  --name sdr-ia-solarprime \
  --env-file .env \
  -p 8000:8000 \
  --restart unless-stopped \
  sdr-ia-solarprime:v0.2
```

## ☁️ Deploy no EasyPanel

1. Importe o arquivo `prod/easypanel.yml`
2. Configure as variáveis de ambiente no painel
3. Conecte ao seu domínio
4. Deploy!

## 🔍 Verificação

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f sdr-ia-solarprime
```

## ⚙️ Variáveis de Ambiente Essenciais

```env
# APIs
OPENAI_API_KEY=sua_chave_aqui
GOOGLE_API_KEY=sua_chave_aqui

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_KEY=sua_chave_servico

# Evolution API
EVOLUTION_API_URL=http://sua-evolution:8080
EVOLUTION_API_KEY=sua_chave_evolution
EVOLUTION_INSTANCE_NAME=sdr-ia-solarprime

# Redis
REDIS_URL=redis://localhost:6379/0

# Controle de Agentes
ENABLE_QUALIFICATION_AGENT=true
ENABLE_CALENDAR_AGENT=true
ENABLE_FOLLOWUP_AGENT=true
ENABLE_KNOWLEDGE_AGENT=true
ENABLE_CRM_AGENT=true
ENABLE_BILL_ANALYZER_AGENT=true

# Timing (segundos)
TYPING_DURATION_SHORT=2
TYPING_DURATION_MEDIUM=4
TYPING_DURATION_LONG=7
RESPONSE_DELAY_MIN=1
RESPONSE_DELAY_MAX=5
```

## 🛠️ Troubleshooting

### Problema: Container não inicia
```bash
# Verificar logs
docker logs sdr-ia-solarprime

# Verificar variáveis de ambiente
docker exec sdr-ia-solarprime env
```

### Problema: Erro de conexão com Supabase
- Verifique se a URL e chave estão corretas
- Confirme se as tabelas foram criadas (veja sqls/)

### Problema: WhatsApp não conecta
- Verifique a Evolution API
- Confirme o webhook URL no .env
- Verifique o QR Code nos logs

## 📊 Monitoramento

### Logs com Emojis
O sistema usa logs com emojis para facilitar o debug:
- 🚀 Sistema iniciando
- ✅ Componente pronto
- ❌ Erro
- ⚠️ Aviso
- 🤖 AGENTIC SDR
- 👥 SDR Team
- 📨 Evolution API
- 🗄️ Supabase

### Métricas
Acesse `/health` para ver o status dos serviços:
```json
{
  "status": "healthy",
  "services": {
    "redis": "connected",
    "supabase": "connected",
    "team": "ready"
  }
}
```

## 🔐 Segurança

1. **NUNCA** commite o arquivo `.env` real
2. Use secrets manager em produção
3. Rotacione as chaves regularmente
4. Configure HTTPS com nginx/traefik
5. Use firewall para proteger portas

## 📝 Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Supabase configurado e tabelas criadas
- [ ] Evolution API conectada
- [ ] Redis disponível
- [ ] Credenciais do Google (se usar Calendar)
- [ ] Teste de health check passando
- [ ] Logs funcionando corretamente
- [ ] WhatsApp conectado
- [ ] Agentes habilitados conforme necessário

## 🆘 Suporte

Em caso de problemas:
1. Verifique os logs com `docker logs`
2. Consulte a documentação em `/docs`
3. Abra uma issue no GitHub

---

**Deploy rápido e seguro do SDR IA SolarPrime v0.2!** 🚀