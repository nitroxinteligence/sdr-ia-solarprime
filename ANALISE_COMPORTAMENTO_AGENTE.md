# Análise de Comportamento e Otimização do Agente SDR

## 1. Diretrizes Fundamentais de Comportamento (Simplificado)

O comportamento do agente deve ser direto, eficiente e focado na simplicidade para garantir robustez e evitar complexidade desnecessária. As seguintes regras são mandatórias:

### 1.1. Interação Inicial e Apresentação
- **Primeiro Contato**: O agente deve se apresentar como "Helen" da SolarPrime **apenas e somente na primeira mensagem** trocada com um novo lead.
- **Contatos Subsequentes**: Se o lead já existe e possui um histórico de mensagens, o agente **NÃO DEVE** se apresentar novamente. Em vez disso, deve analisar o histórico de mensagens no Supabase e retomar a conversa de forma contextual e natural.

### 1.2. Consulta Obrigatória à Base de Dados
- **Consulta ao Histórico**: Para **TODA** interação, o agente deve primeiro consultar o histórico de mensagens do lead no Supabase para obter o contexto completo da conversa.
- **Consulta à Base de Conhecimento**: Para **TODA** resposta, o agente deve obrigatoriamente consultar a tabela `knowledge_base` no Supabase para enriquecer sua resposta com informações precisas e atualizadas sobre produtos, serviços, objeções comuns, etc.

### 1.3. Princípio da Simplicidade
- **Soluções Simples**: Todas as implementações devem seguir o princípio de "o básico funciona sempre". Evitar complexidade, múltiplas camadas de abstração ou lógica excessivamente reativa.
- **Foco no Essencial**: As modificações devem se concentrar em cumprir os requisitos acima, sem introduzir funcionalidades que não sejam estritamente necessárias e sem quebrar o que já existe.

## 2. Plano de Ação (Implementação Simplificada)

Para alinhar o agente com as novas diretrizes, as seguintes modificações serão realizadas, mantendo o foco na simplicidade.

### 2.1. Refatoração do `app/agents/agentic_sdr.py`

O arquivo `agentic_sdr.py` será o ponto central da modificação. A lógica de processamento de mensagens (`process_message`) será ajustada para seguir um fluxo procedural e direto.

**Lógica Proposta:**

1.  **Verificação de Novo Lead**:
    - Dentro de `process_message`, antes de gerar qualquer resposta, verificar se a conversa é nova (ou seja, se o histórico de mensagens está vazio ou contém apenas a primeira mensagem do lead).
    - Uma função simples como `_is_first_contact(conversation_history)` retornará `True` ou `False`.

2.  **Construção do Contexto Obrigatório**:
    - **Sempre** chamar `get_last_100_messages` para obter o histórico.
    - **Sempre** chamar `search_knowledge_base` com a mensagem atual do usuário como `query`.

3.  **Geração da Resposta Condicional**:
    - Se `_is_first_contact` for `True`, o prompt enviado ao LLM incluirá a instrução para se apresentar.
    - Se `_is_first_contact` for `False`, o prompt instruirá o LLM a continuar a conversa, usando o histórico e o conhecimento da base de dados.
    - O resultado da `search_knowledge_base` será sempre injetado no prompt com a instrução: "Use a informação abaixo para formular sua resposta".

**Exemplo de Lógica Simplificada em `process_message`:**

```python
# Dentro de AgenticSDR.process_message

# 1. Obter contexto obrigatório
message_history = await self.get_last_100_messages(phone)
knowledge_results = await self.search_knowledge_base(query=message)
is_new_lead = len(message_history) <= 1

# 2. Construir o prompt dinamicamente
prompt_context = f"Contexto da Base de Conhecimento: {knowledge_results}\n\nHistórico da Conversa:\n{message_history}"

if is_new_lead:
    final_prompt = f"{prompt_context}\n\nINSTRUÇÃO: Você é a Helen. Apresente-se e inicie a conversa."
else:
    final_prompt = f"{prompt_context}\n\nINSTRUÇÃO: Você é a Helen. Continue a conversa a partir do histórico."

# 3. Gerar resposta
response = await self.agent.arun(final_prompt)
```

### 2.2. Garantia de Simplicidade
- **Sem Novos Agentes**: Nenhuma nova classe de agente ou serviço complexo será criada. A lógica será contida dentro do `AgenticSDR`.
- **Busca Direta**: A busca na `knowledge_base` continuará usando `ILIKE` por simplicidade, conforme o princípio de não adicionar complexidade desnecessária (como embeddings) a menos que se prove essencial.
- **Prompt Direto**: O prompt será modificado para ser mais direto e imperativo, removendo ambiguidades.

## 3. Conclusão

Esta abordagem garante que o agente siga as novas diretrizes de forma robusta e confiável. Ao forçar a consulta ao histórico e à base de conhecimento em todas as interações e ao controlar a apresentação inicial, o comportamento do agente se tornará mais consistente e alinhado com os objetivos de negócio, sem introduzir complexidade que possa comprometer a estabilidade do sistema.