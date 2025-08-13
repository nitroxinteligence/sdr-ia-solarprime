# 🔧 Correção do Deploy no EasyPanel

## ❌ Problema Atual
O serviço `sdr-api` está com erro ao fazer pull porque:
- Está tentando fazer pull de um branch antigo ou com conflitos
- O repositório pode ter mudanças incompatíveis

## ✅ Solução Recomendada

### Opção 1: Criar Novo Serviço (RECOMENDADO)

1. **No EasyPanel, crie um NOVO serviço:**
   - Clique em "Add Service"
   - Nome: `agentic-sdr-prime`
   - Tipo: GitHub

2. **Configure o repositório:**
   ```
   Repository URL: https://github.com/nitroxinteligence/agentic-sdr-solar-prime
   Branch: main
   Build Type: Dockerfile
   ```

3. **Configure as variáveis de ambiente:**
   ```env
   # APIs Principais
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

   # Habilitar Agentes
   ENABLE_CALENDAR_AGENT=true
   ENABLE_CRM_AGENT=true
   ENABLE_FOLLOWUP_AGENT=true

   # Configurações IA
   PRIMARY_AI_MODEL=gemini-1.5-pro
   FALLBACK_AI_MODEL=gpt-4-turbo
   AI_TEMPERATURE=0.7
   ```

4. **Configure recursos:**
   - Memory Limit: 2048 MB
   - CPU Limit: 1000m
   - Replicas: 1

5. **Configure o domínio:**
   - Domain: seu-dominio.com
   - Port: 8000

6. **Clique em "Deploy"**

### Opção 2: Corrigir Serviço Existente

Se preferir manter o serviço `sdr-api`:

1. **No terminal do EasyPanel ou SSH:**
   ```bash
   # Entre no diretório do serviço
   cd /var/lib/easypanel/services/sdr-api

   # Faça backup
   cp -r . ../sdr-api-backup

   # Reset do git
   git fetch --all
   git reset --hard origin/main
   
   # Ou mude para o novo repositório
   git remote set-url origin https://github.com/nitroxinteligence/agentic-sdr-solar-prime
   git fetch origin
   git checkout -B main origin/main
   ```

2. **Rebuild o serviço:**
   - No EasyPanel, clique em "Rebuild"
   - Aguarde o build completar

### Opção 3: Deploy Manual via Docker

1. **Clone o novo repositório:**
   ```bash
   git clone https://github.com/nitroxinteligence/agentic-sdr-solar-prime
   cd agentic-sdr-solar-prime
   ```

2. **Build a imagem:**
   ```bash
   docker build -t agentic-sdr:latest .
   ```

3. **Execute:**
   ```bash
   docker run -d \
     --name agentic-sdr \
     --restart unless-stopped \
     -p 8000:8000 \
     --env-file .env \
     -v $(pwd)/logs:/app/logs \
     agentic-sdr:latest
   ```

## 📋 Checklist Pós-Deploy

- [ ] Serviço rodando sem erros
- [ ] Webhook Evolution API configurado
- [ ] Conexão com Supabase funcionando
- [ ] Integração Kommo CRM ativa
- [ ] Google Calendar (se habilitado) conectado
- [ ] Logs sendo gerados em `/app/logs`
- [ ] Health check retornando 200 em `/health`

## 🆘 Troubleshooting

### Erro: "Failed to pull changes"
- **Causa**: Conflitos de git ou branch incorreto
- **Solução**: Use Opção 1 (criar novo serviço)

### Erro: "Module not found"
- **Causa**: Dependências não instaladas
- **Solução**: Verifique se o Dockerfile está correto

### Erro: "Connection refused"
- **Causa**: Serviço não está rodando na porta correta
- **Solução**: Verifique se a porta é 8000

### Erro: "Invalid API key"
- **Causa**: Variáveis de ambiente não configuradas
- **Solução**: Verifique todas as variáveis no EasyPanel

## 🚀 Resultado Esperado

Após o deploy bem-sucedido:
- Sistema AGENTIC SDR v0.3 rodando
- 98% funcional e pronto para produção
- Todos os agentes ativos e funcionando
- Logs disponíveis para monitoramento
- Webhook recebendo mensagens do WhatsApp

---

**Nota**: O novo repositório `agentic-sdr-solar-prime` está limpo, otimizado e sem os arquivos problemáticos do repositório antigo.