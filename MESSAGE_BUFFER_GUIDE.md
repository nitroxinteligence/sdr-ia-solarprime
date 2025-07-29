# Guia do Sistema de Buffer de Mensagens

## Visão Geral

O sistema de buffer de mensagens foi criado para resolver o problema de mensagens "picotadas" no WhatsApp, onde o usuário envia várias mensagens curtas em sequência. O sistema agrupa essas mensagens e as processa como um contexto único.

## Como Funciona

### 1. Detecção de Mensagens Consecutivas

Quando uma mensagem chega:
1. É adicionada a um buffer local (em memória)
2. Um timer é iniciado/resetado para aguardar mais mensagens
3. Se mais mensagens chegarem, o timer é resetado
4. Após o timeout, todas as mensagens são processadas juntas

### 2. Configurações

Adicione ao seu `.env`:

```env
# Buffer de Mensagens
MESSAGE_BUFFER_ENABLED=true          # Habilitar sistema de buffer
MESSAGE_BUFFER_TIMEOUT=8             # Tempo de espera em segundos
MESSAGE_BUFFER_MAX_MESSAGES=20       # Máximo de mensagens no buffer
MESSAGE_BUFFER_MIN_INTERVAL=0.5      # Intervalo mínimo entre mensagens
```

### 3. Fluxo de Processamento

```
Usuário envia: "Olá"
  ↓
Buffer: ["Olá"] - Timer: 8s
  ↓
Usuário envia: "Tudo bem?"
  ↓
Buffer: ["Olá", "Tudo bem?"] - Timer resetado: 8s
  ↓
Usuário envia: "Quero saber sobre energia solar"
  ↓
Buffer: ["Olá", "Tudo bem?", "Quero saber sobre energia solar"] - Timer resetado: 8s
  ↓
(Após 8 segundos sem novas mensagens)
  ↓
Agente processa: "Olá Tudo bem? Quero saber sobre energia solar"
  ↓
Resposta única e contextualizada
```

## Benefícios

### 1. Contexto Completo
- O agente recebe toda a mensagem do usuário
- Evita respostas fragmentadas ou duplicadas
- Melhora a qualidade da conversa

### 2. Economia de Recursos
- Uma única chamada à API de IA
- Menos processamento
- Respostas mais eficientes

### 3. Experiência Natural
- Simula conversação humana
- Aguarda o usuário terminar de digitar
- Responde de forma coerente

## Problemas Resolvidos

### Antes (Sem Buffer)
```
Usuário: "Olá"
Bot: "Olá! Como posso ajudar?"

Usuário: "Quero saber"
Bot: "Claro! O que você gostaria de saber?"

Usuário: "sobre energia solar"
Bot: "Ah, energia solar! É uma ótima escolha..."

(Respostas desconexas e repetitivas)
```

### Depois (Com Buffer)
```
Usuário: "Olá"
Usuário: "Quero saber"
Usuário: "sobre energia solar"

Bot: "Olá! Fico feliz em ajudar você com informações sobre energia solar. 
      É uma excelente escolha para economizar na conta de luz..."

(Resposta única e contextualizada)
```

## Implementação Técnica

### Arquitetura

1. **MessageBufferService** (`services/message_buffer_service.py`)
   - Gerencia buffers locais em memória
   - Controla timers por número de telefone
   - Processa callbacks quando o timeout expira

2. **WhatsAppService** (`services/whatsapp_service.py`)
   - Detecta novas mensagens
   - Adiciona ao buffer
   - Processa mensagens consolidadas

### Buffer Local

O sistema usa um dicionário em memória para armazenar mensagens:

```python
self._local_buffers = {
    "5511999999999": [
        {"content": "Olá", "timestamp": "..."},
        {"content": "Tudo bem?", "timestamp": "..."},
        {"content": "Quero saber sobre solar", "timestamp": "..."}
    ]
}
```

### Timer Management

- Cada número tem seu próprio timer
- Timer é resetado a cada nova mensagem
- Após timeout, processa todas as mensagens

## Testes

### Script de Teste

Execute o teste do buffer:

```bash
python test_message_buffer.py
```

O script simula o envio de múltiplas mensagens e verifica se são processadas juntas.

### Teste Manual via WhatsApp

1. Envie várias mensagens rapidamente:
   - "Olá"
   - "Tudo bem?"
   - "Quero informações"
   - "sobre energia solar"
   - "para minha casa"

2. Aguarde a resposta única do bot

3. Verifique nos logs se as mensagens foram bufferizadas

## Monitoramento

### Logs Importantes

```
INFO: Mensagem adicionada ao buffer local para 5511999999999. Total: 3
INFO: Timer criado para 5511999999999 - Aguardando 8s
INFO: Processando 3 mensagens bufferizadas de 5511999999999
```

### Métricas

O sistema rastreia:
- Quantidade de mensagens bufferizadas
- Tempo de processamento
- Taxa de sucesso

## Troubleshooting

### Buffer não está funcionando

1. Verifique se `MESSAGE_BUFFER_ENABLED=true`
2. Confirme o timeout não está muito baixo
3. Verifique os logs para erros

### Mensagens processadas individualmente

1. Aumente o `MESSAGE_BUFFER_TIMEOUT`
2. Verifique se as mensagens chegam dentro do intervalo
3. Confirme que o serviço está rodando

### Timeout muito longo

1. Reduza `MESSAGE_BUFFER_TIMEOUT` para 3-5 segundos
2. Considere o comportamento típico dos usuários

## Configurações Recomendadas

### Conversas Rápidas
```env
MESSAGE_BUFFER_TIMEOUT=5
MESSAGE_BUFFER_MAX_MESSAGES=10
```

### Conversas Detalhadas
```env
MESSAGE_BUFFER_TIMEOUT=8
MESSAGE_BUFFER_MAX_MESSAGES=20
```

### Alta Performance
```env
MESSAGE_BUFFER_TIMEOUT=3
MESSAGE_BUFFER_MAX_MESSAGES=5
```

## Integração com Outros Sistemas

### Chunking de Mensagens

O buffer trabalha em conjunto com o sistema de chunking:
1. Mensagens são bufferizadas
2. Processadas como contexto único
3. Resposta é dividida em chunks naturais

### Follow-up System

O follow-up é criado apenas após processar todas as mensagens bufferizadas.

### Analytics

Eventos especiais são rastreados:
- `buffered_messages_processed`
- Quantidade de mensagens
- Tempo de processamento