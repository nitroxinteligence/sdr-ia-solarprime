# 🔧 Guia de Troubleshooting - SDR Agent Helen Vieira

## 🎯 Objetivo

Este guia fornece soluções para os problemas mais comuns encontrados na operação do SDR Agent Helen Vieira, organizados por categoria e severidade.

## 🚨 Problemas Críticos (Sistema Parado)

### 1. Helen não responde mensagens

#### Sintomas
- Mensagens chegam mas não há resposta
- Cliente vê apenas um "visto" sem resposta
- Logs mostram mensagens recebidas mas não processadas

#### Diagnóstico
```bash
# 1. Verificar se o container está rodando
docker ps | grep agente

# 2. Verificar logs do agente
docker-compose logs agente -f --tail=100

# 3. Verificar conexão do WhatsApp
curl -X GET http://localhost:8080/instance/connectionState/solarprime \
  -H "apikey: sua-api-key"

# 4. Verificar health check
curl http://localhost:8000/health
```

#### Soluções

**Se o container não está rodando:**
```bash
docker-compose up -d
```

**Se há erro de conexão com WhatsApp:**
```bash
# Reiniciar Evolution API
docker-compose restart evolution

# Se persistir, reconectar WhatsApp via QR Code
# Acesse: http://seu-servidor:8080
```

**Se há erro de API do Gemini:**
```bash
# Verificar chave da API
echo $GOOGLE_API_KEY

# Testar API diretamente
curl -X POST https://generativelanguage.googleapis.com/v1/models/gemini-2.5-pro:generateContent \
  -H "x-goog-api-key: $GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

### 2. Erro "Connection refused" no webhook

#### Sintomas
- Evolution API não consegue enviar webhooks
- Logs mostram "connection refused" ou timeout

#### Diagnóstico
```bash
# Verificar se o serviço está escutando
netstat -tlnp | grep 8000

# Verificar firewall
sudo ufw status

# Testar webhook manualmente
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"event":"test"}'
```

#### Soluções

**Liberar porta no firewall:**
```bash
sudo ufw allow 8000
sudo ufw reload
```

**Verificar Nginx (se usando):**
```nginx
# /etc/nginx/sites-available/sdr-agent
location /webhook {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Database connection error

#### Sintomas
- Erro "connection to server failed"
- Mensagens não são salvas
- Histórico não carrega

#### Diagnóstico
```bash
# Testar conexão com Supabase
python -c "
from supabase import create_client
import os
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)
print(supabase.table('profiles').select('*').limit(1).execute())
"
```

#### Soluções

**Verificar variáveis de ambiente:**
```bash
# Conferir se estão definidas
env | grep SUPABASE

# Recarregar se necessário
source .env
docker-compose restart
```

**Verificar status do Supabase:**
- Acesse: https://app.supabase.com
- Verifique se o projeto está ativo
- Confirme limites de uso

---

## ⚠️ Problemas de Alta Prioridade

### 4. Mensagens duplicadas

#### Sintomas
- Helen responde múltiplas vezes
- Cliente recebe mensagens repetidas
- Logs mostram processamento duplicado

#### Diagnóstico
```bash
# Verificar se há múltiplas instâncias rodando
docker ps | grep agente

# Verificar logs por duplicação
docker-compose logs agente | grep "message_id"

# Verificar Redis
docker exec -it redis redis-cli
> KEYS *message*
```

#### Soluções

**Implementar deduplicação:**
```python
# No message_processor.py
async def is_duplicate(self, message_id: str) -> bool:
    key = f"processed:{message_id}"
    if await self.redis.exists(key):
        return True
    await self.redis.setex(key, 300, "1")  # 5 minutos TTL
    return False
```

**Limpar cache se necessário:**
```bash
docker exec -it redis redis-cli FLUSHDB
```

### 5. Follow-ups não são enviados

#### Sintomas
- Sistema não envia mensagens de acompanhamento
- Leads ficam sem resposta após 30 minutos
- Confirmações de reunião não são enviadas

#### Diagnóstico
```bash
# Verificar Celery worker
docker ps | grep celery

# Verificar fila de tarefas
docker exec -it redis redis-cli
> LLEN celery

# Ver logs do Celery
docker-compose logs celery -f
```

#### Soluções

**Reiniciar Celery:**
```bash
docker-compose restart celery celery-beat
```

**Verificar configuração de horários:**
```python
# Em config.py
FOLLOW_UP_DELAYS = {
    'immediate': timedelta(minutes=30),
    'daily': timedelta(hours=24),
    'meeting_reminder': timedelta(hours=8)
}
```

### 6. Erro ao processar imagens

#### Sintomas
- Contas de luz não são analisadas
- Erro "Failed to process image"
- OCR não funciona

#### Diagnóstico
```bash
# Verificar se a imagem foi baixada
ls -la /tmp/media/

# Testar processamento manual
python -c "
from services.media_processor import process_energy_bill
result = process_energy_bill('path/to/image.jpg')
print(result)
"
```

#### Soluções

**Verificar dependências:**
```bash
# Instalar ferramentas de imagem
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-por
pip install pillow pytesseract
```

**Aumentar timeout:**
```python
# Em media_processor.py
DOWNLOAD_TIMEOUT = 30  # segundos
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
```

---

## 🟡 Problemas Médios

### 7. Taxa de resposta lenta

#### Sintomas
- Helen demora mais de 10 segundos para responder
- Clientes reclamam de lentidão
- Timeout em algumas mensagens

#### Diagnóstico
```bash
# Monitorar uso de recursos
docker stats

# Verificar latência da API
time curl -X POST http://localhost:8000/health

# Ver logs de performance
docker-compose logs agente | grep "response_time"
```

#### Soluções

**Otimizar recursos:**
```yaml
# docker-compose.yml
services:
  agente:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

**Ajustar workers:**
```bash
# Em Dockerfile ou comando
CMD ["uvicorn", "agente.main:app", "--workers", "4"]
```

### 8. Agendamentos não aparecem no Kommo

#### Sintomas
- Reuniões agendadas mas não aparecem no CRM
- Cards não movem no pipeline
- Erros de sincronização

#### Diagnóstico
```bash
# Testar API do Kommo
curl -X GET https://suaempresa.kommo.com/api/v4/leads \
  -H "Authorization: Bearer seu-token"

# Ver logs de integração
docker-compose logs agente | grep "kommo"
```

#### Soluções

**Verificar token:**
```python
# Testar token manualmente
from services.kommo_service import KommoService
kommo = KommoService()
print(kommo.test_connection())
```

**Reautenticar se necessário:**
- Acesse Kommo > Integrações
- Gere novo token de longa duração
- Atualize no .env

### 9. Relatórios não são enviados

#### Sintomas
- Relatório semanal não chega no WhatsApp
- Erro ao gerar estatísticas
- Dados incompletos

#### Diagnóstico
```bash
# Verificar agendamento
docker exec -it celery celery -A tasks inspect scheduled

# Ver logs de relatórios
docker-compose logs celery | grep "report"

# Testar geração manual
python -c "
from services.reports import generate_weekly_report
report = generate_weekly_report()
print(report)
"
```

#### Soluções

**Verificar configuração:**
```env
REPORT_DAY_OF_WEEK=monday
REPORT_TIME=09:00
WHATSAPP_GROUP_ID=120363XXXXXXXXXX@g.us
```

**Executar manualmente:**
```bash
docker exec -it celery celery -A tasks call services.tasks.send_weekly_report
```

---

## 🟢 Problemas Menores

### 10. Emojis não aparecem corretamente

#### Sintomas
- Emojis aparecem como "?"
- Caracteres especiais corrompidos
- Acentuação incorreta

#### Solução
```python
# Garantir UTF-8 em todos os lugares
# Em config.py
DEFAULT_ENCODING = 'utf-8'

# No banco de dados
ALTER DATABASE seu_banco SET client_encoding TO 'UTF8';
```

### 11. Horário comercial não funciona

#### Sintomas
- Helen responde fora do horário
- Não informa sobre horário de atendimento

#### Solução
```env
# Verificar timezone
TIMEZONE=America/Recife
BUSINESS_HOURS_START=08:00
BUSINESS_HOURS_END=18:00
```

### 12. Score de qualificação incorreto

#### Sintomas
- Leads qualificados aparecem como desqualificados
- Score não reflete realidade

#### Solução
```python
# Ajustar pesos em qualification_flow.py
SCORE_WEIGHTS = {
    'bill_value': 30,
    'property_ownership': 20,
    'decision_maker': 20,
    'urgency': 15,
    'engagement': 15
}
```

---

## 🛠️ Ferramentas de Diagnóstico

### Script de Diagnóstico Completo

```bash
#!/bin/bash
# diagnostico.sh

echo "=== DIAGNÓSTICO SDR AGENT ==="
echo

echo "1. Verificando containers..."
docker ps --format "table {{.Names}}\t{{.Status}}"
echo

echo "2. Verificando conectividade..."
curl -s http://localhost:8000/health | jq '.'
echo

echo "3. Verificando WhatsApp..."
curl -s http://localhost:8080/instance/connectionState/solarprime \
  -H "apikey: $EVOLUTION_API_KEY" | jq '.'
echo

echo "4. Verificando banco de dados..."
echo "SELECT COUNT(*) as total_leads FROM leads;" | \
  docker exec -i postgres psql -U postgres -d sdr_agent
echo

echo "5. Verificando Redis..."
docker exec -it redis redis-cli ping
echo

echo "6. Últimos erros..."
docker-compose logs --tail=20 | grep ERROR
echo

echo "=== FIM DO DIAGNÓSTICO ==="
```

### Monitoramento Contínuo

```bash
# Monitor em tempo real
watch -n 5 'docker stats --no-stream'

# Logs em tempo real com filtro
docker-compose logs -f | grep -E "(ERROR|WARNING|failed)"

# Métricas do sistema
htop
iotop
nethogs
```

---

## 📊 Métricas de Saúde

### Indicadores Normais

| Métrica | Valor Normal | Alerta | Crítico |
|---------|--------------|--------|---------|
| CPU Usage | < 60% | > 80% | > 95% |
| Memory Usage | < 70% | > 85% | > 95% |
| Response Time | < 3s | > 5s | > 10s |
| Error Rate | < 1% | > 5% | > 10% |
| Queue Size | < 50 | > 100 | > 500 |

### Comandos de Verificação

```bash
# CPU e Memória
docker stats --no-stream

# Tempo de resposta
time curl http://localhost:8000/health

# Taxa de erro (últimas 1000 linhas)
docker-compose logs agente --tail=1000 | grep -c ERROR

# Tamanho da fila
docker exec -it redis redis-cli LLEN celery
```

---

## 🚑 Procedimentos de Emergência

### 1. Sistema Completamente Parado

```bash
# Passo 1: Backup imediato
./agente/scripts/backup.sh emergency

# Passo 2: Parar tudo
docker-compose down

# Passo 3: Limpar e reiniciar
docker system prune -f
docker-compose up -d

# Passo 4: Verificar logs
docker-compose logs -f
```

### 2. Rollback de Emergência

```bash
# Usar script de rollback
./agente/scripts/rollback.sh --emergency

# Ou manualmente
git checkout stable
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 3. Recuperação de Dados

```bash
# Restaurar último backup
./agente/scripts/restore_backup.sh latest

# Verificar integridade
python agente/scripts/check_data_integrity.py
```

---

## 📞 Escalonamento

### Quando Escalar

1. **Para Nível 2 (Técnico):**
   - Após 30 minutos sem solução
   - Erro afeta > 10% dos usuários
   - Problema recorrente

2. **Para Nível 3 (Desenvolvimento):**
   - Bug identificado no código
   - Necessita alteração estrutural
   - Problema de segurança

### Informações para Incluir

- Data/hora do problema
- Passos executados
- Logs relevantes
- IDs de exemplo
- Impacto no negócio

---

## 📚 Recursos Adicionais

- [Documentação da API](API_REFERENCE.md)
- [Guia de Arquitetura](ARCHITECTURE.md)
- [Manual de Instalação](INSTALLATION.md)
- [Fórum de Suporte](https://suporte.nitroxai.com)

---

*Última atualização: Dezembro 2024*
*Versão: 2.0*
*Desenvolvido por Nitrox AI*