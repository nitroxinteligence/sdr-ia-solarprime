# 📘 Guia de Integração - Typing Controller

## Arquitetura Modular para Controle de Typing

### 🎯 Objetivo
Resolver definitivamente o problema de typing aparecendo quando não deveria, usando uma arquitetura **SIMPLES**, **MODULAR** e **TESTÁVEL**.

### 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Typing Controller                      │
│                  (Ponto Único de Decisão)                │
├─────────────────────────────────────────────────────────┤
│ Responsabilidades:                                       │
│ • Decidir QUANDO mostrar typing (baseado em contexto)   │
│ • Calcular duração apropriada                           │
│ • Executar typing via Evolution API                     │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
   ┌────┴─────┐                         ┌──────┴──────┐
   │ Webhooks │                         │   Agente    │
   └──────────┘                         └─────────────┘
```

### 🔧 Como Integrar

#### 1. **No webhook (process_message_with_agent)**

```python
# app/api/webhooks.py
from app.services.typing_controller import get_typing_controller, TypingContext

async def process_message_with_agent(
    phone: str,
    message_content: str,
    original_message: Dict[str, Any],
    message_id: str
):
    # ... código existente ...
    
    # ANTES de processar com o agente, notificar que está pensando
    typing_controller = get_typing_controller(evolution_client)
    await typing_controller.notify_agent_thinking(phone)
    
    # Processar com o agente
    response = await agentic.process(
        phone_number=phone,
        message=message_content,
        media_data=media_data,
        lead_data=lead,
        conversation_id=conversation["id"]
    )
    
    # NÃO precisa se preocupar com typing ao enviar resposta
    # O controller já cuidou disso ANTES
```

#### 2. **No Evolution Client (remover lógica duplicada)**

```python
# app/integrations/evolution.py
async def send_text_message(
    self,
    phone: str,
    message: str,
    delay: Optional[float] = None,
    simulate_typing: bool = True  # DEPRECADO - não usar mais
):
    # REMOVER toda lógica de typing daqui
    # Apenas enviar a mensagem
    
    payload = {
        "number": phone,
        "text": message,
        "delay": int(settings.delay_between_messages * 1000)
    }
    
    response = await self._make_request(
        "post",
        f"/message/sendText/{self.instance_name}",
        json=payload
    )
    # ...
```

### 📋 Regras de Negócio

#### Contextos de Typing:

1. **USER_MESSAGE**: Usuário enviando mensagem → **NUNCA** mostrar typing
2. **AGENT_THINKING**: Agente processando/pensando → **SEMPRE** mostrar typing
3. **SYSTEM_MESSAGE**: Mensagens do sistema → **NUNCA** mostrar typing

#### Fluxo Correto:

```
1. Usuário envia mensagem
   └─> NÃO mostrar typing

2. Sistema recebe e processa
   └─> Mostrar typing IMEDIATAMENTE (agente pensando)

3. Agente gera resposta
   └─> Typing já está ativo

4. Sistema envia resposta
   └─> Typing para automaticamente
```

### 🧪 Como Testar

```bash
# Rodar testes unitários
pytest tests/test_typing_controller.py -v

# Teste manual
1. Desabilitar typing globalmente:
   - Setar enable_typing_simulation = False no config
   - Verificar que NUNCA aparece typing

2. Habilitar typing:
   - Setar enable_typing_simulation = True
   - Enviar mensagem como usuário
   - Verificar que typing aparece APENAS quando agente responde
```

### ✅ Vantagens da Arquitetura

1. **SOLID**:
   - **S**: TypingController tem UMA responsabilidade
   - **O**: Extensível para novos contextos sem modificar código existente
   - **L**: TypingContext pode ser estendido
   - **I**: Interface simples e focada
   - **D**: Depende de abstração (evolution_client)

2. **DRY**: Lógica de typing em UM lugar apenas

3. **KISS**: Solução mais simples possível que resolve o problema

4. **Testável**: 100% de cobertura com testes unitários

5. **Manutenível**: Fácil entender, modificar e debugar

### 🚀 Próximos Passos

1. Integrar o TypingController no código existente
2. Remover TODA lógica de typing duplicada
3. Rodar testes para garantir funcionamento
4. Monitorar logs para confirmar comportamento correto

### 📊 Métricas de Sucesso

- ✅ Typing aparece APENAS quando agente está respondendo
- ✅ Zero ocorrências de typing quando usuário envia mensagem
- ✅ 100% de consistência no comportamento
- ✅ Código 70% mais simples e manutenível