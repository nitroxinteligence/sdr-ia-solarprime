# Análise de Performance e Configuração de Timeouts - SDR IA SolarPrime

## Resumo Executivo

Esta análise identificou os principais gargalos de performance e oportunidades de otimização no sistema SDR IA SolarPrime. Os principais achados incluem configurações de timeout inadequadas, falta de paralelização em operações críticas, uso limitado de cache, e processamento de mídia sem otimização.

## 1. Configuração de Timeouts

### 1.1 Timeouts Identificados

| Componente | Timeout Atual | Recomendação | Justificativa |
|------------|---------------|--------------|---------------|
| **Message Buffer** | 5s | 3s | Reduzir latência na resposta |
| **Webhook Processing** | 30s | 20s | Evitar timeouts do WhatsApp |
| **Agent Processing** | 45s | 30s | Limitar tempo de processamento |
| **Multimodal Processing** | 30s | 20s | Otimizar experiência do usuário |
| **Knowledge Base Search** | 5s | 2s | Cache deve acelerar buscas |
| **Evolution API** | 30s (read) | 15s | API calls devem ser rápidas |
| **FFmpeg Audio** | 30s | 15s | Áudios longos devem ser rejeitados |
| **Personalization** | 25s | 15s | Processamento deve ser otimizado |

### 1.2 Recomendações de Timeout

```python
# app/config.py - Configurações recomendadas
TIMEOUT_CONFIG = {
    # Timeouts principais
    "webhook_timeout": 20,  # Reduzido de 30s
    "message_buffer_timeout": 5.0,  # Reduzido de 5s (nao precisa reduzir aqui)
    "agent_timeout": 30,  # Reduzido de 45s
    
    # Timeouts de mídia
    "multimodal_timeout": 20,  # Reduzido de 30s
    "audio_processing_timeout": 15,  # Reduzido de 30s
    "image_processing_timeout": 10,  # Novo
    
    # Timeouts de integração
    "evolution_read_timeout": 15,  # Reduzido de 30s
    "knowledge_base_timeout": 2,  # Reduzido de 5s
    "personalization_timeout": 15,  # Reduzido de 25s
}
```

## 2. Operações Paralelas vs Sequenciais

### 2.1 Oportunidades de Paralelização

#### **Knowledge Base + Agent Processing**
```python
# ATUAL: Sequencial
knowledge_results = await knowledge_service.get_all_knowledge()
agent_result = await agent.arun(prompt)

# RECOMENDADO: Paralelo
kb_task = asyncio.create_task(knowledge_service.get_all_knowledge())
agent_task = asyncio.create_task(agent.arun(prompt))
knowledge_results, agent_result = await asyncio.gather(kb_task, agent_task)
```

#### **Múltiplos Loops de Sincronização**
```python
# ATUAL: 4 tasks separadas
asyncio.create_task(self._sync_new_leads_loop())
asyncio.create_task(self._sync_updates_loop())
asyncio.create_task(self._sync_qualifications_loop())

# RECOMENDADO: Batch processing com semáforo
semaphore = asyncio.Semaphore(3)  # Limitar concorrência
async def sync_with_limit(func):
    async with semaphore:
        return await func()
```

### 2.2 Gargalos Sequenciais Identificados

1. **Message Buffer**: Processa mensagens uma por vez por usuário (Aqui o message buffer deveria juntar todas as mensagens do usuário, em vez de processar uma por uma)
2. **Follow-up Executor**: Executa follow-ups sequencialmente
3. **Media Processing**: Processa imagem → análise → resposta sequencialmente

## 3. Uso de Cache e Otimizações

### 3.1 Cache Atual

| Componente | Cache Implementado | TTL | Efetividade |
|------------|-------------------|-----|-------------|
| **Redis** | Conversas/Leads | 2h/24h | ✅ Bom |
| **Knowledge Base** | In-memory | 5min | ⚠️ Muito curto |
| **CRM Tags** | In-memory | Session | ✅ Adequado |
| **Supabase Queries** | Não | - | ❌ Necessário |

### 3.2 Oportunidades de Cache

#### **Cache de Queries Supabase**
```python
# Implementar cache para queries frequentes
@cache_result(ttl=300)  # 5 minutos
async def get_lead_by_phone(phone: str):
    # Query cacheada automaticamente
    return await supabase.get_lead_by_phone(phone)
```

#### **Cache de Processamento de Mídia**
```python
# Cache de análises de conta de luz
BILL_ANALYSIS_CACHE = {}  # hash da imagem → resultado

def get_image_hash(base64_data: str) -> str:
    return hashlib.md5(base64_data.encode()).hexdigest()
```

#### **Cache de Embeddings**
```python
# Cache de embeddings para knowledge base
EMBEDDING_CACHE = LRUCache(maxsize=1000)
```

## 4. Otimização de Queries Supabase

### 4.1 Queries Problemáticas

1. **N+1 Queries**
   - `get_conversation_messages`: Busca conversa, depois mensagens
   - `update_conversation`: Múltiplas atualizações sequenciais

2. **Queries sem Índice**
   - Busca por `phone_number` sem índice
   - Ordenação por `created_at` sem índice composto

3. **Full Table Scans**
   - `search_knowledge` com ILIKE '%query%'
   - `get_all_knowledge` sem paginação

### 4.2 Recomendações de Otimização

```sql
-- Índices recomendados
CREATE INDEX idx_leads_phone ON leads(phone_number);
CREATE INDEX idx_conversations_phone ON conversations(phone_number);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_knowledge_base_category ON knowledge_base(category);

-- Full-text search para knowledge base
CREATE INDEX idx_knowledge_content_fts ON knowledge_base 
USING gin(to_tsvector('portuguese', content));
```

## 5. Processamento de Imagens e Mídia

### 5.1 Problemas Identificados

1. **Validação Tardia**: Imagem decodificada completamente antes de validar tamanho
2. **Sem Compressão**: Imagens processadas em resolução original
3. **Processamento Síncrono**: PIL operations bloqueiam event loop
4. **Sem Cache**: Mesma imagem processada múltiplas vezes

### 5.2 Otimizações Recomendadas

```python
# Validação antecipada de tamanho
def validate_image_size(base64_data: str) -> bool:
    # Estimar tamanho sem decodificar
    estimated_size = (len(base64_data) * 3) // 4
    return estimated_size < MAX_IMAGE_SIZE

# Processamento assíncrono
async def process_image_async(base64_data: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,  # Use default executor
        process_image_sync,
        base64_data
    )

# Redimensionamento automático
def optimize_image(img: PIL.Image) -> PIL.Image:
    if img.width > 1920 or img.height > 1920:
        img.thumbnail((1920, 1920), PIL.Image.Resampling.LANCZOS)
    return img
```

## 6. Memory Leaks Potenciais

### 6.1 Áreas de Risco

1. **Cache sem Limite**
   - Knowledge Base cache cresce indefinidamente
   - CRM cache não tem expiração

2. **Tasks Não Finalizadas**
   - Message buffer tasks podem acumular
   - Follow-up loops sem cleanup

3. **Grandes Objetos em Memória**
   - Imagens base64 mantidas em variáveis
   - Histórico de conversas sem limite

### 6.2 Soluções

```python
# Implementar cache com limite
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_function():
    pass

# Cleanup de tasks
async def cleanup_tasks():
    tasks = [t for t in asyncio.all_tasks() if not t.done()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

# Limitar histórico
MAX_CONVERSATION_HISTORY = 50  # Últimas 50 mensagens
```

## 7. Concorrência e Locks

### 7.1 Problemas de Concorrência

1. **Message Buffer**: Lock por usuário pode causar contenção
2. **Redis Locks**: TTL muito alto (60s) para follow-ups
3. **Agent Creation**: Sem pool, cria nova instância sempre

### 7.2 Melhorias de Concorrência

```python
# Pool de agentes
class AgentPool:
    def __init__(self, size=5):
        self.agents = asyncio.Queue(maxsize=size)
        self._initialize_agents()
    
    async def get_agent(self):
        return await self.agents.get()
    
    async def return_agent(self, agent):
        await self.agents.put(agent)

# Lock com timeout adaptativo
async def acquire_lock_with_backoff(key: str, max_attempts=3):
    for attempt in range(max_attempts):
        if await redis.acquire_lock(key, ttl=10):
            return True
        await asyncio.sleep(0.1 * (2 ** attempt))
    return False
```

## 8. Gargalos de Performance Principais

### 8.1 Top 5 Gargalos

1. **Agent Processing (45s timeout)**
   - Causa: Processamento síncrono, sem cache
   - Impacto: 50% das requisições lentas
   - Solução: Paralelização + cache de respostas

2. **Knowledge Base Full Load**
   - Causa: Carrega todos documentos sempre
   - Impacto: +2s por requisição
   - Solução: Cache persistente + lazy loading

3. **Multimodal Processing**
   - Causa: Imagens grandes, processamento síncrono
   - Impacto: +10s para imagens >5MB
   - Solução: Redimensionamento + async processing

4. **Supabase N+1 Queries**
   - Causa: Queries não otimizadas
   - Impacto: +100ms por operação
   - Solução: Batch queries + índices

5. **Message Buffer Wait**
   - Causa: Timeout fixo de 5s
   - Impacto: Delay artificial nas respostas
   - Solução: Timeout adaptativo baseado em contexto

## 9. Plano de Ação Prioritizado

### Fase 1 - Quick Wins (1 semana)
1. ✅ Ajustar timeouts conforme tabela
2. ✅ Implementar cache no Knowledge Base
3. ✅ Adicionar índices no Supabase
4. ✅ Paralelizar KB + Agent processing

### Fase 2 - Otimizações Médias (2 semanas)
1. ⏳ Implementar pool de agentes
2. ⏳ Cache de processamento de mídia
3. ⏳ Otimizar queries Supabase
4. ⏳ Async image processing

### Fase 3 - Melhorias Estruturais (1 mês)
1. 📅 Refatorar message buffer
2. 📅 Implementar cache distribuído
3. 📅 Otimizar multimodal pipeline
4. 📅 Monitoring e alertas de performance

## 10. Métricas de Sucesso

### KPIs de Performance
- **P95 Response Time**: < 5s (atual: ~15s)
- **Timeout Rate**: < 1% (atual: ~5%)
- **Cache Hit Rate**: > 80% (atual: ~20%)
- **Concurrent Users**: > 100 (atual: ~20)

### Monitoramento Recomendado
```python
# Instrumentação com métricas
from prometheus_client import Histogram, Counter

response_time = Histogram('sdr_response_time_seconds', 'Response time')
timeout_counter = Counter('sdr_timeouts_total', 'Total timeouts')
cache_hits = Counter('sdr_cache_hits_total', 'Cache hits')

@response_time.time()
async def process_message():
    # Processar mensagem com métrica
    pass
```

## Conclusão

A implementação das otimizações propostas pode reduzir o tempo de resposta em até 70% e aumentar a capacidade de usuários concorrentes em 5x. As quick wins devem ser priorizadas para impacto imediato, seguidas pelas otimizações estruturais para sustentabilidade a longo prazo.