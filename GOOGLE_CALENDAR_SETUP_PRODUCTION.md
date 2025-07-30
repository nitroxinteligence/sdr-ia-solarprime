# Configuração do Google Calendar em Produção

## Problema
O arquivo de credenciais do Google Calendar (`credentials/google_calendar_credentials.json`) não está sendo enviado para produção porque a pasta `credentials/` está no `.gitignore`.

## Solução 1: Variáveis de Ambiente no EasyPanel (Recomendado)

### 1. Adicione estas variáveis de ambiente no EasyPanel:

```bash
# Credenciais do Google Calendar
GOOGLE_CLIENT_ID=<seu_client_id_aqui>
GOOGLE_CLIENT_SECRET=<seu_client_secret_aqui>
GOOGLE_PROJECT_ID=<seu_project_id_aqui>

# Opcional - para desabilitar temporariamente
DISABLE_GOOGLE_CALENDAR=true
```

### 2. Criar arquivo de credenciais em runtime (adicionar ao código):

```python
# No início do google_calendar_service.py
import json
import os

def create_credentials_from_env():
    """Cria arquivo de credenciais a partir de variáveis de ambiente"""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    
    if client_id and client_secret:
        credentials = {
            "installed": {
                "client_id": client_id,
                "project_id": project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": ["http://localhost"]
            }
        }
        
        os.makedirs('credentials', exist_ok=True)
        with open('credentials/google_calendar_credentials.json', 'w') as f:
            json.dump(credentials, f)
        
        return True
    return False
```

## Solução 2: Montar Volume no Docker (EasyPanel)

1. No EasyPanel, crie um volume persistente
2. Monte o volume em `/app/credentials`
3. Faça upload manual dos arquivos de credenciais

## Solução 3: Desabilitar Temporariamente

Para desabilitar o Google Calendar temporariamente, adicione no EasyPanel:

```bash
DISABLE_GOOGLE_CALENDAR=true
```

E modifique o código em `agents/sdr_agent.py`:

```python
# Linha 114
if not os.getenv('DISABLE_GOOGLE_CALENDAR') and os.path.exists(os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "")):
```

## Solução 4: Usar Base64 (Alternativa)

Codifique o arquivo em base64 e adicione como variável de ambiente:

```bash
# No terminal local
base64 credentials/google_calendar_credentials.json

# No EasyPanel
GOOGLE_CALENDAR_CREDENTIALS_BASE64=<resultado_do_base64>
```

## Próximos Passos

1. Escolha uma das soluções acima
2. Configure as variáveis de ambiente no EasyPanel
3. Faça o deploy novamente

## Observação Importante

⚠️ **NUNCA** commite arquivos de credenciais no repositório Git!
- Mantenha `credentials/` no `.gitignore`
- Use sempre variáveis de ambiente para secrets
- Considere usar um gerenciador de secrets em produção