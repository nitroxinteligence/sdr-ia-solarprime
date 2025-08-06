# Análise Completa e Aprofundada do Sistema de Follow-up e Integração com o AGNO Framework

## 1. Introdução e Escopo da Análise

Esta análise visa aprofundar o entendimento do sistema de follow-up existente, sua interação com o `SDRTeam`, a integração com o Kommo CRM e a interpretação de transcrições de áudio pelo agente principal. O objetivo é identificar lacunas, propor melhorias detalhadas e garantir que o sistema opere de forma coesa e eficiente, alinhado com as melhores práticas de arquitetura de software e IA conversacional.

**Componentes Chave Analisados:**
*   `FollowUpAgent` (`app/teams/agents/followup.py`)
*   `FollowUpExecutorService` (`app/services/followup_executor_service.py`)
*   `CRMAgent` / `KommoEnhancedCRM` (`app/teams/agents/crm.py`, `app/teams/agents/crm_enhanced.py`)
*   `AgenticSDR` (`app/agents/agentic_sdr.py`)
*   `SDRTeam` (`app/teams/sdr_team.py`)
*   Webhooks (`app/api/webhooks.py`)
*   Esquema do Banco de Dados (`sqls/tabela-follow_ups.sql`, `sqls/fix_followup_system.sql`, `sqls/migration_followup_reminders.sql`)
*   Prompt do Agente (`app/prompts/prompt-agente.md`)

## 2. Diagnóstico Aprofundado da Implementação Atual

### 2.1. `FollowUpAgent` (`app/teams/agents/followup.py`)

Este agente é o *cérebro* por trás do agendamento e personalização dos follow-ups.
*   **Função e Responsabilidades:** Principalmente responsável por *agendar* follow-ups na tabela `follow_ups` do Supabase. Ele não envia as mensagens diretamente, apenas as prepara e as registra para execução posterior.
*   **Geração de Mensagens:** Utiliza o método `personalize_message` para criar mensagens dinâmicas e contextuais. Este método carrega o `prompt-agente.md` para garantir que as mensagens sigam o tom e as diretrizes da Helen Vieira. A personalização inclui o nome do lead, valor da conta, e informações específicas de reunião/campanha.
*   **Agendamento (`schedule_followup`):** Recebe o `lead_id`, `followup_type`, `delay_hours` e `priority`. Calcula `scheduled_at` e ajusta para horário comercial (`_adjust_to_business_hours`). Salva o registro na tabela `follow_ups` com status `pending` e `attempts=0`.
*   **Estratégias de Follow-up (`FollowUpStrategy`):** Define estratégias (`AGGRESSIVE`, `MODERATE`, `GENTLE`, `EDUCATIONAL`) baseadas na "temperatura" do lead, influenciando a frequência e o conteúdo das mensagens.
*   **Rastreamento de Engajamento (`track_engagement`):** Atualiza o status do follow-up para `completed` e registra se houve resposta (`response_received`). Calcula métricas como `response_rate` e `avg_response_time_minutes` para o lead, atualizando a tabela `leads`.
*   **Lógica de Tentativas (`attempt`):** A coluna `attempt` na tabela `follow_ups` é usada para rastrear quantas vezes um follow-up específico foi tentado. No entanto, a lógica de *limite de tentativas* e a ação de "marcar como não interessado" após falhas consecutivas não estão totalmente centralizadas ou impostas por este agente.

### 2.2. `FollowUpExecutorService` (`app/services/followup_executor_service.py`)

Este serviço é o *braço executor* que opera em segundo plano.
*   **Função e Operação:** Roda em loops assíncronos (`_execution_loop`, `_meeting_reminder_loop`) para processar follow-ups e lembretes de reunião pendentes.
*   **Processamento de Follow-ups Pendentes (`process_pending_followups`):** Busca registros na tabela `follow_ups` com `status='pending'` e `scheduled_at <= NOW()`. Para cada um, chama `_execute_followup`.
*   **Envio de Mensagens:** Utiliza `evolution_client.send_text_message` para enviar as mensagens via WhatsApp. Após o envio, o status do follow-up é atualizado para `executed`.
*   **Lógica de Agendamento do Próximo Follow-up (`_schedule_next_followup`):**
    *   Atualmente, se um `IMMEDIATE_REENGAGEMENT` é enviado e o lead não respondeu (`not lead.get('last_response_at')`), ele agenda um `DAILY_NURTURING` para 24 horas depois.
    *   Para `DAILY_NURTURING`, ele continua agendando mais `DAILY_NURTURING` por até 7 tentativas.
    *   **Lacuna:** Esta lógica não incorpora diretamente a regra de "duas tentativas falhas e marcar como Não Interessado no Kommo". A dependência de `last_response_at` pode ser imprecisa para determinar uma "tentativa falha" no contexto de um follow-up específico.
*   **Processamento de Lembretes de Reunião (`process_meeting_reminders`, `_send_meeting_reminder`):** Busca eventos na tabela `calendar_events` que precisam de lembretes (24h e 2h antes) e os envia via WhatsApp, atualizando os flags `reminder_24h_sent` e `reminder_2h_sent`.
*   **Lacuna Principal:** O `FollowUpExecutorService` não possui uma instância do `CRMAgent` injetada, o que impede a atualização direta do status do lead no Kommo CRM após falhas de follow-up.

### 2.3. Kommo CRM Integration (`app/teams/agents/crm.py`, `app/teams/agents/crm_enhanced.py`, `app/services/kommo_auto_sync.py`)

A integração com o Kommo CRM é central para o ciclo de vida do lead.
*   **`CRMAgent` / `KommoEnhancedCRM`:** O `KommoEnhancedCRM` estende o `CRMAgent` e fornece métodos robustos para interagir com a API do Kommo, incluindo:
    *   `create_or_update_lead_direct`: Cria ou atualiza leads.
    *   `add_tags_to_lead`: Adiciona tags (ex: "qualificado-ia", "sem-resposta").
    *   `update_custom_fields`: Atualiza campos personalizados (ex: valor da conta, score).
    *   `move_card_to_pipeline`: Move leads entre estágios do pipeline (ex: "novo_lead", "qualificado", "nao_interessado").
    *   `create_deal`: Cria negócios.
    *   `add_task`: Adiciona tarefas.
*   **`KommoAutoSyncService`:** Este serviço (`app/services/kommo_auto_sync.py`) é responsável pela sincronização automática em segundo plano entre o Supabase e o Kommo. Ele monitora novos leads, atualizações, qualificações e reuniões, garantindo que o Kommo reflita o estado mais recente do lead.
*   **Lacuna:** A lógica de "marcar como Não Interessado" após duas tentativas falhas de follow-up *não está implementada* dentro do `FollowUpExecutorService` para acionar o `CRMAgent`. Atualmente, o `KommoAutoSyncService` não tem um gatilho direto para essa condição específica de follow-up.

### 2.4. Database Schema (`sqls/tabela-follow_ups.sql`, `sqls/fix_followup_system.sql`, `sqls/migration_followup_reminders.sql`)

O esquema do banco de dados é fundamental para o rastreamento do follow-up.
*   **`follow_ups` table:**
    *   `id`, `lead_id`, `scheduled_at`, `type`, `message`, `status`, `executed_at`, `result`, `created_at`, `updated_at`, `metadata`.
    *   **`follow_up_type`:** Enum com tipos como `IMMEDIATE_REENGAGEMENT`, `DAILY_NURTURING`, `MEETING_CONFIRMATION`, `MEETING_REMINDER`, `ABANDONMENT_CHECK`, `CUSTOM`.
    *   **`attempt` (INTEGER DEFAULT 0):** Coluna para rastrear o número de tentativas de envio de um follow-up.
    *   `last_attempt_at`, `next_retry_at`, `error_reason`, `response`: Colunas para gerenciar retries e erros.
    *   **Lacuna:** Não há uma coluna explícita para indicar se o Kommo já foi atualizado para "Não Interessado" para uma sequência de follow-up específica.
*   **`calendar_events` table:** Armazena eventos de calendário e possui flags para lembretes (`reminder_24h_sent`, `reminder_2h_sent`, `reminder_30min_sent`).
*   **SQL Functions/Triggers:**
    *   `auto_schedule_followup()`: Um trigger que tenta agendar um `IMMEDIATE_REENGAGEMENT` se o `last_interaction_at` de um lead for muito antigo.
    *   `get_events_needing_reminder()`: Funções para buscar eventos que precisam de lembretes.

### 2.5. `AgenticSDR` (`app/agents/agentic_sdr.py`) e Webhooks (`app/api/webhooks.py`)

Estes são os pontos de entrada e o agente principal.
*   **Fluxo de Mensagens:** O `webhooks.py` recebe mensagens da Evolution API (`process_new_message`) e as encaminha para `process_message_with_agent`. Este, por sua vez, obtém a instância do `AgenticSDR` e chama `agentic.process_message`.
*   **Processamento Multimodal (`process_multimodal_content` em `AgenticSDR`):**
    *   Lida com imagens, documentos e áudios.
    *   Para áudio, utiliza `AudioTranscriber` para converter o áudio em texto.
    *   **Ponto Crítico da Análise:** A transcrição de áudio é retornada no dicionário `multimodal_result` com a chave `transcription`.
*   **Lógica `should_call_sdr_team`:** No `AgenticSDR`, esta função decide se a mensagem deve ser tratada pelo `SDRTeam` (que delega para agentes especializados) ou se o `AgenticSDR` pode responder sozinho. Gatilhos como "solicitação de agendamento" (para `CalendarAgent`) ou "análise de conta" (para `BillAnalyzerAgent`) são detectados aqui.
*   **Interpretação da Transcrição de Áudio pelo Agente:**
    *   O `prompt-agente.md` contém uma seção explícita: "SE FOR ÁUDIO (MENSAGEM TRANSCRITA)".
    *   Instrui o agente a **PRIORIZAR O TEXTO DA TRANSCRIÇÃO** como conteúdo principal da mensagem do usuário e a **IGNORAR** mensagens genéricas como "[Áudio recebido]".
    *   O `AgenticSDR` no `process_message` passa o `media` (que contém a transcrição) para o `SDRTeam`.
    *   No `SDRTeam.process_message_with_context`, o `specialized_prompt` é construído para incluir a transcrição de áudio, garantindo que o Team Leader e os agentes a considerem como o "conteúdo real da mensagem".
    *   **Conclusão:** A arquitetura está desenhada para que a transcrição de áudio seja a fonte primária de informação para o agente, conforme as instruções do prompt.
*   **Interrupção da Sequência de Follow-ups:** Atualmente, quando uma nova mensagem é processada em `process_message_with_agent` (em `webhooks.py`), não há uma chamada explícita para cancelar follow-ups pendentes para aquele lead. Isso é uma lacuna crítica.

### 2.6. `SDRTeam` (`app/teams/sdr_team.py`)

O `SDRTeam` atua como o orquestrador dos agentes especializados.
*   **Função:** Recebe mensagens do `AgenticSDR` (após a análise inicial) e delega para os agentes especializados (`QualificationAgent`, `CalendarAgent`, `FollowUpAgent`, `CRMAgent`, etc.) com base na intenção detectada.
*   **Coordenação:** Opera no modo `coordinate`, onde o `Team Leader` (`Helen SDR Master`) analisa o contexto e decide qual agente deve agir.
*   **Injeção de Dependências:** Os agentes especializados são inicializados e seus `Agent`s são adicionados como membros do `Team`. No entanto, a injeção do `CRMAgent` no `FollowUpExecutorService` precisa ser garantida aqui.

## 3. Problemas e Lacunas Identificadas (Aprofundado)

1.  **Lógica "Não Interessado" no Kommo (Crítico):**
    *   **Problema:** Não há um mecanismo automatizado e robusto para mover o lead para o status "Não Interessado" no Kommo CRM após um número definido de tentativas de follow-up sem resposta. A lógica de `_schedule_next_followup` no `FollowUpExecutorService` apenas agenda o próximo follow-up, mas não aciona a atualização do CRM.
    *   **Impacto:** Leads inativos permanecem em estágios incorretos no CRM, poluindo o pipeline e exigindo intervenção manual.

2.  **Aplicação Incompleta do Limite de Tentativas:**
    *   **Problema:** Embora a coluna `attempt` exista na tabela `follow_ups`, ela não é rigorosamente utilizada para *parar* as sequências de follow-up e *acionar* a atualização no Kommo após um limite (ex: 2 tentativas falhas). O `FollowUpExecutorService` continua agendando `DAILY_NURTURING` por até 7 tentativas.
    *   **Impacto:** Envio excessivo de follow-ups para leads que já demonstraram inatividade, podendo gerar spam e deteriorar a experiência do lead.

3.  **Comunicação Inter-Serviços Deficiente (`FollowUpExecutorService` <-> `CRMAgent`):**
    *   **Problema:** O `FollowUpExecutorService` não tem acesso direto a uma instância do `CRMAgent` para realizar as atualizações no Kommo. A injeção de dependência do `CRMAgent` no `FollowUpExecutorService` não está implementada.
    *   **Impacto:** Impede a automação da atualização do status "Não Interessado" no Kommo diretamente do serviço que gerencia os follow-ups.

4.  **Sequência Específica (30min/24h) Não Totalmente Imposta:**
    *   **Problema:** A lógica atual de `_schedule_next_followup` no `FollowUpExecutorService` é genérica para `IMMEDIATE_REENGAGEMENT` e `DAILY_NURTURING`. A sequência exata de "30 minutos, depois 24 horas, e então marcar como não interessado" não está explicitamente codificada como um fluxo de estado com transições claras e um limite de tentativas global por lead.
    *   **Impacto:** Falha em seguir a estratégia de follow-up definida, resultando em leads perdidos ou mal gerenciados.

5.  **Definição Clara de "Tentativa Falha" e Interrupção da Sequência:**
    *   **Problema:** A lógica para determinar uma "tentativa falha" é baseada em `not lead.get('last_response_at')`, o que pode ser ambíguo. Além disso, quando um lead *finalmente responde*, não há um mecanismo automático em `webhooks.py` para *cancelar* todos os follow-ups pendentes para aquele lead.
    *   **Impacto:** Leads podem continuar recebendo follow-ups mesmo após terem respondido, gerando uma experiência negativa.

6.  **Interpretação da Transcrição de Áudio (Potencial Melhoria):**
    *   **Problema:** Embora o prompt instrua o agente a priorizar a transcrição, a forma como o `AgenticSDR` e o `SDRTeam` *utilizam* essa transcrição para inferência e resposta pode ser otimizada. A transcrição é passada como parte do `multimodal_result`, mas a garantia de que ela é a *única* fonte de "conteúdo da mensagem" para o LLM quando presente pode ser reforçada.
    *   **Impacto:** O agente pode ocasionalmente se confundir com a mensagem genérica "[Áudio recebido]" em vez de focar no conteúdo real da transcrição, levando a respostas menos precisas ou relevantes.

## 4. Proposta de Solução Detalhada

A solução proposta visa resolver as lacunas identificadas, aprimorando a robustez, a automação e a inteligência do sistema de follow-up.

### 4.1. Atualização do Esquema do Banco de Dados

*   **Tabela `follow_ups`:**
    *   **Adicionar `kommo_updated BOOLEAN DEFAULT FALSE`:** Esta coluna indicará se o Kommo CRM já foi atualizado para "Não Interessado" para aquela sequência de follow-up, evitando atualizações duplicadas.
    *   **Estender `follow_up_type` ENUM:**
        *   `SECOND_REENGAGEMENT_24H`: Para a segunda tentativa de reengajamento após 24 horas.
        *   `KOMMO_NOT_INTERESTED`: Um tipo de follow-up "final" que aciona a atualização no Kommo.
*   **Tabela `leads`:**
    *   **Adicionar `follow_up_attempt_count INTEGER DEFAULT 0`:** Para rastrear o número total de tentativas de follow-up *por lead* (não por follow-up individual), permitindo uma lógica de "duas tentativas falhas" mais global.
    *   **Adicionar `last_follow_up_response_at TIMESTAMP WITH TIME ZONE`:** Para registrar a última vez que o lead respondeu a *qualquer* follow-up, facilitando a interrupção das sequências.

### 4.2. Modificações no Código

#### 4.2.1. `app/services/followup_executor_service.py`

*   **Injeção do `CRMAgent`:**
    *   Modificar o construtor de `FollowUpExecutorService` para aceitar uma instância do `CRMAgent`. Isso permitirá que o serviço chame métodos do CRM diretamente.

    ```python
    # Exemplo de modificação no construtor
    class FollowUpExecutorService:
        def __init__(self, crm_agent: CRMAgent): # Adicionar crm_agent aqui
            self.db = SupabaseClient()
            self.evolution = evolution_client
            self.crm = crm_agent # Atribuir a instância do CRMAgent
            self.running = False
            self.check_interval = 60 # 1 minuto
            # ... (restante do código)
    ```

*   **Refinar Lógica de `_execute_followup`:**
    *   Após o envio de uma mensagem de follow-up, o status do registro na tabela `follow_ups` deve ser atualizado para `executed`.
    *   **Incrementar `attempt`:** A coluna `attempt` do follow-up atual deve ser incrementada.
    *   **Incrementar `follow_up_attempt_count` no `leads`:** O campo `follow_up_attempt_count` do lead deve ser incrementado.
    *   **Implementar Fluxo Condicional (30min/24h/Não Interessado):**
        *   **Se `IMMEDIATE_REENGAGEMENT` (1ª tentativa) for enviado:**
            *   Agendar um novo follow-up do tipo `SECOND_REENGAGEMENT_24H` (2ª tentativa) para 24 horas depois, *apenas se o lead não respondeu*.
        *   **Se `SECOND_REENGAGEMENT_24H` (2ª tentativa) for enviado:**
            *   Esta é a última tentativa antes de marcar como "Não Interessado".
            *   **Se o lead ainda não respondeu:** Chamar um novo método auxiliar `_mark_lead_not_interested_in_kommo(lead_id)`.
            *   Marcar o status do follow-up como `completed` e `kommo_updated = TRUE`.
        *   **Para outros tipos de follow-up:** Manter a lógica existente ou adicionar novas regras conforme a estratégia.

*   **Novo Método: `_mark_lead_not_interested_in_kommo(self, lead_id: str)`:**
    *   Este método será responsável por interagir com o Kommo CRM.
    *   Buscar o `kommo_lead_id` do lead no Supabase.
    *   Utilizar a instância injetada do `CRMAgent` para:
        *   Chamar `self.crm.move_card_to_pipeline` para mover o lead para o estágio "Não Interessado" no Kommo.
        *   Chamar `self.crm.add_tags_to_lead` para adicionar uma tag como "sem-resposta-final" ao lead no Kommo.
    *   Atualizar o registro correspondente na tabela `follow_ups` com `kommo_updated = TRUE` para o follow-up que acionou esta ação.
    *   Atualizar o `lead.qualification_status` para `NOT_QUALIFIED` no Supabase.

*   **Novo Método: `cancel_pending_followups_for_lead(self, lead_id: str)`:**
    *   Este método será chamado quando o usuário responder a qualquer mensagem.
    *   Ele deve atualizar todos os follow-ups `pending` (pendentes) para aquele `lead_id` para um status como `responded` ou `cancelled`, garantindo que não sejam enviados follow-ups desnecessários.

#### 4.2.2. `app/teams/agents/followup.py`

*   **Simplificar `schedule_followup`:**
    *   Garantir que este método possa iniciar o follow-up do tipo `IMMEDIATE_REENGAGEMENT` com `attempt=0`. A lógica de agendamento da próxima tentativa será movida para o `FollowUpExecutorService`.
*   **Atualizar `personalize_message`:**
    *   Adicionar templates de mensagens específicos para os novos tipos de follow-up: `IMMEDIATE_REENGAGEMENT` e `SECOND_REENGAGEMENT_24H`.

#### 4.2.3. `app/teams/sdr_team.py`

*   **Injetar Dependências:**
    *   No método `initialize` do `SDRTeam`, garantir que o `FollowUpExecutorService` seja instanciado com a instância correta do `CRMAgent`.

    ```python
    # Exemplo de modificação no initialize do SDRTeam
    # ...
    from app.services.followup_executor_service import followup_executor_service
    # Certifique-se de que self.crm_agent está inicializado antes
    if settings.enable_crm_agent and settings.enable_crm_integration:
        self.crm_agent = CRMAgent(model=self.model, storage=self.storage)
        await self.crm_agent.initialize() # Inicializar o CRMAgent
        team_members.append(self.crm_agent.agent)
        followup_executor_service.crm = self.crm_agent # Injetar o crm_agent
    # ...
    ```

*   **Gatilho de Follow-up Inicial:**
    *   No método `process_message_with_context` do `SDRTeam`, implementar uma lógica para verificar se uma conversa ficou inativa (por exemplo, baseando-se em `lead_data.last_interaction` ou `lead_data.updated_at`).
    *   Se a conversa estiver inativa e não houver follow-ups pendentes para o lead, chamar `self.followup_agent.schedule_followup` para iniciar o `IMMEDIATE_REENGAGEMENT` (30 minutos).
    *   Adicionar uma verificação para evitar agendamentos duplicados.

#### 4.2.4. `app/api/webhooks.py`

*   **Marcar Follow-ups como Respondidos:**
    *   No método `process_message_with_agent`, após uma mensagem do usuário ser processada, chamar o novo método `followup_executor_service.cancel_pending_followups_for_lead(lead_id)` para interromper qualquer sequência de follow-up ativa para aquele lead.
    *   Atualizar `lead.last_follow_up_response_at` no Supabase.

#### 4.2.5. `app/teams/agents/crm_enhanced.py`

*   **Verificar Estágio "Não Interessado":**
    *   Confirmar que o dicionário `self.pipeline_stages` no `CRMAgent` (ou `KommoEnhancedCRM`) mapeia corretamente `"nao_interessado"` para o ID do estágio correspondente no Kommo CRM.

#### 4.2.6. `app/agents/agentic_sdr.py` (Interpretação de Áudio)

*   **Reforçar Prioridade da Transcrição:**
    *   No método `process_multimodal_content`, garantir que, quando `media_type == "audio"` e `result["status"] == "success"`, a `transcribed_text` seja a *única* e *principal* informação usada para o `analysis_prompt` ou para qualquer processamento subsequente pelo agente.
    *   A seção do prompt (`prompt-agente.md`) que instrui o agente a priorizar a transcrição já é um bom começo, mas a implementação do código deve garantir que essa prioridade seja mantida.

### 4.3. Testes e Validação

*   **Testes Unitários:**
    *   Criar ou atualizar testes unitários para `FollowUpAgent` e `FollowUpExecutorService` para cobrir a nova lógica de tentativas e a integração com o CRM.
    *   Testar o método `_mark_lead_not_interested_in_kommo` isoladamente.
    *   Testar `cancel_pending_followups_for_lead`.
*   **Testes de Integração (End-to-End):**
    1.  Simular uma conversa que fica inativa.
    2.  Verificar o agendamento e envio do follow-up de 30 minutos (`IMMEDIATE_REENGAGEMENT`).
    3.  Simular inatividade contínua.
    4.  Verificar o agendamento e envio do follow-up de 24 horas (`SECOND_REENGAGEMENT_24H`).
    5.  Simular inatividade contínua após a 2ª tentativa.
    6.  Verificar se o lead é marcado como "Não Interessado" no Kommo CRM e no Supabase.
    7.  Simular uma resposta do lead em qualquer ponto da sequência para verificar se os follow-ups pendentes são cancelados.
    8.  **Testes de Áudio:** Enviar mensagens de áudio e verificar se o agente responde de forma coerente com o conteúdo transcrito, ignorando a mensagem genérica de áudio.

## 5. Conclusão e Próximos Passos

Com estas modificações, o sistema de follow-up se tornará mais robusto, autônomo e alinhado com os requisitos de negócio, garantindo que leads inativos sejam devidamente classificados no CRM e que a comunicação seja sempre contextual e eficiente, especialmente com o processamento aprimorado de áudio.

**Próximos Passos:**
1.  Implementar as alterações propostas no esquema do banco de dados.
2.  Modificar o código conforme as seções 4.2.1 a 4.2.6.
3.  Desenvolver e executar os testes unitários e de integração para validar as mudanças.
4.  Monitorar o sistema em ambiente de desenvolvimento/staging para garantir o comportamento esperado.
