# Guia para Obter Tokens do Kommo CRM

## Método 1: Via Interface do Kommo (Mais Fácil)

1. **Acesse sua conta Kommo**:
   - https://leonardofvieira00.kommo.com/

2. **Vá para Configurações > Integrações**:
   - https://leonardofvieira00.kommo.com/settings/integrations/

3. **Crie uma Integração Privada**:
   - Clique em "+ Criar integração"
   - Escolha "Integração privada"
   - Preencha:
     - Nome: "SDR IA SolarPrime"
     - Descrição: "Integração WhatsApp AI"
   
4. **Configure os escopos necessários**:
   - ✅ Leads (Leitura e Escrita)
   - ✅ Contatos (Leitura e Escrita)
   - ✅ Tarefas (Leitura e Escrita)
   - ✅ Notas (Escrita)
   - ✅ Pipelines (Leitura)

5. **Após criar, você verá**:
   - **Access Token**: Um token longo que começa com algo como "eyJ0eXAiOiJKV1..."
   - **Refresh Token**: Outro token longo similar
   - Copie ambos!

## Método 2: Via Fluxo OAuth Correto

Se preferir usar o fluxo OAuth completo:

1. **Gere a URL de autorização**:
   ```
   https://leonardofvieira00.kommo.com/oauth?
   client_id=0dd96bf8-4ab8-4d4e-b43e-68dab6270348&
   redirect_uri=https://sdr-api-evolution-api.fzvgou.easypanel.host/auth/kommo/callback&
   response_type=code&
   state=kommo_oauth&
   mode=popup
   ```

2. **Acesse a URL no navegador**:
   - Faça login
   - Autorize a aplicação
   - Será redirecionado com o código

3. **Use o código rapidamente** (expira em 20 minutos)

## Método 3: Via API (se você for admin)

Se você é administrador da conta:

1. **Acesse**: https://leonardofvieira00.kommo.com/settings/profile/
2. **Procure por "API" ou "Tokens de API"**
3. **Gere um token de longa duração**

## Tokens de Exemplo (formato correto)

- **Access Token**: Geralmente começa com "eyJ..." e tem 200+ caracteres
- **Refresh Token**: Similar ao access token
- **NÃO é**: O Client Secret (Z8O7amBq...)

## Diferenças Importantes

| Item | O que é | Exemplo |
|------|---------|---------|
| Client ID | ID da aplicação | 0dd96bf8-4ab8-4d4e-b43e-68dab6270348 |
| Client Secret | Senha da aplicação | Z8O7amBqdszg... |
| Access Token | Token de acesso | eyJ0eXAiOiJKV1QiLCJhbGciOi... |
| Refresh Token | Token de renovação | eyJ0eXAiOiJKV1QiLCJhbGciOi... |

⚠️ **IMPORTANTE**: Você precisa do Access Token, não do Client Secret!