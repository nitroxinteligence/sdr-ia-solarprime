#  relatório de diagnóstico e solução: erros de formatação e comportamento do agente

**documento:** `DIAGNOSTICO_E_SOLUCAO_FORMATACAO_AGENTE.md`  
**versão:** 2.0  
**data:** 07/08/2025  
**autor:** engenharia sênior

---

## 1. resumo executivo

A análise do diálogo fornecido e do código-fonte em `@app/**` revela três categorias principais de erros que degradam a performance e a humanização do agente "helen vieira":

1.  **vazamento de formatação da base de conhecimento:** o agente está extraindo conteúdo da tabela `knowledge_base` e o inserindo diretamente na resposta, sem reformatar, o que viola as regras de estilo do whatsapp (uso de `**negrito**` em vez de `*negrito*`, enumerações, etc.).
2.  **falha na sanitização do output:** a camada final de processamento de texto, antes do envio, não está tratando adequadamente a formatação incorreta, permitindo que emojis e markdown inválido cheguem ao usuário. (EMOJI DEVEM SER APENAS NAS REAÇÕES)
3.  **quebra inadequada de mensagens:** o `messagesplitter` está interpretando quebras de linha no output do agente como um sinal para enviar múltiplas mensagens, resultando em uma experiência de usuário fragmentada e robótica.

Estes problemas indicam uma falha no ciclo de vida do processamento da resposta: o agente não adere estritamente às suas instruções de formatação ao usar dados de fontes externas, e os mecanismos de segurança (sanitização e splitting) não são robustos o suficiente para corrigir essas falhas.

---

## 2. diagnóstico detalhado por erro

### 2.1. erro 1: uso de emojis, enumerações e markdown incorreto

-   **sintoma:** a mensagem enviada ao usuário contém emojis (✍️, ), enumerações (`1.`, `2.`, `3.`) e markdown de negrito com duplo asterisco (`**grátis**`).
-   **causa raiz:** sua suspeita está correta. O `agenticsdr` utiliza a ferramenta `search_knowledge_base` para obter informações sobre os diferenciais da empresa. A análise do `app/services/knowledge_service.py` e do `app/agents/agentic_sdr.py` mostra o seguinte fluxo:
    1.  o agente busca por um `query` na `knowledge_base`.
    2.  o `knowledgeservice` retorna o campo `content` da tabela.
    3.  **ponto da falha:** o agente, ao construir a resposta, incorpora o texto de `content` diretamente, sem reprocessá-lo ou reformatá-lo. Se o texto no banco de dados contiver `1. **garantia...**`, o agente o utiliza literalmente.
-   **violação de prompt:** isso viola diretamente a seção do `prompt-agente.md` que instrui: "*para negrito no whatsapp use apenas um asterisco: `*texto em negrito*`*" e "*nunca use listas numeradas*."

### 2.2. erro 2: envio de múltiplas mensagens curtas

-   **sintoma:** a resposta é dividida em múltiplos balões de mensagem no whatsapp, um para cada item da lista.
-   **causa raiz:** o `app/services/message_splitter.py` é projetado para dividir mensagens longas. No entanto, se ele recebe uma string contendo caracteres de nova linha (`\n`), ele pode interpretar isso como uma instrução para dividir a mensagem, mesmo que os trechos individuais sejam curtos. O agente está gerando um output com quebras de linha, que são então processadas pelo `webhook` e enviadas ao `messagesplitter`.
-   **ponto da falha:** a função `process_message_with_agent` em `app/api/webhooks.py` possui uma lógica de sanitização:

    ```python
    # app/api/webhooks.py
    response_text = response_text.replace('\n', ' ').replace('\r', ' ').strip()
    response_text = ' '.join(response_text.split())
    ```

    Esta lógica deveria prevenir o problema, o que indica que ela pode não estar sendo aplicada corretamente a todos os caminhos de resposta ou que o `messagesplitter` está sendo invocado antes desta sanitização em alguns fluxos. Uma análise mais profunda no `webhooks.py` mostra que a sanitização é feita, mas o `messagesplitter` é chamado *depois*. O problema é que a sanitização junta tudo com espaços, mas se a fonte (da `knowledge_base`) já tem a numeração, ela permanece.

### 2.3. erro 3: uso de emojis

-   **sintoma:** a resposta contém emojis como ✍️ e .
-   **causa raiz:** PRECISAMOS IDENTIFICAR. NO PROMPT PRINCIPAL DO AGENTE JÁ ESTÁ BEM SINALIZADO PARA NAO UTILIZAR EMOJIS, MAS O AGENTE CONTINUA.

---

## 3. plano de ação para correção

A solução requer uma abordagem em três camadas para garantir robustez, mesmo que uma das camadas falhe.

### camada 1: fortalecer o prompt do agente (instrução)

Vamos reforçar o `prompt-agente.md` com uma regra explícita e inequívoca sobre como lidar com informações de ferramentas e da base de conhecimento.

-   **arquivo a ser modificado:** `app/prompts/prompt-agente.md`
-   **ação:** adicionar uma nova regra crítica na seção 2 (regras operacionais).

```xml
<rule priority="critical" name="tratamento_de_dados_externos">
- ao usar informações de ferramentas ou da base de conhecimento, você nunca deve copiar o conteúdo diretamente.
- você deve sempre reescrever e reformatar a informação com suas próprias palavras, seguindo o tom de helen vieira e as regras de formatação do whatsapp (*negrito*, sem emojis, sem enumerações).
- trate os dados da knowledge_base como uma fonte de informação, não como um texto pronto para ser enviado.
</rule>
```

### camada 2: sanitização de saída agressiva (validação)

Esta é a correção mais importante e eficaz. Vamos criar uma função de sanitização mais poderosa em `app/api/webhooks.py` para limpar o texto final *antes* de ser enviado ao `messagesplitter` e à `evolutionapi`. Esta função irá **remover toda e qualquer formatação**, garantindo que apenas texto puro seja enviado.

-   **arquivo a ser modificado:** `app/api/webhooks.py`
-   **ação:** criar uma nova função `sanitize_final_response` e usá-la para processar `response_text`.

```python
# nova função em app/api/webhooks.py
import re

def sanitize_final_response(text: str) -> str:
    """
    sanitiza agressivamente o texto final para garantir conformidade total com as regras de formatação do whatsapp, removendo todo o markdown e emojis.
    """
    if not isinstance(text, str):
        return ""

    # 1. remover emojis (padrão unicode abrangente)
    emoji_pattern = re.compile("["
                               u"\U0001f600-\U0001f64f"  # emoticons
                               u"\U0001f300-\U0001f5ff"  # symbols & pictographs
                               u"\U0001f680-\U0001f6ff"  # transport & map symbols
                               u"\U0001f1e0-\U0001f1ff"  # flags (ios)
                               u"\u2600-\u26ff"          # miscellaneous symbols
                               u"\u2700-\u27bf"          # dingbats
                               u"\u2300-\u23ff"          # misc technical
                               u"\ufe0f"                # variation selector
                               u"\u200d"                # zero width joiner
                               "]+", flags=re.unicode)
    text = emoji_pattern.sub(r'', text)

    # 2. remover todo o markdown (negrito, itálico, etc.)
    # remove *, **, _, __, ~, `,
etc.
    text = re.sub(r'[\*\_\~\`]', '', text)

    # 3. remover enumerações e juntar linhas
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # remove padrões como "1. ", "- ", "* " no início da linha
        cleaned_line = re.sub(r'^\s*\d+\.\s*|^\s*[-*]\s*', '', line.strip())
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    text = ' '.join(cleaned_lines)

    # 4. remover espaços duplos
    text = ' '.join(text.split())

    return text

# modificar a função process_message_with_agent para usar a nova função
# ...
response_text = extract_final_response(response_text)
response_text = sanitize_final_response(response_text) # <--- aplicar nova sanitização
# ...
```

### camada 3: limpeza da fonte de dados (prevenção)

A solução mais robusta a longo prazo é garantir que os dados na `knowledge_base` já estejam limpos. Isso evita que o agente tenha que corrigir a formatação em primeiro lugar.

-   **ação:** criar um script de manutenção (`scripts/clean_knowledge_base.py`) para ser executado uma vez, que irá varrer a tabela `knowledge_base` e aplicar a mesma lógica de sanitização do passo anterior, salvando o conteúdo limpo de volta no banco.
-   **benefício:** isso garante que, mesmo que as camadas 1 e 2 falhem, a fonte dos dados já é segura, prevenindo a recorrência do problema.

---

## 4. próximos passos

1.  **implementar a camada 2 (sanitização rigorosa):** modificar imediatamente o `app/api/webhooks.py` para incluir a função `sanitize_final_response`. esta é a correção mais rápida e eficaz para o problema visível ao usuário.
2.  **implementar a camada 1 (fortalecer o prompt):** atualizar o `app/prompts/prompt-agente.md` para incluir a nova regra de tratamento de dados externos.
3.  **desenvolver e executar o script da camada 3 (limpeza da fonte):** criar e executar o script para limpar a tabela `knowledge_base`, garantindo a integridade dos dados na fonte.
