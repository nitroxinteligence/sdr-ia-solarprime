# Análise do Sistema de Follow-up - SDR IA SolarPrime

## 🔍 Problema Identificado

O sistema de follow-up não está funcionando - os follow-ups são criados no banco de dados mas as mensagens nunca são enviadas após 30 minutos.

### Log de Exemplo:
```
2025-07-30 04:31:26.784 | INFO | services.follow_up_service:create_follow_up_after_message:91 - 
Follow-up criado para lead 3727426f-aab3-495d-a50b-e28d5e82b1dd - Tipo: first_contact - Agendado para: 02:01 (30 minutos)
```

## 🔎 Análise Detalhada

### 1. **Dois Sistemas de Follow-up Separados**

#### a) `services/follow_up_service.py`
- ✅ Cria registros na tabela `follow_ups` com status 'pending'
- ❌ NÃO tem nenhum worker/task para processar esses registros
- ❌ O método `get_pending_follow_ups()` existe mas nunca é chamado
- ❌ Não tem integração com Celery ou qualquer scheduler

#### b) `services/kommo_follow_up_service.py`
- ✅ Tem tasks do Celery (@celery_app.task)
- ✅ Tem beat schedule configurado (a cada 30 minutos)
- ⚠️ Usa um sistema diferente, não processa os registros da tabela `follow_ups`

### 2. **Follow-up Workflow com AGnO**

#### `workflows/follow_up_workflow.py`
- ✅ Tem um `FollowUpScheduler` completo que processa a tabela `follow_ups`
- ✅ Implementado corretamente com AGnO Workflow
- ✅ Processa follow-ups pendentes e envia mensagens via WhatsApp
- ⚠️ Verifica follow-ups a cada 5 MINUTOS (linha 377)
- ❌ Só é iniciado no `main_v2.py`, não no `main.py`

### 3. **Problemas de Inicialização**

#### `api/main_v2.py` (linha 41)
```python
follow_up_scheduler.start() if config.enable_follow_up else asyncio.sleep(0)
```
- ❌ BUG: Usa `config.enable_follow_up` mas deveria ser `agent_config.enable_follow_up`
- ❌ Este erro faz com que o scheduler nunca seja iniciado

#### `api/main.py`
- ❌ Não tem NENHUMA referência ao follow_up_scheduler
- ❌ Se o servidor estiver usando main.py, o scheduler nunca será iniciado

## 🚨 Causa Raiz

1. **Se usando `main.py`**: O follow_up_scheduler nunca é iniciado
2. **Se usando `main_v2.py`**: O scheduler não inicia devido ao bug na linha 41
3. **Resultado**: Os follow-ups são criados no banco mas nunca processados

## ✅ Soluções Propostas

### Solução 1: Corrigir o main_v2.py (Recomendada)

```python
# api/main_v2.py linha 41
# ANTES:
follow_up_scheduler.start() if config.enable_follow_up else asyncio.sleep(0)

# DEPOIS:
from config.agent_config import config as agent_config
follow_up_scheduler.start() if agent_config.enable_follow_up else asyncio.sleep(0)
```

### Solução 2: Adicionar ao main.py (Se necessário)

Se o servidor estiver usando `main.py`, adicionar no lifespan:

```python
# api/main.py
from workflows.follow_up_workflow import follow_up_scheduler
from config.agent_config import config as agent_config

# No lifespan, após inicializar outros serviços:
if agent_config.enable_follow_up:
    asyncio.create_task(follow_up_scheduler.start())
    logger.info("✅ Follow-up scheduler iniciado")
```

### Solução 3: Reduzir Intervalo de Verificação

No `follow_up_workflow.py` linha 377, mudar de 5 minutos para 1 minuto:

```python
# ANTES:
await asyncio.sleep(300)  # 5 minutos

# DEPOIS:
await asyncio.sleep(60)   # 1 minuto
```

### Solução 4: Alternativa com Celery (Mais complexa)

Adicionar uma task do Celery ao `follow_up_service.py`:

```python
from services.tasks import celery_app
from celery.schedules import crontab

@celery_app.task(name="process_pending_follow_ups")
def process_pending_follow_ups():
    """Processa follow-ups pendentes"""
    import asyncio
    from services.follow_up_service import follow_up_service
    from services.evolution_api import evolution_client
    
    loop = asyncio.get_event_loop()
    pending = loop.run_until_complete(follow_up_service.get_pending_follow_ups())
    
    for follow_up in pending:
        # Enviar mensagem via WhatsApp
        # Marcar como executado
        pass

# Adicionar ao beat schedule
celery_app.conf.beat_schedule.update({
    'process-follow-ups': {
        'task': 'process_pending_follow_ups',
        'schedule': crontab(minute='*'),  # A cada minuto
    }
})
```

## 📋 Plano de Ação

1. **Verificar qual main.py está em uso no servidor**
   ```bash
   ps aux | grep uvicorn
   # ou
   docker ps # verificar comando do container
   ```

2. **Aplicar a correção apropriada**:
   - Se `main_v2.py`: Corrigir bug da linha 41
   - Se `main.py`: Adicionar inicialização do scheduler

3. **Reduzir intervalo de verificação** para 1 minuto

4. **Testar**:
   - Verificar logs para confirmar que o scheduler iniciou
   - Criar um follow-up de teste
   - Aguardar 30 minutos e verificar se a mensagem foi enviada

## 🔧 Configurações Relevantes

- `ENABLE_FOLLOW_UP=true` (habilitado por padrão)
- `FOLLOW_UP_DELAY_MINUTES=30` (primeiro follow-up após 30 minutos)
- `FOLLOW_UP_SECOND_DELAY_HOURS=24` (segundo follow-up após 24 horas)

## 📊 Resumo

O sistema de follow-up está bem implementado mas não está sendo executado devido a:
1. Bug de configuração no `main_v2.py`
2. Falta de inicialização no `main.py`
3. Intervalo de verificação muito longo (5 minutos)

Com as correções propostas, o sistema funcionará corretamente, processando follow-ups a cada minuto e enviando mensagens nos tempos configurados.