# Relatório de Implementação: Saudações Contextuais por Período do Dia

## 1. Objetivo

Tornar o agente de IA mais humano e natural, capacitando-o a usar saudações apropriadas como "Bom dia", "Boa tarde" e "Boa noite" com base no horário atual do dia.

## 2. Análise da Arquitetura Atual

A análise do código, em especial dos arquivos `app/agents/agentic_sdr.py` e `app/config.py`, revela os seguintes pontos-chave:

*   **Timezone Configurado**: O arquivo `app/config.py` já possui uma configuração de `timezone` (padrão: `America/Sao_Paulo`). Isso é fundamental, pois garante que o agente opere no fuso horário correto, independentemente de onde o servidor está localizado.

*   **Contexto do Agente**: O `AgenticSDR` em `app/agents/agentic_sdr.py` já possui um dicionário de `context` que é passado para o `Agent` da AGNO. Atualmente, ele inclui `current_time` e `day_of_week`.

    ```python
    # Em app/agents/agentic_sdr.py
    self.agent = Agent(
        # ...
        context={
            "emotional_state": self.emotional_state.value,
            "cognitive_load": self.cognitive_load,
            "current_time": datetime.now().strftime("%H:%M"),
            "day_of_week": datetime.now().strftime("%A")
        }
    )
    ```

*   **Prompt do Agente**: O arquivo `app/prompts/prompt-agente.md` já contém exemplos de saudações que variam com o horário, como:

    ```markdown
    **Variações por horário**:
    - Manhã: "Oi! Bom dia! Tudo bem?"
    - Tarde: "Oi! Boa tarde! Como está seu dia?"
    ```

Esta estrutura é excelente e nos fornece o local perfeito para injetar a informação do período do dia (Manhã, Tarde, Noite) de forma simples e eficaz.

## 3. Plano de Implementação

A melhor abordagem é aprimorar o contexto que já é passado para o agente, adicionando uma nova chave, `period_of_day`, que conterá o valor "Manhã", "Tarde" ou "Noite".

### Passo 1: Criar uma Função Utilitária (Recomendado)

Para manter o código limpo e reutilizável, criaremos uma função auxiliar em um arquivo de utilitários, como `app/utils/time_utils.py` (se não existir, pode ser criado). Esta função determinará o período do dia.

**Arquivo Sugerido: `app/utils/time_utils.py`**
```python
from datetime import datetime
import pytz

def get_period_of_day(timezone: str = "America/Sao_Paulo") -> str:
    """
    Retorna o período do dia (Manhã, Tarde, Noite) baseado no fuso horário.
    """
    try:
        tz = pytz.timezone(timezone)
        current_hour = datetime.now(tz).hour

        if 5 <= current_hour < 12:
            return "Manhã"
        elif 12 <= current_hour < 18:
            return "Tarde"
        else:
            return "Noite"
    except Exception:
        # Fallback em caso de erro de timezone
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            return "Manhã"
        elif 12 <= current_hour < 18:
            return "Tarde"
        else:
            return "Noite"

```

### Passo 2: Modificar o `AgenticSDR` para Incluir o Período do Dia no Contexto

Agora, modificaremos o `_create_agentic_agent` em `app/agents/agentic_sdr.py` para usar a nova função e adicionar a informação ao contexto do agente.

**Modificação em `app/agents/agentic_sdr.py`:**

```python
# Importar a nova função no início do arquivo
from app.utils.time_utils import get_period_of_day

# ... dentro da classe AgenticSDR ...

def _create_agentic_agent(self):
    """Cria o agente AGENTIC SDR com personalidade completa"""
    
    # ... (código existente para carregar o prompt)

    # Obter o período do dia atual
    current_period = get_period_of_day(settings.timezone)

    self.agent = Agent(
        name="AGENTIC SDR",
        model=self.intelligent_model,
        instructions=enhanced_prompt,
        tools=self.tools,
        memory=self.memory,
        knowledge=self.knowledge,
        show_tool_calls=True,
        markdown=True,
        debug_mode=settings.debug,
        # Contexto agora inclui o período do dia
        context={
            "emotional_state": self.emotional_state.value,
            "cognitive_load": self.cognitive_load,
            "current_time": datetime.now().strftime("%H:%M"),
            "day_of_week": datetime.now().strftime("%A"),
            "period_of_day": current_period  # <-- NOVA CHAVE ADICIONADA
        }
    )
```

### Passo 3: Atualizar o Prompt para Usar o Novo Contexto

Finalmente, atualizaremos o `prompt-agente.md` para instruir o agente a usar a nova variável de contexto `period_of_day`.

**Modificação Sugerida em `app/prompts/prompt-agente.md`:**

```markdown
## 💬 FLUXO CONVERSACIONAL HUMANIZADO (8 ESTÁGIOS)

### ESTÁGIO 0 - ABERTURA NATURAL
**Objetivo**: Quebrar gelo e coletar nome

**Instrução de Saudação**: Use a variável de contexto `{period_of_day}` para iniciar a conversa com a saudação correta (Bom dia, Boa tarde, Boa noite).

**Exemplo de Resposta (usando o contexto):**
`"Oi! Bom {period_of_day}! Tudo bem? Meu nome é Helen Vieira, sou consultora especialista aqui da Solar Prime em Recife. Antes de começarmos, como posso te chamar?"`

**Variações por horário (Exemplos para o Agente):**
- Manhã: "Oi! Bom dia! Tudo bem?"
- Tarde: "Oi! Boa tarde! Como está seu dia?"
- Noite: "Oi! Boa noite! Espero que seu dia tenha sido bom."
```

## 4. Vantagens desta Abordagem

*   **Simplicidade e Baixo Risco**: A implementação é feita em um local centralizado (`_create_agentic_agent`) e reutiliza a estrutura de contexto já existente, minimizando o risco de introduzir bugs.
*   **Manutenibilidade**: A lógica para determinar o período do dia fica isolada em uma função utilitária, facilitando futuras manutenções ou ajustes (ex: alterar os horários que definem "tarde").
*   **Eficácia**: Passar a informação diretamente no contexto do agente é a forma mais eficaz de garantir que ele a utilize, pois se torna uma variável disponível em todas as suas execuções.
*   **Humanização**: O agente não apenas "sabe" o período do dia, mas é instruído a usá-lo ativamente, o que resultará em saudações mais naturais e contextuais, melhorando significativamente a experiência do usuário.

## 5. Próximos Passos

1.  Criar o arquivo `app/utils/time_utils.py` com a função `get_period_of_day`.
2.  Modificar o arquivo `app/agents/agentic_sdr.py` para importar e usar a nova função, adicionando `period_of_day` ao contexto do agente.
3.  Atualizar o `app/prompts/prompt-agente.md` com as novas instruções e exemplos.

Com estas modificações, o agente terá a capacidade de saudar os usuários de forma contextual e humanizada, alinhado com os objetivos do projeto.
