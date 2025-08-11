# Análise e Solução para Problemas de Sistema Multi-Usuário

## 1. Diagnóstico do Problema

### 1.1. Comportamento Observado

O agente não responde a mensagens de múltiplos usuários do WhatsApp simultaneamente. Especificamente, quando um segundo usuário tenta interagir, o agente recebe as mensagens, mas não retorna respostas, enquanto a interação com o primeiro usuário continua funcionando normalmente.

### 1.2. Causa Raiz Identificada

A análise do codebase, especialmente em `app/agents/agentic_sdr.py`, revela que a instância do `AgenticSDR` é tratada como um **singleton stateful**. Isso significa que o agente mantém um estado interno (como contexto de conversa, memória, etc.) que é compartilhado entre todas as requisições.

Quando um novo usuário interage, o estado do agente é sobrescrito ou misturado com o contexto do usuário anterior, levando a:
- **Context Bleeding**: Informações de um usuário vazam para a sessão de outro.
- **Inconsistência de Respostas**: O agente tenta responder com base em um contexto misturado ou incorreto.
- **Falha na Resposta**: Em casos de sobreposição crítica, o agente pode falhar completamente em gerar uma resposta coerente ou enviá-la para o usuário correto.

O uso do Supabase para gerenciamento de banco de dados é adequado, mas o problema reside na **gestão do contexto do usuário na camada da aplicação (o agente)**, e não diretamente no banco de dados. O agente não está carregando e salvando o contexto de cada usuário de forma isolada por requisição.

## 2. Solução Proposta: Arquitetura Stateless e Contexto por Requisição

A solução mais inteligente e robusta para este problema é refatorar o `AgenticSDR` para ser **stateless** e garantir que todo o contexto específico do usuário seja carregado do banco de dados (Supabase) no início de cada requisição e salvo de volta ao final.

### 2.1. Princípios da Arquitetura Stateless

- **Isolamento de Sessão**: Cada interação do usuário é tratada de forma independente.
- **Contexto por Requisição**: Todas as informações necessárias para processar uma mensagem (histórico, dados do lead, estado emocional, etc.) são carregadas do Supabase no início da função `process_message` e salvas de volta ao final.
- **Agente Reutilizável**: A instância do `AgenticSDR` em si não armazena dados específicos de um usuário entre as chamadas.

### 2.2. Detalhes da Implementação

#### 2.2.1. Refatorar `AgenticSDR`

O `AgenticSDR` deve ser instanciado ou ter seus métodos chamados de forma que o contexto do usuário seja explicitamente passado e gerenciado.

**Ações:**
- **Remover estado interno persistente**: Quaisquer atributos de instância em `AgenticSDR` que armazenem dados específicos de um usuário (ex: `self.current_lead`, `self.current_conversation`) devem ser removidos ou redefinidos para serem carregados por chamada de método.
- **Passar contexto como argumento**: O método `process_message` (e quaisquer métodos auxiliares que dependam do contexto do usuário) deve receber explicitamente o `lead_data`, `conversation_id`, e o histórico de mensagens como argumentos.

#### 2.2.2. Gerenciamento de Contexto com Supabase

O Supabase já é utilizado para persistência, o que é excelente. A refatoração focará em como os dados são acessados e atualizados.

**Ações:**
- **Carregar Contexto**: No início de `process_message`, carregar o histórico de mensagens (`get_last_100_messages`), dados do lead (`get_lead_by_phone`), e qualquer outro estado relevante do Supabase usando o `phone` ou `conversation_id`.
- **Salvar Contexto**: Após o processamento da mensagem e a geração da resposta, atualizar o `lead_data` e salvar a nova mensagem no histórico do Supabase.

#### 2.2.3. Exemplo de Fluxo Refatorado (`process_message` em `AgenticSDR`)

```python
async def process_message(
    self,
    phone: str,
    message_content: str,
    message_id: str,
    media: Optional[Dict[str, Any]] = None
) -> str:
    # 1. Carregar dados do lead (stateless)
    lead = await supabase_client.get_lead_by_phone(phone)
    if not lead:
        lead = await supabase_client.create_lead({"phone_number": phone, ...})

    # 2. Carregar/criar conversa (stateless)
    conversation = await supabase_client.get_or_create_conversation(phone, lead["id"])

    # 3. Carregar histórico de mensagens (stateless)
    messages_history = await supabase_client.get_conversation_messages(conversation["id"], limit=100)

    # 4. Salvar a nova mensagem do usuário
    await supabase_client.save_message({
        "conversation_id": conversation["id"],
        "content": message_content,
        "role": "user",
        "sender": "user",
        "media_data": {"message_id": message_id, "raw_data": original_message}
    })

    # 5. Preparar contexto para o AGNO Agent (passar tudo como argumento ou contexto)
    # O AGNO AgenticSDR deve ser instanciado por chamada ou ter seus métodos de run/arun
    # recebendo o contexto completo.
    # A IntelligentModelFallback e o Agent (agno.agent.Agent) devem ser instanciados
    # com o modelo e ferramentas, mas sem estado de usuário.
    
    # Exemplo de como o AGNO Agent pode ser usado de forma stateless:
    # self.agent.run(prompt, context={"lead": lead, "history": messages_history, ...})
    
    # 6. Processar com o AGENTIC SDR (agora stateless)
    # A lógica de análise contextual, emocional, etc., usará os dados passados.
    response_text = await self._internal_process_logic(
        phone, message_content, lead, conversation, messages_history, media
    )

    # 7. Salvar a resposta do agente
    await supabase_client.save_message({
        "conversation_id": conversation["id"],
        "content": response_text,
        "role": "assistant",
        "sender": "assistant",
        "media_data": {"agent": "agentic_sdr", "context_analyzed": True}
    })

    return response_text
```

### 2.3. Impacto e Benefícios

- **Suporte Multi-Usuário Real**: O agente poderá lidar com centenas de conversas simultaneamente sem misturar contextos.
- **Escalabilidade Horizontal**: Facilita a execução de múltiplas instâncias do agente, pois não há estado compartilhado.
- **Robustez**: Reduz a chance de bugs relacionados a estado inconsistente.
- **Clareza do Código**: O fluxo de dados se torna mais explícito e fácil de depurar.

## 3. Plano de Ação

1.  **Refatorar `AgenticSDR`**:
    *   Remover todos os atributos de instância que armazenam estado de usuário.
    *   Ajustar métodos para receberem o contexto necessário como argumentos.
2.  **Modificar `app/api/webhooks.py`**:
    *   Ajustar a chamada para `agentic.process_message` para passar todos os dados de contexto necessários.
3.  **Testar Exaustivamente**:
    *   Realizar testes de concorrência com múltiplos usuários simulados.
    *   Verificar a integridade do contexto em cada sessão.

Este plano de ação aborda a causa raiz do problema e levará a um sistema multi-usuário verdadeiramente funcional e escalável.
