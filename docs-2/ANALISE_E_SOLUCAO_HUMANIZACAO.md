# Análise Detalhada e Solução para Humanização do Agente

## 1. Introdução

Este documento detalha a análise e a solução para dois problemas críticos que afetam a humanização e a eficácia do agente de IA:

1.  **Quebra de Linha Indevida**: O agente gera respostas com \
, resultando em múltiplas mensagens no WhatsApp em vez de uma única mensagem fluida.
2.  **Uso de Placeholders**: O agente utiliza placeholders como `[Seu Nome]`, o que quebra a imersão e a percepção de estar conversando com um humano.

A solução proposta visa corrigir esses problemas de forma robusta, combinando melhorias no prompt do agente e salvaguardas no código da aplicação.

---


## 2. Problema 1: Quebra de Linha Indevida (`\
`)

### 2.1. Análise da Causa Raiz

O problema ocorre porque o agente, ao gerar o texto da resposta, inclui caracteres de nova linha (`\
`). O sistema atual, em `app/api/webhooks.py`, só aciona o `MessageSplitter` para mensagens com mais de 150 caracteres (`settings.message_max_length`).

Se uma resposta gerada tem, por exemplo, 100 caracteres mas contém `\
`, ela não passa pelo `MessageSplitter` e é enviada diretamente para a API do WhatsApp. O WhatsApp, por sua vez, interpreta o `\
` e divide o texto em balões de mensagem separados, resultando na experiência fragmentada vista na imagem.

A instrução no `prompt-agente.md` para não usar quebras de linha é um bom primeiro passo, mas não é uma garantia, pois o LLM pode ocasionalmente falhar em seguir todas as diretrizes de formatação.

### 2.2. Solução Proposta (Dupla Camada)

Para garantir que o problema seja resolvido de forma definitiva, aplicaremos uma solução em duas camadas:

#### **Camada 1: Reforço no Prompt**

A instrução no `prompt-agente.md` será reforçada e movida para uma posição de maior destaque, tornando-a uma diretriz inegociável para o agente.

**Modificação Sugerida em `app/prompts/prompt-agente.md`:**

Adicionar no início do prompt, sob a seção `DIRETRIZES OPERACIONAIS INDERROGÁVEIS`:

```markdown
### 🚨 FORMATAÇÃO OBRIGATÓRIA DE MENSAGENS 🚨

**REGRA ABSOLUTA: TODA SUA RESPOSTA DEVE SER UM TEXTO CONTÍNUO SEM QUEBRAS DE LINHA!**

O sistema de Message Splitter cuidará automaticamente de dividir mensagens longas. Você deve:

- ✅ Escrever TUDO em um único parágrafo contínuo.
- ✅ Usar espaços simples entre frases, não quebras de linha (`\
`).
- ✅ Consolidar TODO seu pensamento em texto fluido.
- ❌ **NUNCA** usar Enter ou quebras de linha (`\
`) entre frases.
- ❌ **NUNCA** separar frases com linhas em branco.
- ❌ **NUNCA** simular múltiplos envios.

**Exemplo CORRETO (tudo em uma linha):**
`Oii!! Meu nome é Helen Vieira. Sou consultora especialista aqui da SolarPrime em Recife. Antes de começarmos, como posso te chamar?`

**Exemplo INCORRETO (com quebras - NUNCA FAÇA ISSO):**
`Oii! Seja muito bem-vindo à Solar Prime!

Meu nome é Helen Vieira.`

**⚠️ ATENÇÃO: Se você usar quebras de linha, as mensagens aparecerão separadas no WhatsApp!**
```

#### **Camada 2: Salvaguarda no Código (Garantia de 100%)**

Para eliminar completamente a possibilidade do erro ocorrer, adicionaremos uma linha de código em `app/api/webhooks.py` que remove programaticamente quaisquer quebras de linha da resposta do agente antes de enviá-la.

**Modificação Sugerida em `app/api/webhooks.py`:**

No método `process_message_with_agent`, logo após receber a resposta do agente e antes de verificar o `MessageSplitter`, adicione a seguinte linha:

```python
# ... (após receber a resposta do agente)

if isinstance(response, dict):
    response_text = response.get("text", "")
    # ...
else:
    response_text = response

# ===== LINHA A SER ADICIONADA =====
# Garante que não haverá quebras de linha, substituindo-as por espaços.
response_text = response_text.replace('\n', ' ').strip()
# ===================================

emoji_logger.webhook_process(f"Resposta recebida do AGENTIC SDR: {response_text[:100] if response_text else 'NENHUMA'}...")

# Se o splitter está habilitado e a mensagem é longa, divide em chunks
if settings.enable_message_splitter and len(response_text) > settings.message_max_length:
    # ... (resto do código)
```

Esta abordagem garante que, mesmo que o LLM falhe em seguir o prompt, o sistema corrigirá a formatação antes do envio, resolvendo o problema de forma definitiva.

---


## 3. Problema 2: Uso de Placeholders (`[Seu Nome]`)

### 3.1. Análise da Causa Raiz

O agente está utilizando placeholders como `[Seu Nome]` porque está imitando os exemplos fornecidos em seu prompt principal, `app/prompts/prompt-agente.md`. O prompt utiliza esses placeholders para generalizar os exemplos de diálogo.

O agente, em vez de entender que `[NOME]` deve ser substituído pelo nome real do lead (disponível no contexto), está tratando o placeholder como texto literal a ser reproduzido.

### 3.2. Solução Proposta

A solução consiste em refatorar o prompt para que ele seja mais "humano" em seus próprios exemplos e instruir o agente a usar os dados reais do contexto.

#### 1. Refatoração dos Exemplos no Prompt

Todos os exemplos em `app/prompts/prompt-agente.md` que usam placeholders devem ser substituídos por nomes e valores concretos e realistas.

**Exemplo de Modificação em `app/prompts/prompt-agente.md`:**

**Antes:**
`"Muito prazer em conhecê-la, [NOME]. me conte... você está buscando uma forma de economizar na sua energia ou tem interesse em instalar uma usina solar?"`

**Depois:**
`"Muito prazer em conhecê-la, Maria. Me conte, você está buscando uma forma de economizar na sua energia ou tem interesse em instalar uma usina solar?"`

**Antes:**
`"[NOME], com uma conta de *R$[VALOR]*, nossa solução traz desconto de *20%*..."`

**Depois:**
`"Maria, com uma conta de *R$ 6.000*, nossa solução traz desconto de *20%*..."`

#### 2. Adicionar Instrução Explícita Anti-Placeholder

Incluir uma regra clara na seção de "O QUE VOCÊ NUNCA DEVE FAZER" do prompt.

**Modificação Sugerida em `app/prompts/prompt-agente.md`:**

```markdown
### PLACEHOLDERS
- Substitua todos os placeholders por informações reais.
- **NUNCA** use placeholders como `[Nome]`, `[Valor]`, etc. em suas respostas. Utilize sempre os dados reais do lead fornecidos no contexto da conversa.
```

#### 3. Garantir o Uso do Contexto

O agente já recebe `lead_data` no método `process_message`. A solução é garantir que o prompt o instrua a usar esses dados. A refatoração dos exemplos (item 1) já incentiva esse comportamento, pois o agente verá exemplos com nomes e valores reais, o que o levará a buscar informações similares no contexto para construir suas respostas.

---


## 4. Conclusão

A implementação dessas duas soluções resolverá os problemas de forma abrangente:

1.  **As quebras de linha serão eliminadas**, garantindo que as mensagens sejam enviadas como um único bloco de texto coeso, melhorando a fluidez da conversa.
2.  **O uso de placeholders será erradicado**, substituído pelo uso de dados reais do lead, o que aumentará drasticamente a percepção de humanização e personalização do agente.

O resultado será um agente de IA que se comunica de forma mais natural, profissional e, acima de tudo, humana, alinhado com os objetivos do projeto SolarPrime.
