# 🔐 Configurando OAuth2 do Kommo no EasyPanel (Produção)

## 📋 Visão Geral do Problema

Você tem o SDR IA rodando no EasyPanel e precisa configurar a URL de redirecionamento OAuth2 do Kommo. O Kommo está rejeitando `localhost` porque precisa de uma URL pública acessível.

## ✅ Solução Completa para Produção

### 1️⃣ Configure um Domínio no EasyPanel

#### Opção A: Usando Subdomínio do EasyPanel (Mais Rápido)
1. No EasyPanel, acesse seu serviço `sdr-api`
2. Vá para a aba **"Domains"**
3. O EasyPanel já fornece um domínio padrão como:
   ```
   https://sdr-api-evoapi.easypanel.host
   ```
4. Certifique-se de que **"Enable HTTPS"** está marcado

#### Opção B: Usando Domínio Personalizado
1. Configure seu DNS para apontar para o IP do servidor
2. No EasyPanel, adicione o domínio personalizado:
   ```
   https://api.seudominio.com
   ```

### 2️⃣ Configure a URL de Redirecionamento no Kommo

No painel do Kommo, use uma dessas URLs:

**Com domínio EasyPanel:**
```
https://sdr-api-evoapi.easypanel.host/auth/kommo/callback
```

**Com domínio personalizado:**
```
https://api.seudominio.com/auth/kommo/callback
```

### 3️⃣ Atualize as Variáveis de Ambiente no EasyPanel

1. No EasyPanel, acesse seu serviço `sdr-api`
2. Vá para a aba **"Environment"**
3. Adicione/atualize:

```env
# Kommo OAuth2
KOMMO_CLIENT_ID=seu_client_id_aqui
KOMMO_CLIENT_SECRET=seu_client_secret_aqui
KOMMO_SUBDOMAIN=leonardofvieira00
KOMMO_REDIRECT_URI=https://sdr-api-evoapi.easypanel.host/auth/kommo/callback

# URL Base da API (importante para callbacks)
API_BASE_URL=https://sdr-api-evoapi.easypanel.host
WEBHOOK_BASE_URL=https://sdr-api-evoapi.easypanel.host
```

### 4️⃣ Verifique as Rotas de Autenticação

Certifique-se de que as rotas OAuth2 estão configuradas no seu FastAPI:

```python
# api/routes/auth.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import os

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/kommo/login")
async def kommo_login():
    """Inicia fluxo OAuth2 do Kommo"""
    # Redireciona para página de autorização do Kommo
    
@router.get("/kommo/callback")
async def kommo_callback(code: str, state: str = None):
    """Callback OAuth2 do Kommo"""
    # Processa o código de autorização
```

### 5️⃣ Configure o Proxy Reverso no EasyPanel

O EasyPanel usa Traefik como proxy reverso. Certifique-se de que:

1. Na aba **"Domains"**, o binding está correto:
   - **Service**: sdr-api
   - **Port**: 8000
   - **Path**: / (raiz)

2. SSL/TLS está habilitado (HTTPS)

### 6️⃣ Teste a Configuração

#### Teste 1: Verificar se a URL está acessível
```bash
# Do seu computador local
curl https://sdr-api-evoapi.easypanel.host/health
```

#### Teste 2: Verificar rota de callback
```bash
curl https://sdr-api-evoapi.easypanel.host/auth/kommo/callback?code=test
```

### 7️⃣ Configuração Completa no Kommo

1. Acesse: `https://leonardofvieira00.kommo.com/settings/widgets/`
2. Edite sua integração privada
3. Configure:
   - **Nome**: SDR IA SolarPrime
   - **Redirect URI**: `https://sdr-api-evoapi.easypanel.host/auth/kommo/callback`
   - **Permissões**: Todas necessárias marcadas

## 🔧 Troubleshooting

### Problema: "URL não encontrado ou não ativo"

**Solução 1**: Verificar se o serviço está rodando
```bash
# No EasyPanel, veja os logs do serviço
# Verifique se está respondendo na porta 8000
```

**Solução 2**: Testar acesso externo
```bash
# De qualquer lugar
curl -I https://sdr-api-evoapi.easypanel.host
```

**Solução 3**: Verificar firewall/segurança
- Porta 443 (HTTPS) deve estar aberta
- Certificado SSL deve estar válido

### Problema: "Invalid redirect URI"

**Solução**: A URL no Kommo deve ser EXATAMENTE igual à do .env:
- ❌ `https://sdr-api-evoapi.easypanel.host/auth/kommo/callback/`
- ✅ `https://sdr-api-evoapi.easypanel.host/auth/kommo/callback`
(Note a diferença da barra final)

## 📝 Script de Verificação

Crie este endpoint para verificar a configuração:

```python
# api/routes/system.py
@router.get("/oauth-config")
async def get_oauth_config():
    """Retorna configuração OAuth para debug"""
    return {
        "redirect_uri": os.getenv("KOMMO_REDIRECT_URI"),
        "client_id": os.getenv("KOMMO_CLIENT_ID", "NOT_SET"),
        "subdomain": os.getenv("KOMMO_SUBDOMAIN"),
        "base_url": os.getenv("API_BASE_URL"),
        "auth_url": f"{os.getenv('API_BASE_URL')}/auth/kommo/login"
    }
```

Acesse: `https://sdr-api-evoapi.easypanel.host/oauth-config`

## 🚀 Fluxo Completo de Autenticação

1. **Usuário acessa**: 
   ```
   https://sdr-api-evoapi.easypanel.host/auth/kommo/login
   ```

2. **API redireciona para Kommo**:
   ```
   https://leonardofvieira00.kommo.com/oauth/authorize?
   client_id=XXX&
   redirect_uri=https://sdr-api-evoapi.easypanel.host/auth/kommo/callback&
   response_type=code
   ```

3. **Kommo redireciona de volta**:
   ```
   https://sdr-api-evoapi.easypanel.host/auth/kommo/callback?code=XXX&state=YYY
   ```

4. **API processa e salva tokens**

## ✅ Checklist Final

- [ ] Domínio configurado no EasyPanel (com HTTPS)
- [ ] URL de redirect configurada no Kommo
- [ ] Variáveis de ambiente atualizadas no EasyPanel
- [ ] Rotas /auth/kommo/* implementadas
- [ ] Serviço reiniciado após mudanças
- [ ] URL de callback acessível externamente
- [ ] Teste de fluxo OAuth2 completo

## 🎯 Exemplo de .env Completo para EasyPanel

```env
# === APLICAÇÃO ===
ENVIRONMENT=production
DEBUG=False
API_BASE_URL=https://sdr-api-evoapi.easypanel.host
WEBHOOK_BASE_URL=https://sdr-api-evoapi.easypanel.host

# === KOMMO CRM ===
KOMMO_CLIENT_ID=abc123def456
KOMMO_CLIENT_SECRET=xyz789secret
KOMMO_SUBDOMAIN=leonardofvieira00
KOMMO_REDIRECT_URI=https://sdr-api-evoapi.easypanel.host/auth/kommo/callback

# Pipeline e Stages
KOMMO_PIPELINE_ID=1234567
KOMMO_STAGE_NEW=1001
KOMMO_STAGE_IN_QUALIFICATION=1002
KOMMO_STAGE_QUALIFIED=1003
KOMMO_STAGE_MEETING_SCHEDULED=1004

# Campos Personalizados
KOMMO_FIELD_WHATSAPP=2001
KOMMO_FIELD_ENERGY_BILL=2002
KOMMO_FIELD_QUALIFICATION_SCORE=2003

# Usuários
KOMMO_USER_DEFAULT=4001
KOMMO_USER_HIGH_VALUE=4002

# === OUTROS SERVIÇOS (internos no EasyPanel) ===
EVOLUTION_API_URL=http://evolution-api:8080
REDIS_URL=redis://evolution-api-redis:6379/0
```

## 🆘 Suporte Adicional

Se ainda tiver problemas:

1. **Verifique os logs do EasyPanel**:
   - Acesse a aba "Logs" do serviço
   - Procure por erros relacionados a "auth" ou "kommo"

2. **Teste com Postman/Insomnia**:
   - Faça requisições diretas para testar as rotas

3. **Verifique certificado SSL**:
   ```bash
   openssl s_client -connect sdr-api-evoapi.easypanel.host:443
   ```

Com essa configuração, você terá uma URL pública válida que o Kommo pode verificar e usar para o redirecionamento OAuth2!