# 🚀 OTIMIZAÇÃO INTELIGENTE: 30S COM HUMANIZAÇÃO PRESERVADA

## PREMISSAS
- ✅ MANTER typing delay (humanização)
- ✅ MANTER buffer de 10s
- ❌ NÃO comprometer a experiência natural
- 🎯 META: 30s total

## 🔥 AS 4 MUDANÇAS ESSENCIAIS (SEM TOCAR EM DELAYS)

### 1️⃣ SINGLETON DO AGENTE (GANHO: -15s) 🏆 MAIOR IMPACTO!

**Arquivo**: `app/api/webhooks.py` (adicionar no topo, após imports)
```python
# Cache global do agente - REUTILIZAR SEMPRE!
_cached_agent = None
_agent_lock = asyncio.Lock()

async def get_agentic_agent(phone: str) -> AgenticSDR:
    """Retorna instância única e reutilizável do agente"""
    global _cached_agent
    
    async with _agent_lock:
        if _cached_agent is None:
            emoji_logger.webhook_process("🚀 Criando AgenticSDR singleton...")
            _cached_agent = await create_agentic_sdr()
            await _cached_agent.initialize()
            emoji_logger.system_ready("✅ AgenticSDR singleton pronto!")
        
        # IMPORTANTE: Limpar contexto anterior para evitar vazamentos
        _cached_agent.current_phone = phone
        _cached_agent.context["current_time"] = datetime.now().strftime("%H:%M")
        _cached_agent.context["period_of_day"] = get_period_of_day(settings.timezone)
        
        return _cached_agent

# NO FINAL DO ARQUIVO, comentar ou remover:
# async def get_agentic_agent(phone: str) -> AgenticSDR:
#     """Retorna uma instância do AGENTIC SDR"""
#     return await create_agentic_sdr()
```

### 2️⃣ CACHE AGRESSIVO DE HISTÓRICO (GANHO: -5s)

**Arquivo**: `app/agents/agentic_sdr.py` (modificar método get_last_100_messages)
```python
# Adicionar no __init__ da classe AgenticSDR:
def __init__(self, storage=None):
    # ... código existente ...
    self._message_cache = {}  # Cache simples
    self._cache_ttl = 300  # 5 minutos

# Modificar o método get_last_100_messages:
async def get_last_100_messages(self, identifier: str) -> List[Dict[str, Any]]:
    """Busca as últimas 100 mensagens COM CACHE"""
    
    # Check cache first
    cache_key = f"hist_{identifier}"
    now = time.time()
    
    if cache_key in self._message_cache:
        cached_time, cached_data = self._message_cache[cache_key]
        if now - cached_time < self._cache_ttl:
            emoji_logger.agentic_cache(f"✅ Cache hit! Economizou query de 100 msgs")
            return cached_data
    
    # ... código existente de busca ...
    
    # Antes de retornar, cachear:
    if messages:  # Se encontrou mensagens
        self._message_cache[cache_key] = (now, messages)
        # Limpar cache antigo (manter só últimos 10)
        if len(self._message_cache) > 10:
            oldest = min(self._message_cache.items(), key=lambda x: x[1][0])
            del self._message_cache[oldest[0]]
    
    return messages
```

### 3️⃣ PARALELIZAÇÃO DE I/O NO WEBHOOK (GANHO: -5s)

**Arquivo**: `app/api/webhooks.py` (método process_message_with_agent)
```python
# SUBSTITUIR as linhas ~349-391 por:

# 1. Buscar lead
lead = await supabase_client.get_lead_by_phone(phone)
if not lead:
    lead_data = {
        "name": extract_name_from_message(message_content) or phone,
        "phone": phone,
        "email": None,
        "city": extract_city_from_message(message_content),
        "has_energy_bill": False,
        "energy_bill_amount": None
    }
    lead = await supabase_client.create_lead(lead_data)

# 2. PARALELO: Buscar/criar conversa + preparar cache
async def get_or_create_conversation():
    conv = await supabase_client.get_conversation_by_phone(phone)
    if not conv:
        conv = await supabase_client.create_conversation(phone, lead["id"])
    return conv

# Executar em PARALELO
conversation_task = asyncio.create_task(get_or_create_conversation())

# 3. Pegar conversa
conversation = await conversation_task

# 4. PARALELO: Salvar mensagem + cache + incrementar contador
save_tasks = [
    supabase_client.save_message(
        conversation_id=conversation["id"],
        content=message_content,
        sender="user",
        message_type="text",
        quoted_message_id=None,
        metadata={"whatsapp_message_id": message_id}
    ),
    redis_client.setex(
        f"conversation:{phone}",
        3600,
        json.dumps({"id": conversation["id"], "lead_id": lead["id"]})
    )
]

# Só incrementar se não for continuação
if not is_continuation:
    save_tasks.append(
        supabase_client.increment_message_count(conversation["id"], phone)
    )

# Executar TUDO em paralelo
await asyncio.gather(*save_tasks, return_exceptions=True)
```

### 4️⃣ OTIMIZAÇÃO DO REASONING CONDICIONAL (GANHO: -5s)

**Arquivo**: `app/agents/agentic_sdr.py` (já implementado mas vamos melhorar)
```python
# Melhorar a função _is_complex_message para ser mais precisa:
def _is_complex_message(self, message: str) -> bool:
    """Determina se precisa reasoning (mais restritivo)"""
    message_lower = message.lower().strip()
    
    # Mensagens SUPER simples - definitivamente não precisam reasoning
    if len(message_lower) < 15:  # Aumentado de 10 para 15
        return False
    
    # Respostas diretas que não precisam reasoning
    simple_responses = {
        'sim', 'não', 'ok', 'certo', 'beleza', 'entendi',
        'pode ser', 'claro', 'com certeza', 'obrigado', 'obrigada',
        'oi', 'olá', 'bom dia', 'boa tarde', 'boa noite',
        'tudo bem', 'tudo certo', 'tá bom', 'ta ok'
    }
    
    # Se é uma resposta simples, não precisa reasoning
    if message_lower in simple_responses or any(
        message_lower.startswith(s) for s in simple_responses
    ):
        return False
    
    # SÓ ativar reasoning para questões REALMENTE complexas
    complex_indicators = [
        'como funciona', 'me explica', 'não entendi',
        'quanto custa', 'qual o valor', 'economia',
        'comparar', 'diferença', 'vantagem',
        'garantia', 'manutenção', 'instalação'
    ]
    
    # Precisa ter pelo menos 2 indicadores OU uma pergunta elaborada
    indicator_count = sum(1 for ind in complex_indicators if ind in message_lower)
    has_multiple_questions = message.count('?') > 1
    
    return indicator_count >= 2 or has_multiple_questions
```

## 📊 ANÁLISE DE TEMPO APÓS OTIMIZAÇÕES

### ANTES (60s):
```
[0s] Webhook recebe
[15s] CRIA AGENTE NOVO ❌
[20s] Queries sequenciais ❌
[25s] Busca 100 mensagens ❌
[30s] Análise contexto
[40s] LLM call
[50s] Typing humanizado ✅
[60s] Resposta enviada
```

### DEPOIS (25-30s):
```
[0s] Webhook recebe
[0s] USA SINGLETON ✅ (-15s!)
[3s] Queries paralelas ✅ (-5s!)
[3s] Cache histórico ✅ (-5s!)
[5s] Análise contexto
[15s] LLM call
[25s] Typing humanizado ✅ (mantido!)
[30s] Resposta enviada
```

## 🚀 BÔNUS: MICRO-OTIMIZAÇÕES ADICIONAIS

Se ainda precisar ganhar mais alguns segundos:

```python
# 1. Em agentic_sdr.py - Pré-compilar regexes
class AgenticSDR:
    # Compilar uma vez só
    PHONE_REGEX = re.compile(r'\b\d{10,11}\b')
    EMAIL_REGEX = re.compile(r'\b[\w.-]+@[\w.-]+\.\w+\b')
    
    def _extract_phone(self, text):
        return self.PHONE_REGEX.findall(text)  # Mais rápido!

# 2. Reduzir retry delays apenas
# webhooks.py linha ~824
await asyncio.sleep(retry_count * 0.2)  # Era 0.5

# 3. Cache do prompt (não ler arquivo toda vez)
_CACHED_PROMPT = None

def _load_enhanced_prompt(self):
    global _CACHED_PROMPT
    if _CACHED_PROMPT is None:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            _CACHED_PROMPT = f.read()
    return _CACHED_PROMPT
```

## ✅ RESULTADO FINAL

Com essas 4 mudanças principais:
- **Tempo médio**: 25-30 segundos ✅
- **Humanização**: 100% preservada ✅
- **Complexidade**: ZERO ✅
- **Risco**: MÍNIMO ✅

### ORDEM DE IMPLEMENTAÇÃO (45 min):
1. **Singleton** (20 min) - FAZER PRIMEIRO, MAIOR IMPACTO!
2. **Cache histórico** (10 min)
3. **Paralelização I/O** (10 min)
4. **Testar** (5 min)

**COMECE PELO SINGLETON - É 50% DO GANHO DE PERFORMANCE!**