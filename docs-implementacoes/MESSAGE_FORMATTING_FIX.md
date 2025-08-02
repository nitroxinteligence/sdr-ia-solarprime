# Correções de Formatação de Mensagens

## Problemas Identificados e Resolvidos

### 1. **Chunking Inadequado**
**Problema**: Mensagens sendo quebradas em vírgulas aleatoriamente
- Exemplo: "Ótimo. Agora com sua fatura em mãos e sabendo como me dirigir a você,"

**Solução Implementada**:
- Removida a vírgula da lista de pontos de quebra em `optimize_chunk_sizes()`
- Criada função `improve_chunk_splitting()` que junta chunks muito curtos
- Implementada lógica para detectar quebras naturais (parágrafos, listas)

### 2. **Pontuação Incorreta**
**Problema**: Dois pontos ":" precisavam virar reticências "..."
- Exemplo: "vamos ao que interessa:" → "vamos ao que interessa..."

**Solução Implementada**:
- Regex em `format_message_for_whatsapp()` que converte `:` seguido de espaço ou fim de linha para `...`
- Tratamento especial para casos como `**Importante:**` → `*Importante...*`

### 3. **Formatação de Negrito**
**Problema**: Usando formato Markdown `**texto**` ao invés do formato WhatsApp `*texto*`

**Solução Implementada**:
- Conversão automática de `**texto**` para `*texto*` em `format_message_for_whatsapp()`
- Conversão de headers Markdown (###) para negrito WhatsApp

## Arquivos Modificados

1. **`utils/message_formatter.py`** (NOVO)
   - Função `format_message_for_whatsapp()` - formatação principal
   - Função `improve_chunk_splitting()` - melhoria de chunks
   - Função `should_use_natural_breaks()` - detecção de quebras naturais

2. **`agents/tools/message_chunker_tool.py`**
   - Importação das novas funções de formatação
   - Aplicação de formatação antes do chunking
   - Remoção de vírgula como ponto de quebra
   - Integração com quebras naturais

3. **`services/whatsapp_service.py`**
   - Importação de `format_message_for_whatsapp()`
   - Aplicação de formatação em todos os pontos de envio:
     - `_send_chunked_messages()` - linha 399
     - Mensagem única - linha 311
     - `send_message()` - linha 536
     - Mensagens bufferizadas - linha 748

## Como Funciona

1. **Antes do Chunking**: A mensagem passa por `format_message_for_whatsapp()` que:
   - Converte `**texto**` → `*texto*`
   - Converte `:` (fim de frase) → `...`
   - Remove hífens desnecessários
   - Converte headers Markdown

2. **Durante o Chunking**: 
   - Verifica quebras naturais (parágrafos, listas)
   - Evita quebrar em vírgulas
   - Junta chunks muito curtos

3. **Depois do Chunking**: Cada chunk passa novamente pela formatação para garantir consistência

## Resultados

- ✅ Negrito corretamente formatado para WhatsApp
- ✅ Dois pontos convertidos para reticências
- ✅ Chunks mais naturais, sem quebras em vírgulas
- ✅ Mensagens com aparência mais profissional e natural

## Configuração

As seguintes variáveis de ambiente controlam o chunking:
- `MESSAGE_CHUNKING_ENABLED` - Ativa/desativa chunking (padrão: true)
- `CHUNK_JOIN_PROBABILITY` - Probabilidade de juntar sentenças (padrão: 0.6)
- `CHUNK_MAX_WORDS` - Máximo de palavras por chunk (padrão: 30)
- `CHUNK_MAX_CHARS` - Máximo de caracteres por chunk (padrão: 1200)