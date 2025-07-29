# Correções do Sistema de Buffer de Mensagens

## Problema Identificado

O sistema estava processando mensagens individualmente ao invés de aguardar o buffer completo, causando múltiplas respostas do agente para o mesmo conjunto de mensagens do usuário.

### Evidências do Problema:
1. **Log mostrava**: "Processando 1 mensagens do buffer" quando havia múltiplas mensagens
2. **Múltiplos PIDs**: Servidor rodando com workers 8 e 9 simultaneamente
3. **Respostas duplicadas**: Agente respondia 3 vezes para o mesmo usuário

## Correções Implementadas

### 1. MessageBufferService - Prevenção de Condições de Corrida

#### Adicionado Sistema de Locks e Flags:
```python
# Novos atributos adicionados na classe
self._locks: Dict[str, asyncio.Lock] = {}  # Lock por telefone
self._processing: Dict[str, bool] = {}    # Flag indicando processamento ativo
```

#### Proteção no Método add_message:
- Lock assíncrono para garantir operações atômicas
- Verificação se buffer já está sendo processado
- Logs detalhados do estado do buffer

#### Melhorias no Timer:
- Verificação dupla antes de processar
- Processamento em task separada com limpeza de flags
- Melhor tratamento de cancelamento

### 2. Configuração de Worker Único

#### Variável de Ambiente:
```env
UVICORN_WORKERS=1  # Evita problemas de concorrência
```

#### Script de Inicialização:
- Criado `scripts/start_server.sh` com configuração adequada
- Dockerfile atualizado para usar variável de ambiente
- Documentação atualizada com comando correto

### 3. Logs Detalhados para Debug

#### MessageBufferService:
- Log quando timer é criado/cancelado
- Estado do buffer antes/depois de operações
- Número de mensagens no buffer

#### WhatsAppService:
- Status do buffer antes de adicionar mensagem
- Callback do buffer sendo acionado
- Conteúdo consolidado sendo enviado ao agente

#### Webhook:
- Detalhes de cada mensagem recebida
- ID, conteúdo e origem das mensagens

## Como o Sistema Funciona Agora

### Fluxo Correto:
1. **Primeira mensagem** chega → Buffer iniciado, timer de 8s começa
2. **Segunda mensagem** chega → Timer resetado, mensagem adicionada ao buffer
3. **Terceira mensagem** chega → Timer resetado novamente
4. **Quarta mensagem** chega → Timer resetado
5. **Após 8s sem novas mensagens** → Todas processadas juntas
6. **Agente responde UMA vez** com contexto completo

### Proteções Implementadas:
- **Lock por telefone**: Evita condições de corrida
- **Flag de processamento**: Previne processamento duplicado
- **Worker único**: Elimina concorrência entre processos
- **Logs detalhados**: Facilita debug de problemas futuros

## Configurações Recomendadas

### .env:
```env
# Buffer de Mensagens
MESSAGE_BUFFER_ENABLED=true
MESSAGE_BUFFER_TIMEOUT=8.0      # Aguarda 8 segundos
MESSAGE_BUFFER_MAX_MESSAGES=20  # Máximo antes de forçar processamento

# Servidor
UVICORN_WORKERS=1               # IMPORTANTE: Apenas 1 worker
```

### Comando de Inicialização:
```bash
# Desenvolvimento
./scripts/start_server.sh

# Produção
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## Monitoramento

### Logs para Acompanhar:
- `📥 Nova mensagem de`: Entrada de mensagem
- `✅ Mensagem adicionada ao buffer`: Buffer funcionando
- `🔄 Iniciando processamento de X mensagens`: Processamento consolidado
- `💬 Agente gerou resposta`: Resposta única enviada

### Indicadores de Problema:
- "Processando 1 mensagens" quando esperava múltiplas
- "Buffer já está sendo processado" frequente
- Múltiplas respostas do agente para mesmo usuário

## Próximos Passos

1. **Testes Unitários**: Validar cenários de concorrência
2. **Métricas**: Dashboard com estatísticas do buffer
3. **Ajuste Fino**: Otimizar timeout baseado em uso real