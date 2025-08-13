# 📅 Guia de Configuração Google Calendar OAuth 2.0

## ✅ Status da Implementação

**IMPLEMENTAÇÃO COMPLETA!** O sistema agora suporta:
- ✅ Autenticação OAuth 2.0
- ✅ Criação automática de Google Meet
- ✅ Convite de participantes
- ✅ Coleta de emails pelo agente
- ✅ Endpoints de autorização funcionais

## 🚀 Configuração Rápida

### 1. Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Vá para **APIs & Services** → **Credentials**
3. Clique em **+ CREATE CREDENTIALS** → **OAuth client ID**
4. Selecione **Web application**
5. Configure:
   - **Name**: SDR IA SolarPrime OAuth
   - **Authorized redirect URIs** (adicione TODAS as URIs que você vai usar): 
     - Desenvolvimento local: `http://localhost:8000/google/callback`
     - Produção EasyPanel: `https://sdr-ia-solarprime.fzvgou.easypanel.host/google/callback`
     - Alternativa (se tiver domínio próprio): `https://seudominio.com.br/google/callback`
6. Salve e copie:
   - **Client ID**
   - **Client Secret**

### 2. Configurar Variáveis de Ambiente

Adicione ao arquivo `.env`:

```env
# Google Calendar OAuth 2.0
GOOGLE_AUTH_METHOD=oauth
GOOGLE_OAUTH_CLIENT_ID=seu_client_id_aqui
GOOGLE_OAUTH_CLIENT_SECRET=seu_client_secret_aqui

# Para desenvolvimento local:
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/google/callback

# Para produção no EasyPanel (descomente e use esta):
# GOOGLE_OAUTH_REDIRECT_URI=https://sdr-ia-solarprime.fzvgou.easypanel.host/google/callback

GOOGLE_OAUTH_REFRESH_TOKEN=  # Será preenchido automaticamente após autorização

# Email do usuário principal (opcional)
GOOGLE_WORKSPACE_USER_EMAIL=leonardo@solarprime.com
```

### 3. Autorizar a Aplicação (Uma única vez)

1. Inicie o servidor:
```bash
python main.py
```

2. Acesse no navegador:
```
http://localhost:8000/google/auth
```

3. Faça login com a conta Google que será usada para criar eventos
4. Autorize os escopos solicitados
5. Você será redirecionado de volta com mensagem de sucesso

**O refresh token será salvo automaticamente no `.env`!**

### 4. Verificar Status

Teste se tudo está funcionando:

```bash
curl http://localhost:8000/google/status
```

Resposta esperada:
```json
{
  "oauth_configured": true,
  "user_email": "leonardo@solarprime.com",
  "calendar_id": "primary",
  "can_create_meets": true,
  "can_invite_attendees": true,
  "message": "Conexão estabelecida com sucesso"
}
```

## 🧪 Teste Completo

### Teste 1: Criar Evento com Meet e Participantes

```python
# test_oauth_complete.py
import asyncio
from datetime import datetime, timedelta
from app.integrations.google_oauth_handler import get_oauth_handler

async def test_oauth_meeting():
    """Testa criação de evento com Google Meet e participantes"""
    
    handler = get_oauth_handler()
    
    # Criar evento
    result = handler.create_event_with_meet(
        title="Reunião Solar - Teste OAuth",
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=1),
        attendees=[
            "cliente@example.com",
            "vendedor@solarprime.com"
        ],
        description="Teste completo do sistema OAuth com Google Meet",
        location="Online - Google Meet"
    )
    
    if result.get("success"):
        print("✅ SUCESSO TOTAL!")
        print(f"📅 Evento: {result['event_link']}")
        print(f"📹 Google Meet: {result['meet_link']}")
        print(f"👥 Participantes: {', '.join(result['attendees'])}")
    else:
        print(f"❌ Erro: {result['message']}")

if __name__ == "__main__":
    asyncio.run(test_oauth_meeting())
```

### Teste 2: Agente Coletando Emails

```python
# test_agent_with_attendees.py
import asyncio
from app.agents.agentic_sdr_refactored import get_agentic_agent

async def test_agent_scheduling():
    """Testa agente coletando emails e agendando reunião"""
    
    agent = await get_agentic_agent()
    
    # Simular conversa
    messages = [
        "Olá, quero agendar uma reunião sobre energia solar",
        "Meu email é cliente@teste.com",
        "Também quero convidar meu sócio: socio@empresa.com",
        "Pode ser amanhã às 14h?"
    ]
    
    for msg in messages:
        response = await agent.process_message(
            message=msg,
            metadata={
                "phone": "11999999999",
                "name": "Cliente Teste"
            }
        )
        print(f"Agente: {response}")

if __name__ == "__main__":
    asyncio.run(test_agent_scheduling())
```

## 🔧 Troubleshooting

### Erro: "OAuth não inicializado corretamente"
- **Causa**: Refresh token não configurado
- **Solução**: Execute `/google/auth` para autorizar

### Erro: "403 Forbidden" ao criar eventos
- **Causa**: Escopos insuficientes
- **Solução**: 
  1. Revogue acesso em https://myaccount.google.com/permissions
  2. Execute `/google/auth` novamente

### Erro: "Refresh token não obtido"
- **Causa**: Aplicação já foi autorizada antes
- **Solução**:
  1. Revogue acesso em https://myaccount.google.com/permissions
  2. Delete o GOOGLE_OAUTH_REFRESH_TOKEN do .env
  3. Execute `/google/auth` novamente

## 📊 Comparação: OAuth vs Service Account

| Funcionalidade | Service Account | OAuth 2.0 |
|---------------|-----------------|-----------|
| Google Meet | ❌ Não funciona | ✅ Funciona |
| Participantes | ❌ Não funciona | ✅ Funciona |
| Configuração | Complexa | Simples |
| Autorização | Automática | Manual (1x) |
| Segurança | Chave privada | Refresh token |
| Manutenção | Baixa | Baixa |

## 🎯 Próximos Passos

1. **Produção**: Mover refresh token para vault seguro
2. **Multi-usuário**: Implementar OAuth por vendedor
3. **Renovação**: Automatizar renovação de tokens
4. **Auditoria**: Log de todas operações OAuth

## 📝 Notas Importantes

- O refresh token **nunca expira** se usado regularmente
- Cada vendedor pode ter sua própria conta OAuth
- Google Meet funciona **automaticamente** com OAuth
- Participantes recebem convites **por email**
- Suporta até 100 participantes por evento

## 🚨 Segurança

**IMPORTANTE**: Em produção, **NÃO** armazene o refresh token no `.env`:

### Opções Seguras:
1. **HashiCorp Vault**
2. **AWS Secrets Manager**
3. **Azure Key Vault**
4. **Google Secret Manager**
5. **Variáveis de ambiente do servidor (mínimo)**

### Exemplo com AWS Secrets Manager:
```python
import boto3
import json

def get_refresh_token():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='google-oauth-refresh-token')
    return json.loads(response['SecretString'])['refresh_token']
```

---

## ✅ Checklist Final

- [ ] Credenciais OAuth criadas no Google Cloud Console
- [ ] Client ID e Secret configurados no .env
- [ ] Autorização executada via `/google/auth`
- [ ] Refresh token salvo automaticamente
- [ ] Status verificado via `/google/status`
- [ ] Teste de criação de evento com Meet
- [ ] Teste de convite de participantes
- [ ] Agente coletando emails corretamente

**Sistema 100% funcional com OAuth 2.0! 🎉**