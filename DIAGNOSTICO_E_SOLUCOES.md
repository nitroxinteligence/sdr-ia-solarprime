# Diagnóstico e Plano de Ação - Erros de Produção (13/08/2025)

## Visão Geral

A análise dos logs e do código-fonte revelou três problemas principais, sendo um deles a causa raiz para a instabilidade geral do sistema. Os problemas são: um erro crítico de `TypeError` no processamento de mensagens do agente, falhas na autenticação com o Google (OAuth) e, como consequência do primeiro erro, falhas no sistema de follow-up.

---

## 1. Erro Crítico: `TypeError` no `AgenticSDR` (Causa Raiz)

### a. Problema

O sistema está falhando ao processar qualquer nova mensagem do WhatsApp, resultando no erro:
`TypeError: AgenticSDR.process_message() got an unexpected keyword argument 'phone'`

### b. Causa

Existe uma incompatibilidade entre a **chamada** da função e a sua **definição**:

1.  **Onde é chamada (O Chamador):** No arquivo `app/api/webhooks.py`, a função `process_message_with_agent` chama o agente da seguinte forma:
    ```python
    response = await agentic.process_message(
        phone=phone,
        message=message_content,
        lead_data=lead,
        conversation_id=conversation_id,
        media=media_data,
        message_id=message_id,
        current_emotional_state=current_emotional_state
    )
    ```

2.  **Onde é definida (A Função):** No arquivo `app/agents/agentic_sdr_refactored.py`, a função está definida para aceitar apenas `message` e `metadata`:
    ```python
    async def process_message(self, message: str, metadata: Dict[str, Any] = None) -> str:
        # ...
    ```

Essa divergência faz com que o Python lance um `TypeError`, pois a função não reconhece os argumentos `phone`, `lead_data`, etc.

### c. Solução Proposta

Alterar a assinatura do método `process_message` em `app/agents/agentic_sdr_refactored.py` para que ela aceite todos os argumentos que estão sendo passados pelo webhook. Isso sincronizará o chamador e a função, resolvendo o erro principal.

---

## 2. Falha na Autenticação do Google Calendar (OAuth)

### a. Problema

O sistema não consegue se conectar ao Google Calendar para agendar reuniões. O log indica:
`⚠️ Refresh token não disponível - autorização necessária`

### b. Causa

A variável de ambiente `GOOGLE_OAUTH_REFRESH_TOKEN` não está definida no ambiente de produção (Easypanel). Este token é essencial para que o sistema se autentique de forma persistente com a API do Google sem a necessidade de intervenção manual a cada vez.

### c. Solução Proposta

É necessário gerar e configurar o `REFRESH_TOKEN` no ambiente de produção:

1.  **Acessar o Endpoint de Autorização:** Com o sistema rodando, acesse a URL `[SUA_URL_DE_PRODUCAO]/google/auth` em um navegador.
2.  **Autorizar:** Faça login com a conta do Google que gerencia o calendário e conceda as permissões solicitadas.
3.  **Callback e Salvamento:** Após a autorização, o Google redirecionará para a URL de callback. O backend irá capturar o `refresh_token` e **salvá-lo automaticamente no arquivo `.env` do projeto**.
4.  **Configurar no Easypanel:** Copie o valor da variável `GOOGLE_OAUTH_REFRESH_TOKEN` do arquivo `.env` e adicione-a como uma variável de ambiente no painel do seu serviço no Easypanel.
5.  **Reiniciar o Serviço:** Após adicionar a variável, reinicie o serviço no Easypanel para que ele carregue a nova configuração.

---

## 3. Falhas no Sistema de Follow-up

### a. Problema

O serviço de follow-up está falhando repetidamente, como mostra o log:
`⚠️ Follow-up falhou, tentativa 1/3. Aguardando 30s...`

### b. Causa

Este problema é um **sintoma direto do Erro Crítico nº 1**. O sistema de follow-up depende do `AgenticSDR` para gerar mensagens de reengajamento personalizadas. Como a chamada ao `AgenticSDR` falha, a execução do follow-up também falha, resultando no ciclo de retentativas.

### c. Solução Proposta

A correção do `TypeError` no `AgenticSDR` deve resolver este problema automaticamente. Uma vez que o agente consiga processar mensagens e gerar respostas, o sistema de follow-up voltará a funcionar como esperado. Nenhuma ação adicional é necessária além de monitorar os logs após o deploy da correção principal.

---

## Plano de Ação Imediato

1.  **Corrigir o `TypeError` no `AgenticSDR`**, que é a correção mais crítica.
2.  **Realizar o deploy da correção** para o ambiente de produção.
3.  **Executar o fluxo de autorização do Google OAuth** para configurar o `REFRESH_TOKEN` no Easypanel.
4.  **Monitorar os logs** para confirmar que todos os sistemas (processamento de mensagens, follow-up, agendamento) voltaram à normalidade.
