# Autenticação Google Calendar em Servidor (Headless)

## Problema
O erro "could not locate runnable browser" ocorre porque o servidor não tem interface gráfica para abrir o navegador durante a autenticação OAuth.

## Solução Rápida: Usar Token Pré-Autenticado

### 1. Gerar o Token Localmente

Execute este script em sua máquina local (com navegador):

```python
# generate_google_token.py
import pickle
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    
    # Fazer autenticação
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials/google_calendar_credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Salvar o token
    with open('google_calendar_token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    print("✅ Token gerado com sucesso!")
    print("📁 Arquivo: google_calendar_token.pickle")
    print("🚀 Faça upload deste arquivo para o servidor")

if __name__ == '__main__':
    main()
```

### 2. Upload do Token para Produção

#### Opção A: Via Base64 (Recomendado)
```bash
# Na sua máquina local
base64 google_calendar_token.pickle > token_base64.txt

# No EasyPanel, adicione:
GOOGLE_CALENDAR_TOKEN_BASE64=<conteúdo_do_token_base64.txt>
```

#### Opção B: Volume Montado
1. No EasyPanel, crie um volume persistente
2. Monte em `/app/credentials`
3. Faça upload do arquivo `google_calendar_token.pickle`

### 3. Modificar o Código (Já implementado)

O código agora detecta ambientes headless e fornece instruções para autenticação manual.

## Solução Alternativa: Service Account (Mais Profissional)

### 1. Criar Service Account no Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Vá em **IAM & Admin** > **Service Accounts**
3. Crie uma nova Service Account
4. Baixe a chave JSON
5. Compartilhe seu calendário com o email da Service Account

### 2. Usar Service Account no Código

```python
from google.oauth2 import service_account

# Em vez de InstalledAppFlow, use:
credentials = service_account.Credentials.from_service_account_file(
    'path/to/service-account-key.json',
    scopes=SCOPES
)
```

### 3. Variáveis de Ambiente para Service Account

```bash
# No EasyPanel
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json
GOOGLE_CALENDAR_USE_SERVICE_ACCOUNT=true
```

## Status Atual

O código foi atualizado para:
1. ✅ Detectar ambientes headless (sem interface gráfica)
2. ✅ Fornecer URL para autenticação manual
3. ✅ Aceitar código de autorização via variável de ambiente
4. ✅ Continuar funcionando normalmente em ambientes com interface gráfica

## Próximos Passos

1. **Para resolver imediatamente**: Defina `DISABLE_GOOGLE_CALENDAR=true` no EasyPanel
2. **Para autenticação completa**: Siga uma das soluções acima
3. **Recomendação**: Use Service Account para produção (mais estável e sem necessidade de reautenticação)