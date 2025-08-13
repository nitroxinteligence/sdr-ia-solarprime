# Plano de Ação: Integração Google Calendar com OAuth 2.0

**Autor:** Gemini
**Data:** 2025-08-11
**Versão:** 1.0

## 1. Introdução

Este documento detalha o plano de ação para refatorar a integração com o Google Calendar, substituindo a autenticação via **Service Account** pelo fluxo **OAuth 2.0**. O objetivo é capacitar o agente de IA a criar eventos de calendário que incluam links de **Google Meet** e permitam o convite de múltiplos participantes, funcionalidades que não são suportadas de forma robusta pelo método de Service Account sem delegação em todo o domínio.

### 1.1. Limitação Atual (Service Account)

A implementação atual utiliza uma Service Account do Google Cloud. Este método é ideal para acesso a dados do lado do servidor, mas possui limitações significativas para ações que exigem permissões de usuário:

- **Criação de Google Meet:** A API do Calendar não permite que Service Accounts criem links de Google Meet automaticamente, a menos que a conta tenha delegação em todo o domínio (Domain-Wide Delegation), uma configuração complexa e disponível apenas para contas Google Workspace.
- **Convite de Participantes:** Service Accounts não podem convidar participantes para eventos, pois não agem em nome de um usuário real que possua uma agenda.

### 1.2. Solução Proposta (OAuth 2.0)

A solução é migrar para o fluxo de autenticação **OAuth 2.0 para Aplicações Web**. Este fluxo permitirá que a aplicação solicite permissão a um usuário real (ex: o vendedor Leonardo) para gerenciar sua agenda. Uma vez autorizado, o sistema poderá:

- **Agir em nome do usuário:** Criar, modificar e excluir eventos na agenda do usuário autorizado.
- **Criar links de Google Meet:** Gerar links de videoconferência automaticamente para cada evento.
- **Convidar Participantes:** Adicionar uma lista de e-mails como convidados para o evento.
- **Persistir Acesso:** Utilizar um *refresh token* para manter o acesso à API sem a necessidade de intervenção manual repetida.

## 2. Análise do Sistema Atual

A funcionalidade de calendário está distribuída nos seguintes arquivos principais:

- **`app/config.py`**: Armazena as credenciais da Service Account (`GOOGLE_SERVICE_ACCOUNT_EMAIL`, `GOOGLE_PRIVATE_KEY`, etc.).
- **`app/integrations/google_calendar.py`**: Contém a classe `GoogleCalendarClient`, que utiliza as credenciais da Service Account para se autenticar e construir o objeto de serviço da API.
- **`app/integrations/google_meet_handler.py`**: Tenta contornar a limitação da Service Account, mas confirma que a criação de Meets requer delegação em todo o domínio.
- **`app/services/calendar_service_100_real.py`**: A classe `CalendarServiceReal` utiliza o `GoogleCalendarClient` para executar operações como `schedule_meeting`. A implementação atual não passa `attendees` ou `conferenceData` de forma eficaz.
- **`app/agents/agentic_sdr.py`**: O agente principal, que em seu fluxo de agendamento, não solicita os e-mails dos participantes, pois a infraestrutura atual não suporta o convite.

## 3. Plano de Implementação Detalhado

A implementação será dividida em 7 etapas principais, afetando a configuração, a lógica de autenticação, os serviços e a interação do agente.

### Etapa 1: Configuração no Google Cloud Console

Antes de qualquer alteração no código, é necessário criar as credenciais corretas no Google Cloud Console.

1.  **Acesse o Google Cloud Console:** [https://console.cloud.google.com/](https://console.cloud.google.com/)
2.  **Navegue para "APIs & Services" > "Credentials"**.
3.  Clique em **"+ CREATE CREDENTIALS"** e selecione **"OAuth client ID"**.
4.  Selecione **"Web application"** como o tipo de aplicação.
5.  **Configure os "Authorized redirect URIs"**:
    - Adicione a URI de callback da nossa aplicação. Para desenvolvimento local, será `http://localhost:8000/google/callback`. Para produção, será o endereço do servidor.
6.  **Salve as credenciais**. O Google fornecerá um **Client ID** e um **Client Secret**. Estes valores serão usados na nossa configuração.
7.  **Garanta que a API do Google Calendar esteja ativada** no projeto.

### Etapa 2: Atualização das Configurações (`app/config.py`)

As variáveis de ambiente relacionadas à Service Account serão substituídas pelas credenciais OAuth 2.0.

**Ações:**

1.  **Remover** as seguintes variáveis de `app/config.py` e do arquivo `.env`:
    - `GOOGLE_USE_SERVICE_ACCOUNT`
    - `GOOGLE_SERVICE_ACCOUNT_EMAIL`
    - `GOOGLE_PRIVATE_KEY`
    - `GOOGLE_PROJECT_ID`
    - `GOOGLE_PRIVATE_KEY_ID`
2.  **Adicionar** as novas variáveis:
    - `GOOGLE_CLIENT_ID`: O Client ID obtido no Google Cloud Console.
    - `GOOGLE_CLIENT_SECRET`: O Client Secret obtido.
    - `GOOGLE_REDIRECT_URI`: A URI de callback configurada (`http://localhost:8000/google/callback`).
    - `GOOGLE_REFRESH_TOKEN`: Este campo ficará **vazio** inicialmente. Ele será preenchido uma única vez após o primeiro fluxo de autorização.

### Etapa 3: Módulo de Autenticação OAuth 2.0 (`app/integrations/google_oauth_handler.py`)

Criaremos um novo módulo para encapsular a lógica do OAuth 2.0, mantendo o código organizado.

**Ações:**

1.  **Criar o arquivo `app/integrations/google_oauth_handler.py`**.
2.  **Implementar as seguintes funções:**
    - `get_google_auth_url()`: Gera a URL de autorização para a qual o usuário será redirecionado para dar consentimento.
    - `handle_google_callback(code: str)`: Recebe o código de autorização da Google, troca-o por um *access token* e um *refresh token*, e salva o *refresh token* de forma segura.
    - `get_credentials()`: Retorna um objeto de credenciais do Google (usando o refresh token para obter um novo access token quando necessário).

### Etapa 4: Refatoração do Cliente do Google Calendar (`app/integrations/google_calendar.py`)

O `GoogleCalendarClient` será modificado para usar o novo handler de OAuth 2.0.

**Ações:**

1.  **Alterar o método `_authenticate`**: Em vez de carregar as credenciais da Service Account, ele chamará `google_oauth_handler.get_credentials()` para obter as credenciais de usuário.
2.  **Remover a lógica de `delegated_user`**, pois não será mais necessária.

### Etapa 5: Atualização do Serviço de Calendário (`app/services/calendar_service_100_real.py`)

O serviço que cria o evento será atualizado para incluir os novos parâmetros.

**Ações:**

1.  **Modificar a assinatura do método `schedule_meeting`**:
    - Adicionar um parâmetro `attendees: List[str] = None`.
2.  **Atualizar o corpo do evento (`event` body):**
    - Adicionar o campo `attendees` com a lista de e-mails.
    - Adicionar o campo `conferenceData` para solicitar a criação de um Google Meet.

    ```python
    # Exemplo da nova estrutura do evento
    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': settings.timezone},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': settings.timezone},
        'attendees': [{'email': email} for email in attendees],
        'conferenceData': {
            'createRequest': {
                'requestId': f'meet-{uuid.uuid4()}',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        },
        # ...
    }
    ```

### Etapa 6: Modificação do Fluxo do Agente (`app/agents/agentic_sdr.py`)

O agente precisa ser instruído a coletar os e-mails dos participantes durante o processo de agendamento.

**Ações:**

1.  **Atualizar o `prompt-agente.md`**: Na seção de agendamento, adicionar a instrução para que a Helen **sempre** solicite o e-mail de todos os participantes da reunião.
2.  **Modificar a lógica em `should_call_sdr_team` ou `_execute_service_directly`**: Quando o `CalendarAgent` for acionado, o contexto passado para ele deve incluir a lista de e-mails coletada.

### Etapa 7: Criação de Endpoints da API para o Fluxo OAuth

Novos endpoints são necessários para gerenciar o fluxo de autorização.

**Ações:**

1.  **Criar um novo arquivo de rota, ex: `app/api/google_auth.py`**.
2.  **Implementar dois endpoints:**
    - `GET /google/auth`:
        - Gera a URL de autorização usando `google_oauth_handler.get_google_auth_url()`.
        - Redireciona o usuário para essa URL. Este passo é manual e será executado uma única vez pelo administrador do sistema para autorizar a aplicação.
    - `GET /google/callback`:
        - Recebe o `code` de autorização da Google.
        - Chama `google_oauth_handler.handle_google_callback(code)` para obter e salvar o refresh token.
        - Exibe uma mensagem de sucesso para o administrador.

## 4. Considerações de Segurança

O `GOOGLE_REFRESH_TOKEN` é uma credencial extremamente sensível. Se comprometido, permite acesso contínuo à conta do usuário.

- **Armazenamento:** Para este projeto, o token será armazenado como uma variável de ambiente, assim como as outras chaves. Em um ambiente de produção de alta segurança, o ideal seria utilizar um serviço de "vault" (como HashiCorp Vault ou AWS Secrets Manager).

## 5. Conclusão

A migração para o OAuth 2.0 é um passo fundamental para desbloquear funcionalidades essenciais do Google Calendar. Embora exija uma refatoração significativa, o resultado será um sistema mais capaz e profissional, que oferece uma experiência de agendamento completa e automatizada para o usuário final, incluindo convites e links de videoconferência.
