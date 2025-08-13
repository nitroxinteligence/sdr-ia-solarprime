# Documentação do Sistema de Transbordo (Handoff)

## 1. Visão Geral

O sistema de transbordo foi projetado para gerenciar a transição de conversas entre o agente de IA e os atendentes humanos de forma fluida e segura. Ele garante que o agente de IA pause ou cesse completamente suas interações quando um humano assume o controle, evitando respostas duplicadas ou conflitantes.

O sistema opera com base em duas regras principais:

1.  **Pausa Automática por Interação Humana:** Se qualquer membro da equipe humana interagir com um lead no Kommo CRM, o agente de IA é automaticamente pausado por 24 horas para aquele lead específico.
2.  **Bloqueio por Estágio no Pipeline:** Se um lead for movido para o estágio "Atendimento Humano" no pipeline do Kommo, o agente de IA é permanentemente bloqueado de interagir com esse lead, a menos que o lead seja movido para outro estágio.

## 2. Funcionalidades

### Pausa Automática de 24 Horas

- **Gatilho:** Uma nota sendo adicionada ao card do lead no Kommo por qualquer usuário que **não seja** o próprio agente de IA.
- **Ação:** O sistema registra um estado de "pausa" para o lead no Redis com uma duração configurável (padrão de 24 horas).
- **Efeito:** Enquanto a pausa estiver ativa, o agente de IA ignorará todas as mensagens recebidas daquele lead. A pausa é automaticamente removida após o tempo de expiração.

### Bloqueio por Estágio "Atendimento Humano"

- **Gatilho:** O card de um lead ser movido para o estágio "Atendimento Humano" no pipeline de vendas do Kommo.
- **Ação:** O sistema verifica o estágio do lead antes de cada processamento de mensagem.
- **Efeito:** Se o lead estiver no estágio de atendimento humano, o agente de IA é permanentemente impedido de enviar qualquer mensagem. O bloqueio só é removido se o lead for movido para um estágio diferente.

## 3. Configuração

Para que o sistema de transbordo funcione corretamente, as seguintes variáveis de ambiente devem ser configuradas no seu arquivo `.env`:

```env
# Define por quantas horas o agente deve pausar após uma interação humana.
HUMAN_INTERVENTION_PAUSE_HOURS=24

# O ID do pipeline no Kommo que contém o estágio de atendimento humano.
KOMMO_HUMAN_HANDOFF_PIPELINE_ID=11672895

# O ID do estágio (card) "Atendimento Humano" dentro do pipeline acima.
KOMMO_HUMAN_HANDOFF_STAGE_ID=89709599

# O ID do usuário que representa o agente de IA no Kommo.
# Usado para diferenciar interações humanas das ações do próprio agente.
KOMMO_AGENT_USER_ID=11031887
```

**Como obter os IDs do Kommo:**

-   `PIPELINE_ID` e `STAGE_ID`: Abra o pipeline no Kommo. O ID do pipeline estará na URL (`.../leads/pipeline/{PIPELINE_ID}`). Para obter o ID do estágio, use a API do Kommo para listar os estágios do pipeline ou inspecione os elementos da interface web.
-   `USER_ID`: Vá para Configurações > Usuários no Kommo, selecione o usuário do agente e encontre o ID na URL ou através da API.

## 4. Fluxo de Trabalho Técnico

### 4.1. Detecção de Interação Humana e Pausa

1.  **Webhook do Kommo:** Um atendente humano adiciona uma nota a um lead no Kommo CRM.
2.  **Evento:** O Kommo dispara um webhook do tipo `note_added` para o endpoint `/api/kommo/events` da nossa aplicação.
3.  **Análise do Payload:** A aplicação recebe o webhook e analisa o payload JSON. Ela extrai o `created_by` (ID do usuário que criou a nota) e o `entity_id` (ID do lead).
4.  **Verificação de Usuário:** O `created_by` é comparado com o `KOMMO_AGENT_USER_ID`.
5.  **Ação de Pausa:** Se os IDs forem diferentes, o sistema conclui que a interação foi humana.
    - Ele faz uma chamada à API do Kommo para obter o número de telefone do lead usando o `entity_id`.
    - Em seguida, chama a função `redis_client.set_human_handoff_pause()`, que cria uma chave no Redis (ex: `lead:pause:5511999999999`) com um TTL (Time-To-Live) de 24 horas.

### 4.2. Processamento de Mensagens e Lógica de Bloqueio

1.  **Mensagem Recebida:** O sistema recebe uma nova mensagem do WhatsApp através do endpoint `/api/webhooks/whatsapp/messages-upsert`.
2.  **Início do Processamento:** A função `process_new_message` é acionada.
3.  **Ponto de Controle:** Antes de chamar o `AgenticSDR` para gerar uma resposta, as seguintes verificações são feitas em sequência:
    a.  **Verificação de Pausa no Redis:**
        - O sistema chama `redis_client.is_human_handoff_active(phone)`.
        - Se a função retornar `True`, significa que a chave de pausa existe. A execução é interrompida e o agente não responde.
    b.  **Verificação de Estágio no Kommo:**
        - Se não houver pausa no Redis, o sistema chama a API do Kommo para obter os detalhes do lead.
        - Ele verifica o `status_id` e o `pipeline_id` do lead.
        - Se os IDs corresponderem a `KOMMO_HUMAN_HANDOFF_STAGE_ID` e `KOMMO_HUMAN_HANDOFF_PIPELINE_ID`, a execução é interrompida.
4.  **Processamento Normal:** Se nenhuma das condições acima for atendida, a mensagem é encaminhada para o agente de IA para processamento normal.

## 5. Configuração do Webhook no Kommo

Para que o sistema funcione, você deve configurar um webhook no Kommo:

1.  Vá para **Configurações > Integrações** no seu painel Kommo.
2.  Clique em **Criar Integração** e selecione a opção **Webhook**.
3.  **URL do Webhook:** Insira a URL do seu endpoint que receberá os eventos: `https://SUA_URL_DE_PRODUCAO/api/kommo/events`.
4.  **Eventos:** Marque a caixa de seleção para o evento **"Nota Adicionada"** (`note_added`) para Leads. Você também pode adicionar outros eventos como `lead_status_changed` para monitorar a mudança de estágio.
5.  Salve a integração.

Com essa configuração, o Kommo notificará sua aplicação sempre que uma nota for adicionada, permitindo que o sistema de transbordo funcione corretamente.
