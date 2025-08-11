# Análise e Solução Inteligente para o Erro 500 da API Gemini

## 1. Diagnóstico do Problema

O erro `ERROR Error from Gemini API: 500 INTERNAL` que você está observando em produção indica um problema interno nos servidores do Google. **Este não é um erro no seu código, na sua chave de API ou na sua configuração.** É uma falha temporária do lado da API da Gemini, que pode ocorrer por diversos motivos, como sobrecarga de serviço, manutenção ou outros problemas transitórios na infraestrutura do Google.

O log `Attempt 1/1 failed` e `Failed after 1 attempts` é a pista mais importante: sua aplicação está tentando fazer a chamada uma única vez e, ao receber o erro 500, ela falha imediatamente.

Uma aplicação robusta e pronta para produção deve antecipar e gerenciar essas falhas de serviço externas de forma inteligente.

## 2. Causas Comuns para o Erro 500 da API Gemini

- **Sobrecarga Temporária:** O serviço pode estar recebendo um volume de requisições maior do que o normal.
- **Manutenção ou Atualização:** O Google pode estar realizando manutenções ou atualizações nos servidores que atendem a API.
- **Problema de Roteamento ou Rede Interna:** Falhas na comunicação interna da infraestrutura do Google.
- **Input Complexo ou Longo:** Em casos raros, um prompt excessivamente longo ou complexo pode sobrecarregar o modelo de uma maneira que gera um erro interno, embora isso geralmente resulte em outros tipos de erro.

## 3. Estratégia de Solução Inteligente

A abordagem correta não é evitar o erro, mas sim construir um sistema resiliente que o trate de forma adequada. Nossa estratégia será baseada em 3 pilares:

1.  **Retentativas (Retry) com Backoff Exponencial:** Em vez de tentar apenas uma vez, vamos implementar um mecanismo que tenta novamente a requisição em caso de falha. O "backoff exponencial" significa que o tempo de espera entre as tentativas aumenta a cada falha, evitando sobrecarregar ainda mais a API.
2.  **Fallback (Plano B):** Se todas as tentativas falharem, a aplicação não deve quebrar. Ela deve ter um "plano B", como registrar o erro de forma detalhada e, se possível, responder ao usuário com uma mensagem de que o serviço está temporariamente indisponível.
3.  **Logging Aprimorado:** Melhorar o log para capturar o contexto completo da falha, facilitando a depuração futura.

## 4. Plano de Implementação Passo a Passo

### Passo 1: Implementar um Mecanismo de Retry Robusto

Vamos aprimorar ou criar um utilitário de retry. A biblioteca `tenacity` é excelente para isso e provavelmente já está no seu ambiente ou pode ser facilmente adicionada em `requirements.txt`.

**Ação:** Verifique o arquivo `app/utils/gemini_retry.py`. Se ele não existir ou for simples, substitua-o pelo código abaixo, que utiliza `tenacity`.

```python
# /app/utils/gemini_retry.py

import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions

# Configurando o logger para este módulo
logger = logging.getLogger(__name__)

# Definindo os tipos de exceção específicos da API Gemini que queremos tratar.
# O erro 500 é geralmente encapsulado em google.api_core.exceptions.InternalServerError
RETRYABLE_EXCEPTIONS = (
    google.api_core.exceptions.InternalServerError,  # Erro 500
    google.api_core.exceptions.ResourceExhausted,    # Erro 429 (Too Many Requests)
    google.api_core.exceptions.ServiceUnavailable,   # Erro 503
    google.api_core.exceptions.DeadlineExceeded,     # Erro 504
)

def log_retry_attempt(retry_state):
    """Função para logar cada tentativa de retry."""
    logger.warning(
        f"Gemini API request failed, attempt {retry_state.attempt_number}. "
        f"Retrying in {retry_state.next_action.sleep:.2f} seconds. "
        f"Reason: {retry_state.outcome.exception()}"
    )

# Criando o decorador de retry principal
gemini_api_retry = retry(
    # Define as exceções que acionarão o retry
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    # Define a estratégia de espera: começa com 1s e cresce exponencialmente até no máximo 60s
    wait=wait_exponential(multiplier=1, min=2, max=60),
    # Define o número máximo de tentativas
    stop=stop_after_attempt(5),
    # Função a ser chamada antes de cada tentativa
    before_sleep=log_retry_attempt
)

```

**Adicione `tenacity` ao seu `requirements.txt` se não estiver lá:**

```
tenacity
```

### Passo 2: Integrar o Decorador de Retry no `agentic_sdr.py`

Agora, vamos aplicar este decorador à função que efetivamente faz a chamada para a API Gemini. Pelo log de erro (`Erro em AGENTIC SDR`), o local provável é o `app/agents/agentic_sdr.py`.

**Ação:** Encontre a função que chama `model.generate_content` e adicione o decorador `@gemini_api_retry` a ela.

```python
# /app/agents/agentic_sdr.py (Exemplo)

# ... outros imports
from app.utils.gemini_retry import gemini_api_retry
from app.utils.logger import log_with_emoji
import google.api_core.exceptions

# ... (corpo do arquivo)

class AgenticSDR:
    # ... (outros métodos)

    @gemini_api_retry
    async def _generate_gemini_response(self, prompt):
        """
        Gera a resposta do Gemini com o sistema de retry.
        A lógica de chamada da API é encapsulada aqui para aplicar o decorador.
        """
        try:
            # Supondo que 'self.model' é o seu cliente Gemini inicializado
            response = await self.model.generate_content_async(prompt)
            return response
        except google.api_core.exceptions.GoogleAPICallError as e:
            log_with_emoji('error', f"Erro final na chamada da API Gemini após todas as tentativas: {e}", {"component": "AGENTIC SDR"})
            # Propaga a exceção para ser tratada no fluxo principal
            raise
        except Exception as e:
            log_with_emoji('error', f"Um erro inesperado ocorreu durante a geração de resposta do Gemini: {e}", {"component": "AGENTIC SDR"})
            raise

    async def process_message(self, message_data):
        """
        Processa a mensagem do usuário e gera uma resposta.
        """
        try:
            # ... (lógica para construir o prompt)
            prompt = self._build_prompt(message_data)

            # Chama o método com retry
            response = await self._generate_gemini_response(prompt)

            # ... (lógica para processar a resposta)
            return self._parse_response(response)

        except google.api_core.exceptions.GoogleAPICallError as e:
            # Este é o nosso FALLBACK. Ocorre se todas as 5 tentativas falharem.
            log_with_emoji('critical', "Falha crítica: A API Gemini não respondeu após múltiplas tentativas.", {"component": "AGENTIC SDR"})
            # Retorne uma resposta padrão ou lance um erro específico para o seu sistema tratar.
            return "Desculpe, estou com dificuldades técnicas para me conectar aos meus sistemas. Por favor, tente novamente em alguns instantes."
        except Exception as e:
            log_with_emoji('critical', f"Erro crítico no processamento da mensagem: {e}", {"component": "AGENTIC SDR"})
            return "Ocorreu um erro inesperado. A equipe técnica já foi notificada."

```

### Passo 3: Monitoramento e Verificação

- **Monitore os Logs:** Após o deploy, monitore os logs para as mensagens `Gemini API request failed...`. Se elas ocorrerem com muita frequência, pode indicar um problema mais sério com a API do Google.
- **Google Cloud Status:** Em caso de falhas persistentes, verifique o [Google Cloud Status Dashboard](https://status.cloud.google.com/) para anúncios de interrupções na "Vertex AI" ou "Generative AI".

## 5. Resumo da Solução

Ao implementar este sistema, sua aplicação passará de frágil a resiliente.

- **Antes:** Uma única falha 500 da API causava a falha da operação.
- **Depois:** A aplicação tentará se recuperar da falha automaticamente até 5 vezes, com esperas inteligentes. Se a falha persistir, ela terá um comportamento de fallback controlado, registrando o erro e respondendo graciosamente, em vez de quebrar.

Esta é a abordagem padrão da indústria para construir sistemas confiáveis que dependem de serviços de terceiros.
