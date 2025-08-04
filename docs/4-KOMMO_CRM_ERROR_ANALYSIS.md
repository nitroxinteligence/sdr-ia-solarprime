# Análise e Solução Detalhada dos Erros em Produção

## Introdução

O log de erros apresentado revela três problemas distintos e independentes que estão ocorrendo em sua aplicação. É crucial entender que não há uma única "causa raiz", mas sim três falhas separadas que precisam de soluções específicas. Este documento detalha cada erro, sua causa provável e a estratégia mais inteligente para corrigi-lo de forma permanente.

--- 

## Erro 1: Violação de Chave Única no Banco de Dados (PostgreSQL)

### O Erro:
```
Erro ao sincronizar novo evento: {'message': 'duplicate key value violates unique constraint "calendar_events_google_event_id_key"', 'code': '23505', 'details': 'Key (google_event_id)=(6921s3b9e38s2ugur6pbd5baqb) already exists.'}
```

### Análise Profunda:

Este erro é gerado pelo seu banco de dados PostgreSQL. Ele informa que você está tentando inserir uma nova linha na tabela `calendar_events`, mas o valor que está tentando adicionar na coluna `google_event_id` já existe. A coluna `google_event_id` possui uma restrição `UNIQUE`, o que significa que cada valor nela deve ser único.

**Cenário Provável:**

Seu sistema está tentando sincronizar um evento do Google Calendar que já foi sincronizado e inserido no banco de dados anteriormente. Isso pode acontecer por vários motivos:

1.  **Lógica de Sincronização Imperfeita:** O serviço que busca novos eventos (`app.services.kommo_auto_sync:sync_new_leads` ou um serviço relacionado) está buscando eventos que já foram processados.
2.  **Re-processamento de Webhooks:** Um webhook do Google Calendar pode ser enviado mais de uma vez (at-least-once delivery), fazendo com que sua aplicação tente processar o mesmo evento duas vezes.
3.  **Condições de Corrida (Race Conditions):** Se múltiplos processos ou threads tentam sincronizar os mesmos dados simultaneamente, ambos podem verificar que o evento não existe e, em seguida, ambos tentam inseri-lo, com o segundo a falhar.

### Solução Inteligente: Operação "Upsert" (INSERT ... ON CONFLICT)

A solução mais robusta e eficiente não é tentar evitar a inserção duplicada no código Python (verificando com um `SELECT` antes de um `INSERT`), pois isso é ineficiente (duas viagens ao banco de dados) e propenso a condições de corrida.

A solução correta é delegar o tratamento da duplicata ao próprio banco de dados usando a funcionalidade `ON CONFLICT` do PostgreSQL, também conhecida como "Upsert".

**Estratégia:**

Modifique sua instrução SQL de `INSERT` para `INSERT ... ON CONFLICT DO NOTHING` ou `INSERT ... ON CONFLICT DO UPDATE`.

1.  **`ON CONFLICT DO NOTHING`:** Se o `google_event_id` já existir, o PostgreSQL simplesmente ignorará o comando `INSERT` e não fará nada. A operação é considerada um sucesso e nenhum erro é gerado. Esta é a abordagem mais simples e segura se você só precisa garantir que o evento exista no banco.

    **Exemplo de SQL:**
    ```sql
    INSERT INTO calendar_events (google_event_id, other_column_1, other_column_2)
    VALUES (%s, %s, %s)
    ON CONFLICT (google_event_id) DO NOTHING;
    ```

2.  **`ON CONFLICT DO UPDATE`:** Se o `google_event_id` já existir, em vez de ignorar, você pode querer atualizar a linha existente com os novos dados do evento (caso o evento tenha sido modificado no Google Calendar).

    **Exemplo de SQL:**
    ```sql
    INSERT INTO calendar_events (google_event_id, title, event_start_time)
    VALUES (%s, %s, %s)
    ON CONFLICT (google_event_id) DO UPDATE SET
        title = EXCLUDED.title,
        event_start_time = EXCLUDED.event_start_time;
    ```
    * `EXCLUDED` é uma palavra-chave especial do PostgreSQL que se refere aos valores que você *tentou* inserir.

**Recomendação:** Para a sincronização de eventos, `ON CONFLICT DO UPDATE` é geralmente a melhor escolha, pois garante que seus dados locais estejam sempre atualizados com a versão mais recente do Google Calendar.

--- 

## Erro 2: Erro de Formatação no Logging

### O Erro:
```
TypeError: %d format: a real number is required, not str
Call stack:
... 
Message: 'Uvicorn running on %s://%s:%d (Press CTRL+C to quit)'
Arguments: ('http', '0.0.0.0', '8000')
```

### Análise Profunda:

Este erro vem da biblioteca de logging do Python e é acionado pelo Uvicorn. A mensagem de log que o Uvicorn tenta formatar é `'Uvicorn running on %s://%s:%d'`. Os especificadores de formato são:

- `%s`: para uma string.
- `%s`: para uma string.
- `%d`: para um inteiro decimal.

Os argumentos fornecidos são `('http', '0.0.0.0', '8000')`. O problema é que o último argumento, a porta `'8000'`, está sendo passado como uma **string**, mas o especificador de formato `%d` exige um **número inteiro**.

**Causa Provável:**

Isso geralmente acontece quando a configuração da porta para o Uvicorn é lida de uma variável de ambiente ou de um arquivo de configuração. Valores de variáveis de ambiente são **sempre strings**. O código que inicia o Uvicorn não está convertendo a string da porta para um inteiro antes de passá-la para a função `uvicorn.run`.

**Local da Falha:**

Procure no seu arquivo `main.py` (ou onde você inicia o Uvicorn) pela chamada `uvicorn.run`. A correção é garantir que o valor da porta seja um inteiro.

### Solução Inteligente: Coerção de Tipo Explícita

A solução é simples e direta: converter explicitamente a variável da porta para um inteiro usando `int()`.

**Exemplo de Código Corrigido (em `main.py`):**

```python
# main.py
import uvicorn
import os

if __name__ == "__main__":
    # Supondo que a porta venha de uma variável de ambiente
    host = os.getenv("HOST", "0.0.0.0")
    port_str = os.getenv("PORT", "8000")

    try:
        # A CORREÇÃO ESTÁ AQUI:
        port_int = int(port_str)
    except ValueError:
        print(f"Erro: A porta especificada '{port_str}' não é um número válido. Usando a porta padrão 8000.")
        port_int = 8000

    uvicorn.run(
        "app.main:app", # ou o caminho para sua aplicação FastAPI/ASGI
        host=host,
        port=port_int, # Use a variável convertida para inteiro
        reload=True # ou sua configuração
    )
```

--- 

## Erro 3: Falha de Autenticação na API Kommo

### O Erro:
```
2025-08-04 12:14:21.622 | ERROR    | app.teams.agents.crm_enhanced:_make_request:71 | Erro na requisição POST https://api-c.kommo.com/api/v4/leads: 401 - 
```

### Análise Profunda:

Um código de status `401 Unauthorized` significa que a requisição para a API do Kommo foi rejeitada porque o `access_token` (token de acesso) fornecido não é válido. Isso acontece por dois motivos principais no contexto do OAuth 2.0, que o Kommo utiliza:

1.  **Token Expirado:** Os tokens de acesso do Kommo têm uma vida útil curta (geralmente 24 horas). Após esse período, eles expiram e não podem mais ser usados.
2.  **Token Inválido ou Revogado:** O token pode ter sido revogado manualmente, ou o `refresh_token` usado para obtê-lo pode ter se tornado inválido.

Sua aplicação **deve** ter um fluxo para lidar com a expiração de tokens. O fluxo padrão do OAuth 2.0 é:

1.  Fazer a requisição à API com o `access_token` atual.
2.  Se receber um erro `401`, significa que o token provavelmente expirou.
3.  Usar o `refresh_token` (que tem uma vida útil mais longa, geralmente 3 meses) para solicitar um **novo par** de `access_token` e `refresh_token` do endpoint de autenticação do Kommo.
4.  Salvar o **novo par de tokens** de forma segura, substituindo os antigos.
5.  Tentar novamente a requisição original com o novo `access_token`.

### Solução Inteligente: Implementar um Fluxo de Atualização de Token (Token Refresh Flow)

A solução mais robusta é criar um wrapper ou um cliente de API para o Kommo que encapsula essa lógica de atualização de token, tornando-a transparente para o resto da sua aplicação.

**Estratégia:**

1.  **Armazenamento Seguro de Tokens:** Guarde o `access_token` e o `refresh_token` em um local persistente (banco de dados, Redis, ou um arquivo de configuração seguro).

2.  **Wrapper de Requisição:** Crie uma função ou método (como `_make_request` no seu log) que:
    a.  Adiciona o `access_token` atual ao cabeçalho `Authorization: Bearer ...`.
    b.  Executa a requisição.
    c.  Se a resposta for `401`, ele aciona a função de atualização de token.
    d.  A função de atualização faz um `POST` para `https://<seu_subdominio>.kommo.com/oauth2/access_token` com `grant_type='refresh_token'`.
    e.  Salva os novos tokens recebidos.
    f.  Repete a requisição original que falhou, agora com o novo token.

**Exemplo de Código Conceitual:**

```python
# Em um arquivo como app/integrations/kommo_client.py

import requests
import time

class KommoClient:
    def __init__(self, subdomain, client_id, client_secret, redirect_uri):
        # ... inicialização ...
        self.access_token = # carregar de um storage
        self.refresh_token = # carregar de um storage
        self.token_expires_at = # carregar de um storage

    def _refresh_tokens(self):
        print("Token expirado. Atualizando...")
        token_url = f"https://{self.subdomain}.kommo.com/oauth2/access_token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(token_url, json=payload)
        response.raise_for_status() # Lança erro se a atualização falhar
        
        new_tokens = response.json()
        self.access_token = new_tokens['access_token']
        self.refresh_token = new_tokens['refresh_token']
        self.token_expires_at = time.time() + new_tokens['expires_in']
        
        # SALVAR os novos tokens e o tempo de expiração no seu storage
        print("Tokens atualizados com sucesso.")

    def make_request(self, method, endpoint, **kwargs):
        # Checagem proativa (opcional, mas bom)
        if time.time() >= self.token_expires_at:
            self._refresh_tokens()

        url = f"https://{self.subdomain}.kommo.com{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            self._refresh_tokens()
            # Tenta novamente com o novo token
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.request(method, url, headers=headers, **kwargs)
            
        response.raise_for_status() # Lança erro para códigos != 2xx
        return response.json()

```

Esta abordagem centraliza a lógica de autenticação, tornando o resto do código (`crm_enhanced.py`) mais limpo e focado apenas em sua lógica de negócio.