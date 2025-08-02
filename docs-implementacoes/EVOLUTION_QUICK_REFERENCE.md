# Evolution API - Guia Rápido

## 🚀 Início Rápido

### 1. Configurar Ambiente
```bash
# Copiar e editar .env
cp .env.example .env
nano .env

# Configurar Evolution API
EVOLUTION_API_URL=https://sua-api.com
EVOLUTION_API_KEY=sua-chave
EVOLUTION_INSTANCE_NAME=solarprime
```

### 2. Executar Setup
```bash
./scripts/setup_evolution.sh
```

### 3. Iniciar Aplicação
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Conectar WhatsApp
```bash
# Obter QR Code
curl http://localhost:8000/instance/qrcode

# Ou acesse no navegador
http://localhost:8000/instance/qrcode
```

## 📱 Endpoints Principais

### Status da Conexão
```bash
GET /instance/status
```

### Enviar Mensagem
```python
from services.whatsapp_service import whatsapp_service

await whatsapp_service.send_message(
    phone="5511999999999",
    message="Olá! Sou a Luna da SolarPrime"
)
```

### Enviar Enquete
```python
await evolution_client.send_poll(
    phone="5511999999999",
    question="Qual seu interesse?",
    options=["Economia", "Sustentabilidade", "Independência"]
)
```

## 🔍 Monitoramento

### Verificar Status
```bash
python scripts/monitor_evolution.py
```

### Monitoramento Contínuo
```bash
python scripts/monitor_evolution.py --mode continuous --interval 30
```

### Logs em Tempo Real
```bash
tail -f logs/app.log | grep WhatsApp
```

## 🛠️ Troubleshooting Rápido

### WhatsApp Desconectado
```bash
# Verificar status
curl http://localhost:8000/instance/status

# Reiniciar
curl -X POST http://localhost:8000/instance/restart \
  -H "X-API-Key: $ADMIN_API_KEY"
```

### Webhook Não Funciona
```bash
# Verificar config
curl http://localhost:8000/instance/webhook

# Reconfigurar
curl -X POST http://localhost:8000/instance/webhook/reset \
  -H "X-API-Key: $ADMIN_API_KEY"
```

### Redis Offline
```bash
# Verificar
redis-cli ping

# Reiniciar (macOS)
brew services restart redis

# Reiniciar (Linux)
sudo systemctl restart redis
```

## 🧪 Testes

### Executar Todos
```bash
./scripts/run_tests.sh
```

### Apenas Evolution
```bash
./scripts/run_tests.sh evolution
```

### Com Cobertura
```bash
./scripts/run_tests.sh all yes
```

## 📊 Métricas Importantes

- **Uptime**: > 95% esperado
- **Response Time**: < 3s médio
- **Cache Hit Rate**: > 70% ideal
- **Error Rate**: < 1% aceitável

## 🔐 Segurança

### Headers Obrigatórios
```http
apikey: sua-evolution-api-key
Content-Type: application/json
```

### Admin Endpoints
```http
X-API-Key: admin-api-key
```

## 📝 Logs Úteis

### Filtrar por Tipo
```bash
# Erros
grep ERROR logs/app.log

# Conexões
grep "CONNECTION_UPDATE" logs/app.log

# Mensagens processadas
grep "message_processed" logs/app.log
```

### Análise de Performance
```bash
# Tempo de resposta
grep "response_time" logs/app.log | awk '{print $NF}' | sort -n

# Volume por hora
grep "MESSAGES_UPSERT" logs/app.log | awk '{print $1}' | cut -d'T' -f2 | cut -d':' -f1 | sort | uniq -c
```

## 🚨 Comandos de Emergência

### Parar Tudo
```bash
# Parar aplicação
pkill -f "uvicorn api.main:app"

# Limpar Redis
redis-cli FLUSHDB

# Restart completo
docker-compose restart
```

### Backup Rápido
```bash
# Exportar conversas
python scripts/export_conversations.py --output backup.json

# Backup Redis
redis-cli --rdb dump.rdb
```

## 💡 Dicas de Performance

1. **Use cache sempre**: Redis está configurado, use-o!
2. **Batch operations**: Agrupe operações quando possível
3. **Async everywhere**: Nunca bloqueie com operações síncronas
4. **Monitor memory**: Redis pode crescer, configure maxmemory
5. **Log wisely**: Não logue dados sensíveis ou em excesso

## 🔗 Links Úteis

- [Evolution API Docs](https://doc.evolution-api.com)
- [FastAPI Docs](http://localhost:8000/docs)
- [Redis Commander](http://localhost:8081)
- [Supabase Dashboard](https://app.supabase.com)

## 📞 Suporte

1. Verificar logs primeiro
2. Consultar documentação completa
3. Executar scripts de diagnóstico
4. Contatar equipe de desenvolvimento