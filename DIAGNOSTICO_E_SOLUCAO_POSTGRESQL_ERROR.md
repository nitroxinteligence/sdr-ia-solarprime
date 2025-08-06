# Diagnóstico e Solução do Erro de Conexão com PostgreSQL (Supabase)

## 1. Análise do Erro

O log de erro `WARNING | app.utils.optional_storage:__init__:47 | ⚠️ PostgreSQL não disponível: (psycopg2.OperationalError) connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...` indica uma falha na tentativa de conexão com o banco de dados Supabase.

- **`app.utils.optional_storage:__init__`**: O erro ocorre na inicialização da classe `OptionalStorage`, que tenta estabelecer uma conexão com o PostgreSQL através da biblioteca `agno`.
- **`(psycopg2.OperationalError)`**: Este é um erro do driver do PostgreSQL (`psycopg2`) que sinaliza uma falha de conexão. Não é um erro de autenticação (senha errada), mas sim um problema de rede, como incapacidade de alcançar o servidor, firewall, ou falha na resolução de DNS.
- **`connection to server at "db.rcjcpwqezmlhenmhrski.supabase.co" (2a05:d016...)`**: A parte mais reveladora. A aplicação está tentando se conectar ao host do Supabase, e o sistema operacional resolveu esse nome para um endereço **IPv6** (`2a05:d016...`). A falha em conectar-se a este endereço é a causa direta do erro.

**Conclusão da Análise do Erro**: A causa mais provável é um problema de configuração de rede no ambiente de execução (local ou Docker) que impede ou dificulta conexões via IPv6. Muitos ambientes Docker, por padrão, têm suporte limitado ou problemático a IPv6, e quando um nome de domínio (como o do Supabase) resolve tanto para um endereço IPv4 quanto para um IPv6, o sistema pode tentar o IPv6 primeiro e falhar.

## 2. Investigação e Causas Raízes

Dado que as credenciais no arquivo `.env` estão corretas, as causas prováveis são:

1.  **Problema de Rede/DNS com IPv6 (Causa Mais Provável)**: O ambiente de execução não consegue estabelecer uma conexão de saída usando IPv6. O driver de banco de dados tenta usar o endereço IPv6 resolvido e falha.
2.  **Firewall Bloqueando a Conexão**: Firewalls locais ou de rede podem estar bloqueando o tráfego de saída na porta padrão do PostgreSQL (`5432`) ou na porta do pool de conexões do Supabase (`6543`).
3.  **Instância Supabase Pausada**: Projetos no tier gratuito do Supabase são pausados após um período de inatividade. Uma instância pausada recusará conexões.

## 3. Solução Definitiva e Melhores Práticas

A solução mais robusta é forçar a conexão a usar o **pool de conexões do Supabase** no modo `transaction`, que é projetado para ambientes serverless e de curta duração como este, e geralmente oferece melhor resiliência e gerenciamento de conexões. Além disso, a URL do pooler geralmente tem uma configuração de DNS que favorece IPv4 ou é mais compatível com diversos ambientes.

### Camada 1: Corrigir a String de Conexão (Solução Principal)

Vamos modificar a forma como a URL de conexão com o PostgreSQL é construída para garantir que estamos usando o pool de conexões (porta 6543), que é a prática recomendada pelo Supabase para aplicações.

**Modificação proposta para `app/config.py`:**

No método `get_postgres_url`, vamos garantir que a URL seja montada corretamente, priorizando as variáveis de ambiente e usando o formato do pooler.

```python
# Em app/config.py

def get_postgres_url(self) -> str:
    """Retorna a URL de conexão PostgreSQL do Supabase, priorizando o pooler."""
    import os

    # Priorizar a URL completa do .env
    db_url = os.getenv('SUPABASE_DB_URL') or self.supabase_db_url

    if db_url and 'pooler.supabase.com' in db_url:
        print("✅ Usando URL do Pooler de Conexões Supabase (Recomendado).")
        return db_url

    # Se a URL não for do pooler, ou se estivermos montando a partir de partes
    # (Cenário de fallback ou configuração legada)
    if db_url:
        # Extrair partes da URL para garantir que estamos usando a porta do pooler
        from urllib.parse import urlparse, urlunparse
        parsed_url = urlparse(db_url)
        # Forçar o uso da porta 6543 do pooler
        netloc = f"{parsed_url.username}:{parsed_url.password}@{parsed_url.hostname}:6543"
        
        new_url = urlunparse((
            parsed_url.scheme,
            netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))
        print(f"⚠️ URL de DB direta detectada. Convertendo para URL do Pooler: ...@{parsed_url.hostname}:6543")
        return new_url

    print("❌ SUPABASE_DB_URL não encontrada. Verifique seu arquivo .env.")
    raise ValueError("A variável de ambiente SUPABASE_DB_URL é obrigatória.")
```

### Camada 2: Resiliência na Conexão (Melhoria Adicional)

Para tornar a aplicação mais robusta a falhas temporárias, adicionaremos uma lógica de retry com backoff exponencial na classe `OptionalStorage`.

**Modificação sugerida para `app/utils/optional_storage.py`:**

```python
# Em app/utils/optional_storage.py

import asyncio

class OptionalStorage:
    def __init__(self, table_name: str, db_url: str, ...):
        # ...
        self.storage = None
        # Tenta conectar com retry
        try:
            asyncio.run(self.connect_with_retry(table_name, db_url, schema, auto_upgrade_schema))
        except Exception as e:
            logger.error(f"Falha final ao conectar no PostgreSQL: {e}")

    async def connect_with_retry(self, table_name, db_url, schema, auto_upgrade_schema):
        max_retries = 5
        retry_delay = 2.0

        for attempt in range(max_retries):
            try:
                self.storage = PostgresStorage(
                    table_name=table_name,
                    db_url=db_url,
                    schema=schema,
                    auto_upgrade_schema=auto_upgrade_schema
                )
                logger.info(f"✅ PostgresStorage conectado para tabela: {table_name}")
                return # Sucesso
            except Exception as e:
                logger.warning(f"⚠️ PostgreSQL não disponível (tentativa {attempt + 1}/{max_retries}): {str(e)[:100]}...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                else:
                    logger.error("❌ Falha ao conectar ao PostgreSQL. Sistema funcionará em modo de memória.")
                    self.storage = None

    # ... (restante da classe)
```

## 4. Plano de Ação

1.  **Verificar a Instância Supabase**: O usuário deve primeiro garantir que sua instância no [dashboard da Supabase](https://app.supabase.com) não está pausada.
2.  **Atualizar a Lógica de Conexão**: Aplicar a modificação no método `get_postgres_url` em `app/config.py` para forçar o uso do pooler de conexão (porta 6543), que é mais resiliente e contorna problemas de IPv6.
3.  **Aumentar a Resiliência**: Implementar a lógica de retry com backoff exponencial no construtor da classe `OptionalStorage` em `app/utils/optional_storage.py`.
