# Documentação: Sincronização Dinâmica com Kommo CRM

## 1. Visão Geral

Este documento detalha o sistema de sincronização automática e dinâmica de **Tags** e **Campos Personalizados** entre o agente de IA e o Kommo CRM. O objetivo é enriquecer os cards dos leads no Kommo com informações contextuais em tempo real, refletindo a jornada exata do cliente na conversa com o agente.

O sistema foi projetado para ser um "worker" assíncrono, garantindo que as atualizações no CRM ocorram de forma eficiente sem impactar o tempo de resposta do agente.

## 2. Arquitetura e Componentes

A sincronização é orquestrada por três componentes principais que trabalham em conjunto, usando o banco de dados Supabase como a fonte da verdade.

1.  **AgenticSDR (`agentic_sdr_refactored.py`):**
    - **Responsabilidade:** Conduzir a conversa e capturar informações cruciais.
    - **Ação:** Salva o estado atual da conversa (como o fluxo de solução escolhido pelo lead) na tabela `leads` do Supabase.

2.  **Serviços de Suporte (Ex: `calendar_service_100_real.py`):**
    - **Responsabilidade:** Executar ações específicas, como agendar reuniões.
    - **Ação:** Salva os resultados de suas ações (como o link de um evento do Google Calendar) na tabela `leads` do Supabase.

3.  **Serviço de Sincronização (`kommo_auto_sync.py`):**
    - **Responsabilidade:** Atua como um worker em background, monitorando a tabela `leads` no Supabase.
    - **Ação:** Detecta alterações nos leads, determina quais tags e campos precisam ser atualizados e chama o `crm_service` para efetivar as mudanças no Kommo CRM.

4.  **Serviço de CRM (`crm_service_100_real.py`):**
    - **Responsabilidade:** É a camada de comunicação direta com a API do Kommo CRM.
    - **Ação:** Executa as ordens do serviço de sincronização, como adicionar/remover tags e preencher campos personalizados.

## 3. Gerenciamento Dinâmico de Tags

O sistema aplica e atualiza tags automaticamente com base no contexto do lead.

| Tag | Gatilho / Condição | Lógica de Aplicação |
| :--- | :--- | :--- |
| `SDR IA` | Qualquer interação com o agente. | Adicionada a todos os leads que são criados ou gerenciados pelo sistema de IA. |
| `Instalação Usina Própria` | Lead escolhe a **Opção 1** no Estágio 1 do fluxo. | O agente salva o fluxo escolhido no Supabase; o worker detecta e aplica a tag. |
| `Aluguel de Lote` | Lead escolhe a **Opção 2** no Estágio 1 do fluxo. | O agente salva o fluxo escolhido no Supabase; o worker detecta e aplica a tag. |
| `Compra com Desconto` | Lead escolhe a **Opção 3** no Estágio 1 do fluxo. | O agente salva o fluxo escolhido no Supabase; o worker detecta e aplica a tag. |
| `Usina Investimento` | Lead escolhe a **Opção 4** no Estágio 1 do fluxo. | O agente salva o fluxo escolhido no Supabase; o worker detecta e aplica a tag. |
| `follow-up-automatico` | O `FollowUpExecutorService` agenda um follow-up. | Quando um follow-up é criado na tabela `follow_ups`, o worker pode identificar e aplicar a tag. |
| `sem-resposta` | O lead está em um ciclo de reengajamento por inatividade. | Se o `FollowUpExecutorService` envia um follow-up de reengajamento, a tag é aplicada. |
| `numero-invalido` | A API do Evolution (WhatsApp) retorna um erro indicando que o número não é válido. | O sistema detecta a falha no envio, atualiza um campo no Supabase, e o worker aplica a tag. |

## 4. Preenchimento de Campos Personalizados

O sistema preenche automaticamente os campos personalizados no Kommo CRM.

| Campo Personalizado | Fonte do Dado | Lógica de Preenchimento |
| :--- | :--- | :--- |
| `WhatsApp` | `leads.phone_number` | O número de telefone do lead é extraído da primeira interação e salvo neste campo. |
| `Valor da conta de Energia` | `leads.bill_value` | Quando o agente extrai o valor da conta de luz (seja por texto ou imagem), ele é salvo no Supabase e depois sincronizado para este campo. |
| `Solucao Solar` | `leads.chosen_flow` | O nome do fluxo escolhido pelo lead (Ex: "Instalação Usina Própria") é salvo no Supabase e sincronizado para este campo de seleção no Kommo. |
| `Link do evento no google calendar` | `leads.google_event_link` | Quando o `CalendarService` agenda uma reunião, ele recebe o link do evento do Google. Este link é salvo no Supabase, e o worker o sincroniza para este campo no Kommo. |

## 5. Fluxo de Dados (Exemplo)

1.  **Interação:** Um novo lead envia "Olá" e, após a apresentação, escolhe a opção "1. Instalação de usina própria".
2.  **Ação do Agente:** O `AgenticSDR` processa a escolha e atualiza o registro do lead na tabela `leads` do Supabase, preenchendo a coluna `chosen_flow` com o valor `Instalação Usina Própria`.
3.  **Detecção do Worker:** O `KommoAutoSyncService`, em seu próximo ciclo, detecta que o campo `chosen_flow` do lead foi atualizado.
4.  **Lógica de Sincronização:**
    - O serviço determina que a tag `Instalação Usina Própria` deve ser aplicada.
    - Ele também determina que o campo personalizado `Solucao Solar` deve ser preenchido com o mesmo valor.
5.  **Execução no CRM:** O serviço chama os métodos apropriados no `crm_service_100_real.py`.
6.  **Atualização no Kommo:** O `crm_service` faz as chamadas à API do Kommo para adicionar a tag e preencher o campo personalizado no card do lead correspondente.

## 6. Pré-requisitos de Configuração no Kommo CRM

Para que a sincronização funcione, os seguintes itens **devem ser criados manualmente** na sua conta Kommo antes de executar o sistema:

### Tags Obrigatórias

Certifique-se de que as seguintes tags existem em **Configurações > Tags**:

-   `Aluguel de Lote`
-   `Compra com Desconto`
-   `follow-up-automatico`
-   `Instalação Usina Própria`
-   `numero-invalido`
-   `SDR IA`
-   `sem-resposta`
-   `Usina Investimento`

### Campos Personalizados Obrigatórios

Vá para **Configurações > Campos** e crie os seguintes campos para **Leads**:

1.  **WhatsApp**
    -   **Tipo de campo:** Telefone
2.  **Valor da conta de Energia**
    -   **Tipo de campo:** Número
3.  **Solucao Solar**
    -   **Tipo de campo:** Lista de Seleção (Select)
    -   **Opções da Lista:**
        -   `Instalação Usina Própria`
        -   `Aluguel de Lote`
        -   `Compra com Desconto`
        -   `Usina Investimento`
4.  **Link do evento no google calendar**
    -   **Tipo de campo:** URL
