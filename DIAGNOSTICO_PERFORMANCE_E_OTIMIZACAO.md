# Diagnóstico de Performance e Plano de Otimização do Agente

**Solicitação:** Mapear todo o processo de agente, desde a chegada da mensagem do usuário até a resposta do agente, pois precisamos que todo este tempo dure no máximo 30 segundos (ou até 1 minuto com reasoning ativado). Analisar minuciosamente, encontrar gargalos, etapas desnecessárias, melhorias e correções para atingir a meta de performance.

**Análise Realizada:** Foi feita uma análise profunda de todo o diretório `@app/**`, mapeando o fluxo de dados e identificando os principais pontos de latência.

---

## 1. Mapeamento do Fluxo de Processamento Atual (High-Level)

O fluxo atual, desde a chegada de uma mensagem até a resposta, pode ser mapeado da seguinte forma:

1.  **`[Entrada]` Webhook Recebe a Mensagem**: `app/api/webhooks.py` recebe a requisição da Evolution API.
2.  **`[I/O]` Busca/Criação de Dados no Banco**: O método `process_message_with_agent` realiza chamadas sequenciais ao Supabase para:
    *   Obter ou criar o `lead`.
    *   Obter ou criar a `conversation`.
    *   Salvar a mensagem do usuário.
3.  **`[Processamento]` Instanciação do Agente**: `get_agentic_agent()` é chamado, criando uma **nova instância** do `AgenticSDR` a cada mensagem.
    *   Isso implica reinicializar modelos de LLM, configurações, tools, etc., o que é extremamente custoso em termos de tempo.
4.  **`[Processamento + I/O]` Análise de Contexto do Agente**: Dentro do `AgenticSDR`, o método `process_message` (que não está no código, mas é o método principal de um agente) provavelmente aciona `analyze_conversation_context`.
    *   Este método realiza outra chamada ao banco (`get_last_100_messages`).
    *   Executa uma série de análises de texto (regex, contagem, etc.) de forma síncrona.
5.  **`[LLM Call]` Chamada ao Modelo de Linguagem**: O `AgenticSDR` faz uma chamada ao LLM (Gemini) para gerar uma resposta. Se o `reasoning` estiver habilitado, este passo pode ser ainda mais demorado.
6.  **`[Decisão]` Delegação (Potencial)**: O `AgenticSDR` pode decidir chamar o `SDRTeam`, que por sua vez pode acionar outros agentes, potencialmente resultando em **múltiplas chamadas ao LLM em série**.
7.  **`[Saída]` Envio da Resposta**: A resposta final é enviada pela `evolution_client`.

---

## 2. Diagnóstico: Principais Gargalos de Performance

A análise detalhada revela os seguintes gargalos que, somados, elevam o tempo de resposta para além da meta de 30 segundos:

### Gargalo 1: Instanciação Contínua de Agentes (Gravíssimo)

*   **Local**: `app/api/webhooks.py` na função `get_agentic_agent()`.
*   **Problema**: A cada nova mensagem, uma nova instância de `AgenticSDR` é criada. O construtor `__init__` do `AgenticSDR` é complexo: ele inicializa o `IntelligentModelFallback` (que configura os modelos Gemini e OpenAI), o `AgentMemory`, o `PgVector`, o `AgentKnowledge` e o `Agent` principal. Esta é, de longe, a maior fonte de latência do sistema.
*   **Impacto**: Causa um atraso desnecessário de vários segundos em **cada mensagem**, pois recursos que poderiam ser compartilhados (como a conexão com a API do LLM) são recriados a todo momento.

### Gargalo 2: Operações de I/O Sequenciais e Redundantes

*   **Local**: `app/api/webhooks.py` e `app/agents/agentic_sdr.py`.
*   **Problema**: O código executa múltiplas chamadas ao banco de dados (Supabase) de forma sequencial, onde poderiam ser paralelizadas.
    1.  `get_lead_by_phone()`
    2.  `get_conversation_by_phone()`
    3.  `save_message()`
    4.  Dentro do agente, `get_last_100_messages()` é chamado novamente.
*   **Impacto**: Cada chamada de rede ao banco de dados adiciona latência. A execução em série soma esses tempos, em vez de executar as chamadas independentes de forma concorrente.

### Gargalo 3: Múltiplas Camadas de Análise e Chamadas ao LLM

*   **Local**: `app/agents/agentic_sdr.py` e `app/teams/sdr_team.py`.
*   **Problema**: A arquitetura atual possui uma cadeia de comando que pode resultar em múltiplas chamadas ao LLM para uma única mensagem do usuário:
    1.  O `AgenticSDR` primeiro analisa o contexto.
    2.  Ele pode então chamar o `SDRTeam` para uma análise mais aprofundada.
    3.  O `SDRTeam`, por sua vez, delega para um agente especialista (ex: `CalendarAgent`), que pode fazer sua própria chamada ao LLM.
*   **Impacto**: Cada chamada ao LLM é uma operação de alta latência. Múltiplas chamadas em série multiplicam o tempo de espera, tornando a meta de 30 segundos inatingível.

### Gargalo 4: Análise de Contexto Síncrona e Pesada

*   **Local**: `app/agents/agentic_sdr.py`, no método `analyze_conversation_context`.
*   **Problema**: Este método realiza uma série de análises baseadas em regex e lógica síncrona sobre um histórico de até 100 mensagens. Embora não seja tão lento quanto uma chamada de rede, processar um grande volume de texto repetidamente pode adicionar uma latência considerável.
*   **Impacto**: Adiciona um tempo de processamento de CPU que poderia ser otimizado ou executado em paralelo com outras operações de I/O.

---

## 3. Plano de Otimização e Nova Arquitetura Proposta

Para atingir a meta de performance, é necessária uma refatoração significativa, focada em **paralelismo**, **redução de chamadas ao LLM** e **gerenciamento de estado eficiente**. Proponho a seguinte arquitetura:

### Solução 1: Implementar Singletons para Agentes e Clientes

O `AgenticSDR` e seus sub-agentes devem ser inicializados **uma única vez** no startup da aplicação e reutilizados, em vez de serem recriados a cada requisição.

*   **Ação**: Modificar `app/api/webhooks.py` e `main.py` para criar uma instância singleton do `AgenticSDR` (e, por consequência, do `SDRTeam` e seus agentes) que será compartilhada entre as requisições. O estado da conversa (como o emocional) deve ser gerenciado por conversa, não na instância do agente.

### Solução 2: Orquestração Paralela com `asyncio.gather`

O fluxo de processamento deve ser reestruturado para executar todas as operações de I/O e análises independentes em paralelo.

*   **Ação**: Criar um **Agente Orquestrador** (pode ser uma nova função dentro do `webhooks.py` ou uma classe dedicada) que, ao receber uma mensagem, dispara as seguintes tarefas concorrentemente com `asyncio.gather`:
    1.  `task_db_data = asyncio.create_task(supabase_client.get_or_create_conversation_and_lead(phone))`
    2.  `task_history = asyncio.create_task(supabase_client.get_conversation_messages(conversation_id))`
    3.  `task_media = asyncio.create_task(process_multimodal_content(media))` (se houver mídia)

### Solução 3: Centralizar a Inteligência e Reduzir Chamadas ao LLM

Eliminar a cadeia de comando com múltiplas chamadas ao LLM. A nova arquitetura deve ter um fluxo mais direto:

1.  **Coleta Paralela de Dados**: O Orquestrador executa as tarefas do passo anterior.
2.  **Síntese de Contexto**: Aguarda a conclusão de todas as tarefas e sintetiza um **contexto enriquecido único**.
3.  **Chamada Única e Decisiva ao LLM**: Faz **uma única chamada** ao `AgenticSDR` (ou `SDRTeam`) com todo o contexto enriquecido. O prompt deve ser claro para que o agente gere a resposta final e, se necessário, chame as ferramentas (`tools`) apropriadas (como `schedule_meeting`) em uma única passada.

### Solução 4: Introduzir Sub-Agentes de Análise Assíncronos

Para otimizar a análise de contexto, podemos criar sub-agentes leves que rodam em paralelo.

*   **Ação**: Em vez de um método monolítico `analyze_conversation_context`, o Orquestrador pode chamar múltiplos "micro-analisadores" em paralelo:

    ```python
    # Exemplo de como o Orquestrador funcionaria
    analysis_tasks = [
        analyze_sentiment(history),
        detect_intent(message),
        extract_entities(message)
    ]
    analysis_results = await asyncio.gather(*analysis_tasks)
    ```

    Os resultados são então agregados ao contexto enriquecido antes da chamada final ao LLM.

### 5. Proposta de Novo Fluxo Otimizado

1.  **`[Entrada]` Webhook**: Recebe a mensagem.
2.  **`[Orquestração Paralela]`**: `asyncio.gather` é usado para disparar simultaneamente:
    *   Busca/criação de dados do lead e da conversa no Supabase.
    *   Busca do histórico de mensagens.
    *   Processamento de mídia (se houver).
    *   Análises rápidas de texto (sentimento, intenção).
3.  **`[Síntese]`**: O Orquestrador aguarda a conclusão de todas as tarefas e monta um único objeto de `enriched_context`.
4.  **`[Decisão e Geração]`**: O `AgenticSDR` é chamado **uma única vez** com o `enriched_context`. Seu prompt é instruído a:
    *   Gerar a resposta final para o usuário.
    *   Determinar se alguma `tool` precisa ser chamada (ex: `schedule_meeting`).
5.  **`[Execução de Tool + Saída]`**: Se uma `tool` for retornada, ela é executada. A resposta da `tool` (ex: confirmação de agendamento) é formatada e enviada ao usuário.

---

## 6. Conclusão e Recomendações

O principal gargalo é a **recriação constante de agentes e a execução sequencial de operações de I/O e LLM**. A implementação da arquitetura de orquestração paralela proposta, juntamente com a utilização de instâncias singleton para os agentes, irá reduzir drasticamente o tempo de resposta.

**Recomendo fortemente:**

1.  **Não implementar as mudanças diretamente.** Dada a complexidade, sugiro que eu primeiro crie um novo arquivo, por exemplo, `app/refactored_flow.py`, para prototipar o novo fluxo do orquestrador sem quebrar a aplicação atual.
2.  Após a validação do protótipo, podemos integrar as mudanças de forma segura nos arquivos principais.

Este plano de ação, quando implementado, tem o potencial de não apenas atingir a meta de 30-60 segundos, mas de tornar o sistema mais robusto, escalável e eficiente.