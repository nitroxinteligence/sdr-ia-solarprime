
# Análise de Erro: Falha em Cascata - Gemini e OpenAI

## TL;DR (Resumo)

O sistema está enfrentando dois problemas distintos e independentes que ocorrem em sequência:

1.  **Erro de Código na Chamada da API Gemini:** A primeira falha é um `AttributeError` no código Python. A forma como o modelo Gemini está sendo chamado está incorreta. O código tenta usar um método `.run()` que não existe no objeto `Gemini` da biblioteca `agno`, causando o erro inicial.
2.  **Erro de Quota na API da OpenAI:** Após a falha com o Gemini, o sistema corretamente aciona um fallback para o modelo da OpenAI. No entanto, essa chamada também falha, mas por um motivo diferente: um erro `429 insufficient_quota`. Isso significa que a sua conta na OpenAI excedeu a cota de uso disponível (créditos acabaram ou o limite de gastos foi atingido).

Abaixo está a análise detalhada de cada problema e as etapas para corrigi-los.

---

## Problema 1: Erro na Chamada da API Gemini (O Erro Original)

### Log de Erro Relevante:

```
2025-08-04 21:21:30.875 | ERROR    | app.utils.retry_handler:wrapper:103 | ❌ _gemini_call_with_retry failed with non-retryable error: 'Gemini' object has no attribute 'run'
```

### Análise Técnica:

Este erro é um `AttributeError` do Python. Ele indica que o código tentou executar o método `run` em um objeto da classe `Gemini`, mas essa classe não possui um método com este nome.

Analisando o arquivo `app/agents/agentic_sdr.py`, a classe `IntelligentModelFallback` é responsável por gerenciar os modelos. Dentro dela, o método `_gemini_call_with_retry` corretamente usa `self.primary_model.invoke(...)`. No entanto, a forma como o agente principal (`self.agent`) é instanciado em `_create_agentic_agent` parece ser a causa do problema:

```python
# Em app/agents/agentic_sdr.py -> _create_agentic_agent()

self.agent = Agent(
    name="AGENTIC SDR",
    model=self.intelligent_model.current_model, # <--- PROBLEMA AQUI
    instructions=enhanced_prompt,
    # ...
)
```

O `Agent` do framework AGNO espera um objeto de modelo que ele possa executar (provavelmente chamando um método `.run()` ou `.invoke()`). Ao passar `self.intelligent_model.current_model`, você está passando o objeto `Gemini` diretamente para o `Agent`. A biblioteca `agno` parece tentar chamar o método `.run()` por padrão, que não existe no objeto `Gemini` (que usa `.invoke()`).

### Solução Recomendada:

A solução é passar o *wrapper* (`self.intelligent_model`) inteiro para o `Agent`, em vez do modelo bruto. O wrapper `IntelligentModelFallback` já possui um método `run`, que lida com a lógica de chamar `invoke` para o Gemini ou `run` para o OpenAI.

**Ação Corretiva:**

Modifique a instanciação do `Agent` no arquivo `app/agents/agentic_sdr.py` para que o `Agent` interaja com o seu wrapper, e não diretamente com o modelo.

1.  **Abra o arquivo**: `app/agents/agentic_sdr.py`
2.  **Localize o método**: `_create_agentic_agent`
3.  **Altere a linha de instanciação do `Agent` de:**
    ```python
    model=self.intelligent_model.current_model,
    ```
    **Para:**
    ```python
    model=self.intelligent_model,
    ```

Isso fará com que o `Agent` chame `self.intelligent_model.run()`, que por sua vez executará a lógica correta de retry e fallback, chamando `gemini.invoke()` internamente.

---

## Problema 2: Erro de Quota na API da OpenAI (O Erro de Fallback)

### Log de Erro Relevante:

```
2025-08-04 21:21:31.281 | ERROR    | ... | OpenAI o3-mini falhou: API Error 429: {
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details...",
        "type": "insufficient_quota",
        ...
        "code": "insufficient_quota"
    }
}
```

### Análise Técnica:

Este erro é claro e vem diretamente da API da OpenAI.

*   **Código de Status `429`**: Significa "Too Many Requests", mas o corpo do erro especifica a causa real.
*   **`"type": "insufficient_quota"`**: Este é o ponto crucial. Indica que a chave de API (`OPENAI_API_KEY`) é válida, mas a conta associada a ela não tem mais créditos ou atingiu o limite de gastos definido.

Isso **não é um erro de código**. O sistema de fallback funcionou como esperado, mas foi bloqueado pela OpenAI por uma questão de faturamento/créditos.

### Solução Recomendada:

Você precisa verificar o status da sua conta na plataforma da OpenAI.

**Ação Corretiva:**

1.  Acesse o site da OpenAI: [https://platform.openai.com/](https://platform.openai.com/)
2.  Faça login na conta associada à sua chave de API.
3.  Navegue até a seção **"Billing"** (Faturamento).
4.  Verifique seu saldo de créditos ("Usage") e seus limites de gastos ("Usage limits").
5.  **Ação Provável**: Você precisará adicionar um método de pagamento ou aumentar seu limite de gastos para que as chamadas da API voltem a funcionar.

Para mais detalhes sobre este tipo de erro, a própria OpenAI fornece documentação: [OpenAI Error Codes](https://platform.openai.com/docs/guides/error-codes/api-errors)

---

## Conclusão e Próximos Passos

O sistema falhou devido a uma cadeia de dois eventos infelizes: um bug de implementação local seguido por um problema de faturamento com o serviço de fallback.

Para resolver completamente o problema, siga estes passos:

1.  **Corrija o Código:** Altere a linha `model=self.intelligent_model.current_model` para `model=self.intelligent_model` no arquivo `app/agents/agentic_sdr.py`.
2.  **Resolva a Quota da OpenAI:** Acesse sua conta OpenAI e verifique seu plano e detalhes de faturamento para garantir que há créditos ou limites suficientes para as chamadas da API.

Após realizar essas duas ações, o sistema deve voltar a operar corretamente, primeiro tentando o Gemini (agora com a chamada correta) e, se necessário, usando o fallback da OpenAI (que estará com a quota liberada).
