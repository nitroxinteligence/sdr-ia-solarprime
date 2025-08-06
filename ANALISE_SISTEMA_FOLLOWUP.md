# Análise e Proposta de Melhoria para o Sistema de Follow-up

## Diagnóstico da Implementação Atual

O sistema de follow-up existente é composto por três componentes principais:

1.  **`FollowUpAgent` (`app/teams/agents/followup.py`)**:
    *   **Função**: Responsável por *agendar* os follow-ups, ou seja, criar registros na tabela `follow_ups` no banco de dados.
    *   **Geração de Mensagens**: Contém a lógica para gerar mensagens personalizadas para cada tipo de follow-up.
    *   **Agendamento**: Utiliza o parâmetro `delay_hours` para definir o tempo até o follow-up ser agendado.

2.  **`FollowUpExecutorService` (`app/services/followup_executor_service.py`)**:
    *   **Função**: Opera em segundo plano, *executando* os follow-ups pendentes (enviando as mensagens via Evolution API) e gerenciando lembretes de reuniões.
    *   **Lógica de Próximo Follow-up**: Possui uma lógica básica em `_schedule_next_followup` que agenda um `DAILY_NURTURING` após um `IMMEDIATE_REENGAGEMENT` se não houver resposta.
    *   **Limitação**: Atualmente, não há uma integração direta com o CRM para atualizar o status do lead.

3.  **Banco de Dados (Tabelas `follow_ups`, `calendar_events`, `leads`)**:
    *   **`follow_ups`**: Armazena os follow-ups agendados, incluindo um campo `attempt` (tentativa).
    *   **`calendar_events`**: Usada para lembretes de reuniões.
    *   **`leads`**: Contém informações do lead, como `last_response_at` (última resposta).
    *   **Gaps**: O campo `attempt` não é totalmente utilizado para impor uma regra estrita de "duas tentativas e marcar como não interessado".

4.  **Integração com Kommo CRM (`app/teams/agents/crm_enhanced.py`)**:
    *   **Capacidade**: O `KommoEnhancedCRM` possui métodos como `move_card_to_pipeline` e `add_tags_to_lead`, que são essenciais para atualizar o status do lead no Kommo.
    *   **Limitação**: O `FollowUpExecutorService` não interage diretamente com o `CRMAgent` para realizar essas atualizações.

5.  **Gatilhos e Respostas**:
    *   O `SDRTeam` é o ponto de entrada para iniciar o primeiro follow-up.
    *   O `webhooks.py` é responsável por processar as mensagens recebidas e, idealmente, deveria sinalizar quando um lead respondeu para interromper a sequência de follow-ups.

### Problemas e Lacunas Identificadas

1.  **Ausência de Lógica "Não Interessado" no Kommo**: Não existe um mecanismo explícito para mover o lead para o status "Não Interessado" no Kommo CRM após um número definido de follow-ups sem resposta.
2.  **Aplicação Incompleta do Limite de Tentativas**: Embora a coluna `attempt` exista, ela não é rigorosamente utilizada para parar as sequências de follow-up e acionar a atualização no Kommo.
3.  **Comunicação Inter-Serviços Deficiente**: O `FollowUpExecutorService` não tem acesso direto ao `CRMAgent`, o que impede a atualização do Kommo diretamente do serviço de execução de follow-ups.
4.  **Sequência Específica (30min/24h) Não Totalmente Implementada**: A sequência exata de "30 minutos, depois 24 horas, e então marcar como não interessado" não está totalmente codificada ou imposta.
5.  **Definição Clara de "Tentativa Falha"**: A lógica atual para agendar o próximo follow-up baseia-se em `not lead.get('last_response_at')`, que precisa ser mais precisamente vinculada à contagem de tentativas e ao tipo de follow-up.

## Proposta de Solução Detalhada

A solução proposta visa aprimorar o `FollowUpExecutorService` para gerenciar as tentativas de follow-up e interagir diretamente com o `CRMAgent` para atualizar o Kommo.

### A. Atualização do Esquema do Banco de Dados

*   **Adicionar `kommo_updated`**: Incluir uma coluna `kommo_updated BOOLEAN DEFAULT FALSE` na tabela `follow_ups`. Esta coluna indicará se o Kommo CRM já foi atualizado para aquela sequência de follow-up.
*   **Estender `follow_up_type`**: Adicionar novos valores ao `follow_up_type` ENUM para identificar as tentativas específicas:
    *   `SECOND_REENGAGEMENT_24H`: Para a segunda tentativa de reengajamento após 24 horas.

### B. Modificações no Código

#### 1. `app/services/followup_executor_service.py`

*   **Injeção do `CRMAgent`**:
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

*   **Refinar Lógica de `_execute_followup`**:
    *   Após o envio de uma mensagem de follow-up, o status do registro na tabela `follow_ups` deve ser atualizado para `sent`.
    *   Implementar um fluxo condicional baseado no `followup['type']` e `followup['attempt']`:
        *   **Se `IMMEDIATE_REENGAGEMENT` (tentativa 0) for enviado**:
            *   Agendar um novo follow-up do tipo `SECOND_REENGAGEMENT_24H` (tentativa 1) para 24 horas depois.
        *   **Se `SECOND_REENGAGEMENT_24H` (tentativa 1) for enviado**:
            *   Esta é a última tentativa.
            *   Chamar um novo método auxiliar `_mark_lead_not_interested_in_kommo(lead_id)`.
            *   Marcar o status do follow-up como `completed` e `kommo_updated = TRUE`.
    *   Atualizar o registro `follow_ups` com `status='sent'` e `last_attempt_at=datetime.now()`.

*   **Novo Método: `_mark_lead_not_interested_in_kommo(self, lead_id: str)`**:
    *   Este método será responsável por interagir com o Kommo CRM.
    *   Buscar o `kommo_lead_id` do lead no Supabase.
    *   Utilizar a instância injetada do `CRMAgent` para:
        *   Chamar `self.crm.move_card_to_pipeline` para mover o lead para o estágio "Não Interessado" no Kommo.
        *   Chamar `self.crm.add_tags_to_lead` para adicionar uma tag como "sem-resposta-final" ao lead no Kommo.
    *   Atualizar o registro correspondente na tabela `follow_ups` com `kommo_updated = TRUE`.

*   **Novo Método: `cancel_pending_followups_for_lead(self, lead_id: str)`**:
    *   Este método será chamado quando o usuário responder a qualquer mensagem.
    *   Ele deve atualizar todos os follow-ups `pending` (pendentes) para aquele `lead_id` para um status como `responded` ou `cancelled`, garantindo que não sejam enviados follow-ups desnecessários.

#### 2. `app/teams/agents/followup.py`

*   **Simplificar `schedule_followup`**:
    *   Garantir que este método possa iniciar o follow-up do tipo `IMMEDIATE_REENGAGEMENT` com `attempt=0`. A lógica de agendamento da próxima tentativa será movida para o `FollowUpExecutorService`.
*   **Atualizar `personalize_message`**:
    *   Adicionar templates de mensagens específicos para os novos tipos de follow-up: `IMMEDIATE_REENGAGEMENT` e `SECOND_REENGAGEMENT_24H`.

#### 3. `app/teams/sdr_team.py`

*   **Injetar Dependências**:
    *   No método `initialize` do `SDRTeam`, garantir que o `FollowUpExecutorService` seja instanciado com a instância correta do `CRMAgent`.

    ```python
    # Exemplo de modificação no initialize do SDRTeam
    # ...
    if settings.enable_crm_agent and settings.enable_crm_integration:
        self.crm_agent = CRMAgent(model=self.model, storage=self.storage)
        team_members.append(self.crm_agent.agent)
        # ...
    
    # Inicializar FollowUpExecutorService com o crm_agent
    from app.services.followup_executor_service import followup_executor_service
    followup_executor_service.crm = self.crm_agent # Injetar o crm_agent
    # ...
    ```

*   **Gatilho de Follow-up Inicial**:
    *   No método `process_message_with_context` do `SDRTeam`, implementar uma lógica para verificar se uma conversa ficou inativa (por exemplo, baseando-se em `lead_data.last_interaction` ou `lead_data.updated_at`).
    *   Se a conversa estiver inativa e não houver follow-ups pendentes para o lead, chamar `self.followup_agent.schedule_followup` para iniciar o `IMMEDIATE_REENGAGEMENT` (30 minutos).
    *   Adicionar uma verificação para evitar agendamentos duplicados.

#### 4. `app/api/webhooks.py`

*   **Marcar Follow-ups como Respondidos**:
    *   No método `process_message_with_agent`, após uma mensagem do usuário ser processada, chamar o novo método `followup_executor_service.cancel_pending_followups_for_lead(lead_id)` para interromper qualquer sequência de follow-up ativa para aquele lead.

#### 5. `app/teams/agents/crm_enhanced.py`

*   **Verificar Estágio "Não Interessado"**:
    *   Confirmar que o dicionário `self.pipeline_stages` no `CRMAgent` (ou `KommoEnhancedCRM`) mapeia corretamente `"nao_interessado"` para o ID do estágio correspondente no Kommo CRM.

### G. Testes e Validação

*   **Testes Unitários**: Criar ou atualizar testes unitários para `FollowUpAgent` e `FollowUpExecutorService` para cobrir a nova lógica de tentativas e a integração com o CRM.
*   **Testes de Integração**: Realizar testes de ponta a ponta para simular o fluxo completo:
    1.  Início da conversa.
    2.  Inatividade do lead.
    3.  Envio do follow-up de 30 minutos.
    4.  Inatividade contínua.
    5.  Envio do follow-up de 24 horas.
    6.  Inatividade contínua.
    7.  Atualização do status do lead para "Não Interessado" no Kommo CRM.
    8.  Simular uma resposta do lead em qualquer ponto para verificar se os follow-ups pendentes são cancelados.

### H. Documentação

*   Este documento serve como a base para a documentação. Após a implementação, ele pode ser refinado e incluído na pasta `docs/` do projeto.

---

Com esta abordagem, o sistema de follow-up se tornará mais robusto, autônomo e alinhado com os requisitos de negócio, garantindo que leads inativos sejam devidamente classificados no CRM.
