# 🧪 Testes do Sistema de Buffer de Mensagens

Este documento descreve os testes disponíveis para o sistema de buffer de mensagens do SDR IA SolarPrime.

## 📋 Pré-requisitos

1. **Redis instalado e rodando**:
   ```bash
   # Verificar se Redis está rodando
   redis-cli ping
   
   # Se não estiver, iniciar Redis
   redis-server
   ```

2. **Dependências Python instaladas**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Arquivo .env configurado** (para testes de integração):
   - `GEMINI_API_KEY` com API key válida
   - `REDIS_URL` ou configurações do Redis

## 🚀 Como Executar os Testes

### Método Simples (Recomendado)

```bash
# Na raiz do projeto
python run_buffer_tests.py
```

Este script oferece um menu interativo com as opções:
1. Teste básico do buffer
2. Teste de integração com SDR Agent V2
3. Executar todos os testes

### Método Manual

```bash
# Teste básico do buffer apenas
python tests/test_message_buffer.py

# Teste de integração (requer APIs configuradas)
python tests/test_buffer_integration.py
```

## 📊 Cenários de Teste

### 1. Teste Básico do Buffer (`test_message_buffer.py`)

#### Cenários Testados:
- **Mensagens Fragmentadas**: Simula usuário digitando várias mensagens curtas
- **Mensagens com Mídia**: Texto intercalado com imagens/documentos
- **Mensagens Rápidas**: Usuário ansioso enviando muitas mensagens rapidamente
- **Mensagens com Correção**: Usuário corrigindo informações anteriores

#### Funcionalidades Testadas:
- ✅ Adição de mensagens ao buffer
- ✅ Timer de 8 segundos resetando a cada nova mensagem
- ✅ Consolidação de múltiplas mensagens
- ✅ Processamento após timeout
- ✅ Status do buffer
- ✅ Processamento forçado
- ✅ Limpeza do buffer

### 2. Teste de Integração (`test_buffer_integration.py`)

#### Cenários Testados:
- **Fluxo de Qualificação Completo**: 
  - Identificação → Descoberta → Qualificação
  - Simula conversa real com cliente
  
- **Consulta Urgente**:
  - Múltiplas perguntas rápidas
  - Detecção de urgência
  
- **Mensagens com Mídia**:
  - Envio de conta de luz (imagem)
  - Processamento com AGnO Framework

#### Métricas de Performance:
- Tempo de resposta total
- Tempo médio por mensagem
- Verificação do limite de 30s
- Lead score e stage tracking

## 📈 Interpretando os Resultados

### Saída Esperada - Teste Básico

```
━━━ Cenário: Mensagens Fragmentadas ━━━
Telefone: 5511999999001
Total de mensagens: 5

→ Mensagem 1/5 adicionada ao buffer
  "Oi"
  Aguardando 0.5s...
→ Mensagem 2/5 adicionada ao buffer
  "Eu vi o anúncio de vocês"
  ...

⏳ Aguardando timeout do buffer (8s)...

✓ Buffer processado!
Mensagens consolidadas: 5

Texto consolidado:
"Oi Eu vi o anúncio de vocês sobre energia solar Queria saber mais informações Quanto custa?"
```

### Saída Esperada - Teste de Integração

```
🤖 TESTE DE INTEGRAÇÃO: BUFFER + SDR AGENT V2

📍 Primeiro contato
→ "Oi"
→ "Vi o anúncio de vocês"
→ "Sobre energia solar"

✓ Resposta do agente:
"Olá! 😊 Que bom que se interessou pela energia solar! Eu sou a Luna da SolarPrime. Como posso te chamar?"

Metadados:
- Estágio: IDENTIFICATION
- Lead Score: 10
- Tempo de resposta: 2.45s
- Mensagens bufferizadas: 3

Análise do Buffer:
- Fragmentado: Não
- Urgente: Não
- Tem perguntas: Não
```

## 🔍 Troubleshooting

### Redis não conecta
```bash
# Verificar se Redis está rodando
ps aux | grep redis

# Verificar configuração no .env
REDIS_URL=redis://localhost:6379
```

### Timeout nos testes
- Verifique se as API keys estão válidas
- Confirme que o Gemini API tem créditos
- Aumente o timeout em `MESSAGE_BUFFER_TIMEOUT` no .env

### Erro de importação
```bash
# Executar da raiz do projeto
cd /path/to/SDR-IA-SolarPrime-Python
python run_buffer_tests.py
```

## 📝 Logs

Os logs detalhados são salvos em:
```
tests/logs/
├── test_buffer_YYYY-MM-DD_HH-MM-SS.log
└── test_buffer_integration_YYYY-MM-DD_HH-MM-SS.log
```

## 🎯 Critérios de Sucesso

1. **Buffer Básico**:
   - ✅ Todas as mensagens são adicionadas ao buffer
   - ✅ Timer reseta corretamente
   - ✅ Processamento ocorre após 8 segundos
   - ✅ Conteúdo é consolidado corretamente

2. **Integração**:
   - ✅ Agente processa múltiplas mensagens como contexto único
   - ✅ Tempo de resposta < 30 segundos
   - ✅ Detecção correta de intenções (urgência, dúvida, interesse)
   - ✅ Stage progression funciona corretamente
   - ✅ Lead score é calculado adequadamente

## 🚧 Próximos Passos

Após executar os testes com sucesso:

1. **Configurar Supabase** com connection string correta
2. **Adicionar OpenAI API key** com créditos para embeddings
3. **Testar com Evolution API** real (webhook do WhatsApp)
4. **Monitorar performance** em produção