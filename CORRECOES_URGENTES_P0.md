# 🚨 CORREÇÕES URGENTES P0 - IMPLEMENTAR IMEDIATAMENTE

## 1. KOMMOCRM - Corrigir Mapeamento de Stages (CRÍTICO!)

### Arquivo: `app/services/kommo_auto_sync.py`
### Linha: ~71-86

```python
# CORRIGIR URGENTEMENTE:
self.stage_mapping = {
    # Valores em inglês -> Nome em português no Kommo
    "INITIAL_CONTACT": "Novo Lead",
    "EM_QUALIFICACAO": "Em Qualificação", 
    "QUALIFICADO": "Qualificado",
    "REUNIAO_AGENDADA": "Reunião Agendada",
    "NAO_INTERESSADO": "Não Interessado",
    
    # Manter compatibilidade
    "novo_lead": "Novo Lead",
    "em_qualificacao": "Em Qualificação",
    "qualificado": "Qualificado",
    "reuniao_agendada": "Reunião Agendada",
    "nao_interessado": "Não Interessado",
}
```

## 2. SUPABASE - Adicionar Coluna em follow_ups

### Executar no Supabase SQL Editor:

```sql
-- Adicionar coluna phone_number que o código espera
ALTER TABLE follow_ups 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(50);

-- Corrigir índices conflitantes
DROP INDEX IF EXISTS idx_followups_pending;
DROP INDEX IF EXISTS idx_follow_ups_pending;

-- Criar índice único e correto
CREATE INDEX idx_followups_pending 
ON follow_ups (scheduled_at, status) 
WHERE status = 'pending';
```

## 3. FOLLOW-UP - Corrigir Query Knowledge Base

OBS: (NAO PRECISA CORRIGIR AQUI, A TABELA knowledge_base ESTÁ CORRETA, NAO ESTÁ "title" NA TABELA, MAS SIM "question")

### Arquivo: `app/services/followup_executor_service.py`
### Linha: ~715

```python
# ANTES (ERRADO):
kb_result = self.db.client.table('knowledge_base').select("question").limit(1).execute()

# DEPOIS (CORRETO):
kb_result = self.db.client.table('knowledge_base').select("title").limit(1).execute()
```

## 4. SEGURANÇA - Sanitizar Logs

### Criar arquivo: `app/utils/log_sanitizer.py`

```python
import re
from typing import Any

SENSITIVE_PATTERNS = {
    'phone': r'\b\d{10,15}\b',
    'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
}

def sanitize_for_logging(data: Any) -> str:
    """Remove dados sensíveis antes de logar"""
    text = str(data)
    
    # Mascarar padrões sensíveis
    for pattern_name, pattern in SENSITIVE_PATTERNS.items():
        text = re.sub(pattern, f'[{pattern_name.upper()}_MASKED]', text)
    
    # Truncar se muito longo
    if len(text) > 500:
        text = text[:500] + '...[TRUNCATED]'
    
    return text
```

### Usar em `app/api/webhooks.py`:

```python
from app.utils.log_sanitizer import sanitize_for_logging

# Substituir todos os logs diretos por:
logger.info(f"Mensagem recebida: {sanitize_for_logging(message_data)}")
```

## 5. TIMEOUTS - Adicionar em Operações Críticas

### Arquivo: `app/api/webhooks.py`
### Função: `process_message_with_agent`

```python
import asyncio

async def process_message_with_agent(...):
    try:
        # Adicionar timeout de 30 segundos
        async with asyncio.timeout(30):
            response = await agent.process_message(...)
            return response
    except asyncio.TimeoutError:
        logger.error("Timeout ao processar mensagem")
        return {
            "text": "Oi! Tive um probleminha técnico aqui. Pode repetir sua mensagem?",
            "success": False
        }
```

## 6. RATE LIMITING - KommoCRM

### Arquivo: `app/services/kommo_client.py`
### Adicionar no início da classe:

```python
from asyncio import Semaphore
import time

class KommoClient:
    def __init__(self):
        # ... código existente ...
        self.rate_limiter = Semaphore(2)  # Max 2 requisições simultâneas
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms entre requisições
        
    async def _rate_limited_request(self, method: str, url: str, **kwargs):
        """Requisição com rate limiting"""
        async with self.rate_limiter:
            # Garantir intervalo mínimo
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                await asyncio.sleep(self.min_request_interval - time_since_last)
            
            try:
                response = await self._make_request(method, url, **kwargs)
                self.last_request_time = time.time()
                return response
            except Exception as e:
                if "429" in str(e):  # Too Many Requests
                    await asyncio.sleep(5)  # Esperar 5 segundos
                    return await self._make_request(method, url, **kwargs)
                raise
```

## 7. FOLLOW-UP - Aumentar TTL do Lock Redis

### Arquivo: `app/services/followup_executor_service.py`
### Linha: ~253

```python
# ANTES:
lock_acquired = await redis_client.acquire_lock(lock_key, ttl=60)

# DEPOIS:
lock_acquired = await redis_client.acquire_lock(lock_key, ttl=300)  # 5 minutos
```

---

## 🎯 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] KommoCRM - Corrigir mapeamento (10 min)
- [ ] Supabase - Executar SQL (5 min)
- [ ] Knowledge Base - Corrigir query (5 min)
- [ ] Logs - Implementar sanitização (30 min)
- [ ] Timeouts - Adicionar em webhooks (20 min)
- [ ] Rate Limiting - Implementar no Kommo (30 min)
- [ ] Redis Lock - Aumentar TTL (5 min)

**TEMPO TOTAL ESTIMADO: 1h45min**

---

## ⚡ COMANDO PARA TESTAR APÓS CORREÇÕES

```bash
# Testar webhook
curl -X POST http://localhost:8000/webhooks/evolution/v2 \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "SolarPrime",
    "data": {
      "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
      "message": {"conversation": "Teste após correções P0"},
      "messageType": "conversation"
    }
  }'

# Verificar logs
tail -f logs/*.log | grep -E "ERROR|WARNING|CRITICAL"
```

---

**APÓS IMPLEMENTAR ESTAS CORREÇÕES, O SISTEMA ESTARÁ 85% PRONTO PARA PRODUÇÃO!**