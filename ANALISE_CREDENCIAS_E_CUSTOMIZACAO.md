
# Análise de Credenciais e Customização do Agente SDR IA

Este relatório detalha todas as credenciais necessárias para o funcionamento do sistema e as variáveis de ambiente que permitem a personalização do comportamento do agente.

---

## 1. Análise de Credenciais Essenciais

A seguir estão as credenciais necessárias para o funcionamento completo do sistema, separadas por serviço.

### 1.1. OpenAI
- **Variável**: `OPENAI_API_KEY`
- **Utilização**: Chave de API para acessar os modelos da OpenAI, como o `o3-mini`, que é utilizado como um modelo de *fallback* caso o Gemini da Google apresente instabilidade.
- **Status**: **CONFIGURADA**

### 1.2. Google (Gemini e Calendar)
- **Variável**: `GOOGLE_API_KEY`
- **Utilização**: Chave de API para o modelo de linguagem Gemini, o modelo principal do agente.
- **Status**: **CONFIGURADA**

- **Variável**: `GOOGLE_OAUTH_CLIENT_ID`
- **Utilização**: ID do Cliente OAuth para autenticação com a API do Google Calendar. Essencial para agendamento de reuniões.
- **Status**: **CONFIGURADA**

- **Variável**: `GOOGLE_OAUTH_CLIENT_SECRET`
- **Utilização**: Chave secreta do Cliente OAuth para o Google Calendar.
- **Status**: **CONFIGURADA**

- **Variável**: `GOOGLE_OAUTH_REFRESH_TOKEN`
- **Utilização**: Token de atualização para manter a autenticação com o Google Calendar sem a necessidade de interação manual.
- **Status**: **CONFIGURADA**

- **Variável**: `GOOGLE_CALENDAR_ID`
- **Utilização**: ID da agenda do Google a ser utilizada para o agendamento.
- **Status**: **CONFIGURADA**

### 1.3. Evolution API (WhatsApp)
- **Variável**: `EVOLUTION_API_URL`
- **Utilização**: URL da instância da Evolution API para conexão com o WhatsApp.
- **Status**: **CONFIGURADA**

- **Variável**: `EVOLUTION_API_KEY`
- **Utilização**: Chave de API para autenticação com a Evolution API.
- **Status**: **CONFIGURADA**

- **Variável**: `EVOLUTION_INSTANCE_NAME`
- **Utilização**: Nome da instância na Evolution API.
- **Status**: **CONFIGURADA**

### 1.4. Supabase (Banco de Dados)
- **Variável**: `SUPABASE_URL`
- **Utilização**: URL do seu projeto Supabase.
- **Status**: **CONFIGURADA**

- **Variável**: `SUPABASE_ANON_KEY`
- **Utilização**: Chave de API anônima do Supabase.
- **Status**: **CONFIGURADA**

- **Variável**: `SUPABASE_SERVICE_KEY`
- **Utilização**: Chave de serviço do Supabase, que permite acesso total ao banco de dados.
- **Status**: **CONFIGURADA**

### 1.5. Redis (Cache e Filas)
- **Variável**: `REDIS_URL`
- **Utilização**: URL de conexão com o servidor Redis.
- **Status**: **CONFIGURADA**

- **Variável**: `REDIS_HOST`
- **Utilização**: Endereço do servidor Redis.
- **Status**: **CONFIGURADA**

- **Variável**: `REDIS_PORT`
- **Utilização**: Porta do servidor Redis.
- **Status**: **CONFIGURADA**

- **Variável**: `REDIS_PASSWORD`
- **Utilização**: Senha para autenticação no Redis.
- **Status**: **CONFIGURADA**

### 1.6. Kommo CRM
- **Variável**: `KOMMO_LONG_LIVED_TOKEN`
- **Utilização**: Token de longa duração para autenticação com a API do Kommo CRM.
- **Status**: **CONFIGURADA**

- **Variável**: `KOMMO_BASE_URL`
- **Utilização**: URL base da sua instância do Kommo CRM.
- **Status**: **CONFIGURADA**

- **Variável**: `KOMMO_PIPELINE_ID`
- **Utilização**: ID do funil de vendas no Kommo onde os leads serão gerenciados.
- **Status**: **CONFIGURADA**

---

## 2. Guia de Customização do Agente via `.env`

As seguintes variáveis no arquivo `.env` permitem que você personalize o comportamento do agente de forma flexível e sem a necessidade de alterar o código.

### 2.1. Comportamento da IA e Modelos
- **`PRIMARY_AI_MODEL`**: Define o modelo de linguagem principal.
  - **Uso**: `PRIMARY_AI_MODEL=gemini-1.5-pro`
  - **Impacto**: Altera o cérebro do agente. `gemini-1.5-pro` é mais poderoso, enquanto `gemini-1.5-flash` é mais rápido.

- **`ENABLE_MODEL_FALLBACK`**: Ativa ou desativa o uso do modelo da OpenAI (`o3-mini`) como backup.
  - **Uso**: `ENABLE_MODEL_FALLBACK=true` ou `false`
  - **Impacto**: `true` aumenta a resiliência do agente, que continuará funcionando mesmo com instabilidade no Gemini.

- **`AI_TEMPERATURE`**: Controla a criatividade das respostas.
  - **Uso**: `AI_TEMPERATURE=0.7`
  - **Impacto**: Valores mais altos (ex: 0.9) geram respostas mais criativas e variadas. Valores mais baixos (ex: 0.3) tornam as respostas mais diretas e previsíveis.

- **`AI_MAX_TOKENS`**: Define o tamanho máximo da resposta do modelo.
  - **Uso**: `AI_MAX_TOKENS=4096`
  - **Impacto**: Limita o comprimento das respostas, útil para controlar custos e complexidade.

### 2.2. Humanização e Timing das Respostas
- **`ENABLE_TYPING_SIMULATION`**: Ativa ou desativa a simulação de "digitando...".
  - **Uso**: `ENABLE_TYPING_SIMULATION=true` ou `false`
  - **Impacto**: `true` torna a interação mais humana. `false` faz com que as respostas sejam enviadas instantaneamente.

- **`TYPING_DURATION_SHORT`, `TYPING_DURATION_MEDIUM`, `TYPING_DURATION_LONG`**: Controla a duração da simulação de digitação para respostas curtas, médias e longas.
  - **Uso**: `TYPING_DURATION_MEDIUM=4.0` (em segundos)
  - **Impacto**: Permite ajustar a percepção de velocidade e naturalidade do agente.

- **`RESPONSE_DELAY_MIN`, `RESPONSE_DELAY_MAX`**: Define o intervalo de tempo (em segundos) que o agente espera antes de responder.
  - **Uso**: `RESPONSE_DELAY_MIN=1.5`, `RESPONSE_DELAY_MAX=3.0`
  - **Impacto**: Um delay aleatório dentro deste intervalo torna a interação menos robótica.

### 2.3. Funcionalidades do Agente (Feature Flags)
Você pode ligar ou desligar módulos inteiros do agente:

- **`ENABLE_CONTEXT_ANALYSIS`**: Ativa a análise de contexto da conversa.
- **`ENABLE_SENTIMENT_ANALYSIS`**: Ativa a análise de sentimento.
- **`ENABLE_MULTIMODAL_ANALYSIS`**: Permite que o agente entenda imagens e áudios.
- **`ENABLE_VOICE_MESSAGE_TRANSCRIPTION`**: Ativa a transcrição de mensagens de voz.
- **`ENABLE_CRM_INTEGRATION`**: Ativa a integração com o Kommo CRM.
- **`ENABLE_KNOWLEDGE_BASE`**: Permite que o agente consulte a base de conhecimento.
- **`ENABLE_FOLLOW_UP_AUTOMATION`**: Ativa o sistema de follow-ups automáticos.

- **Uso**: `ENABLE_MULTIMODAL_ANALYSIS=true` ou `false`
- **Impacto**: Desativar uma funcionalidade pode simplificar o fluxo do agente ou reduzir custos, enquanto ativá-la aumenta a sua capacidade.

### 2.4. Mensagens e Comunicação
- **`ENABLE_MESSAGE_SPLITTER`**: Ativa a quebra de mensagens longas em partes menores.
  - **Uso**: `ENABLE_MESSAGE_SPLITTER=true`
  - **Impacto**: Melhora a legibilidade no WhatsApp.

- **`MESSAGE_MAX_LENGTH`**: Define o tamanho máximo de cada parte da mensagem.
  - **Uso**: `MESSAGE_MAX_LENGTH=200`
  - **Impacto**: Mensagens mais curtas parecem mais naturais em conversas de WhatsApp.

- **`ENABLE_MESSAGE_BUFFER`**: Agrupa mensagens recebidas em um curto período de tempo para processá-las de uma só vez.
  - **Uso**: `ENABLE_MESSAGE_BUFFER=true`
  - **Impacto**: Evita que o agente responda a cada mensagem individualmente quando o usuário envia várias em sequência.

- **`MESSAGE_BUFFER_TIMEOUT`**: Tempo (em segundos) que o buffer aguarda por novas mensagens antes de processar.
  - **Uso**: `MESSAGE_BUFFER_TIMEOUT=5.0`
  - **Impacto**: Um timeout maior agrupa mais mensagens, enquanto um menor torna o agente mais reativo.

### 2.5. Horário de Funcionamento
- **`BUSINESS_HOURS_START`** e **`BUSINESS_HOURS_END`**: Define o horário de funcionamento do agente.
  - **Uso**: `BUSINESS_HOURS_START=08:00`, `BUSINESS_HOURS_END=20:00`
  - **Impacto**: O agente pode ter comportamentos diferentes fora do horário comercial, como agendar follow-ups para o dia seguinte.

- **`TIMEZONE`**: Define o fuso horário do agente.
  - **Uso**: `TIMEZONE=America/Sao_Paulo`
  - **Impacto**: Garante que o horário de funcionamento e os agendamentos estejam corretos.

---

Este relatório deve fornecer uma visão clara de como o seu sistema está configurado e como você pode personalizá-lo facilmente. Se tiver mais alguma dúvida, estou à disposição!
