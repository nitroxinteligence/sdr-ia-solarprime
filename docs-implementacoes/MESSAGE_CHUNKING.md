# Sistema de Message Chunking

## Visão Geral

O sistema de Message Chunking divide mensagens longas em pedaços menores, criando uma conversação mais natural e humanizada no WhatsApp. Ao invés de enviar um grande bloco de texto, o sistema simula como uma pessoa real digitaria, enviando mensagens curtas e sequenciais.

## Como Funciona

### 1. Divisão Inteligente

O sistema analisa o texto e divide em pontos naturais:
- Final de sentenças (. ! ?)
- Preserva URLs completas
- Mantém abreviações intactas (Dr., Sr., etc.)
- Respeita listas numeradas
- Preserva emojis com pontuação

### 2. Probabilidade de Junção

Com base em uma probabilidade configurável (padrão: 60%), o sistema decide se deve juntar sentenças adjacentes ou mantê-las separadas. Isso cria variação natural no tamanho das mensagens.

### 3. Delays Dinâmicos

O tempo entre mensagens é calculado baseado em:
- Tamanho do texto (palavras por minuto)
- Tipo de conteúdo (perguntas, valores, explicações)
- Estágio da conversa
- Limites do WhatsApp (1-3 segundos)

### 4. Simulação de Digitação

Entre cada chunk, o sistema:
1. Mostra indicador de "digitando..."
2. Aguarda tempo proporcional ao conteúdo
3. Envia a mensagem
4. Pequena pausa antes do próximo chunk

## Configuração

Adicione ao seu `.env`:

```env
# Message Chunking Configuration
MESSAGE_CHUNKING_ENABLED=true          # Habilitar/desabilitar
CHUNK_JOIN_PROBABILITY=0.6             # Probabilidade de juntar (0.0-1.0)
CHUNK_MAX_WORDS=30                     # Máximo palavras por chunk
CHUNK_MIN_WORDS=3                      # Mínimo palavras por chunk
CHUNK_MAX_CHARS=1200                   # Máximo caracteres (WhatsApp: 1600)
CHUNK_TYPING_WORDS_PER_MINUTE=150      # Velocidade de digitação
CHUNK_READING_WORDS_PER_MINUTE=200     # Velocidade de leitura
```

## Ajustes por Estágio

O sistema ajusta automaticamente baseado no estágio da conversa:

### INITIAL_CONTACT (Saudação)
- Mais chunks (join_probability: 0.4)
- Chunks menores (max 20 palavras)
- Cria primeira impressão natural

### QUALIFICATION/DISCOVERY (Explicações)
- Menos chunks (join_probability: 0.7)
- Chunks maiores (max 35 palavras)
- Permite explicações mais fluidas

## Exemplo Prático

**Mensagem Original:**
```
Opa, tudo joia por aí? Que bom que você chamou! Aqui é a Helen Vieira, consultora especialista da Solar Prime Boa Viagem. Pra gente começar com o pé direito, como eu posso te chamar?
```

**Resultado com Chunking:**
```
[10:30:15] Helen: Opa, tudo joia por aí?
[digitando...]
[10:30:17] Helen: Que bom que você chamou!
[digitando...]
[10:30:19] Helen: Aqui é a Helen Vieira, consultora especialista da Solar Prime Boa Viagem.
[digitando...]
[10:30:21] Helen: Pra gente começar com o pé direito, como eu posso te chamar?
```

## Arquivos Principais

### `/agents/tools/message_chunker_tool.py`
- `chunk_message()`: Divide mensagens em chunks
- `analyze_message_for_chunking()`: Analisa estratégia ideal
- `calculate_typing_delay()`: Calcula delays de digitação
- `split_into_sentences()`: Divisão inteligente de sentenças

### `/services/whatsapp_service.py`
- `_send_chunked_messages()`: Envia mensagens em chunks
- Integração com Evolution API
- Gerenciamento de delays e typing

### `/agents/sdr_agent_v2.py`
- Integração das tools de chunking
- Metadata `use_chunking` em todas respostas

## Testes

Execute os testes para verificar o funcionamento:

```bash
# Teste básico do chunking
python test_message_chunking.py

# Teste de integração completa
python test_chunking_integration.py
```

## Desabilitar Chunking

Para desabilitar temporariamente:

1. No `.env`: `MESSAGE_CHUNKING_ENABLED=false`
2. Por mensagem: metadata `use_chunking: false`
3. Mensagens curtas (<100 chars) não são divididas

## Benefícios

1. **Conversação Natural**: Simula digitação humana real
2. **Melhor Engajamento**: Usuário tem tempo para processar
3. **Reduz Sobrecarga**: Evita blocos grandes de texto
4. **Flexibilidade**: Configurável por estágio/contexto

## Considerações

- WhatsApp limita mensagens a 1600 caracteres
- Delays muito longos podem frustrar usuários
- Balancear naturalidade com eficiência
- Monitorar métricas de engajamento