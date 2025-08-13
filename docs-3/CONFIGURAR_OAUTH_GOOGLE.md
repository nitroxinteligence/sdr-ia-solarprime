# 🚨 CONFIGURAÇÃO URGENTE DO GOOGLE OAUTH - RESOLVER ERRO 400

## ❌ ERRO ATUAL
```
Erro 400: invalid_request
Missing required parameter: redirect_uri
```

## ✅ SOLUÇÃO IMEDIATA

### 1. ACESSE O GOOGLE CLOUD CONSOLE
https://console.cloud.google.com/

### 2. VÁ PARA CREDENCIAIS
- No menu lateral: **APIs e serviços** → **Credenciais**
- Ou direto: https://console.cloud.google.com/apis/credentials

### 3. ENCONTRE SEU CLIENT OAuth 2.0
- Procure pelo Client ID: `834251560398-5bl46u08631rvut5d04pi86bot2des43.apps.googleusercontent.com`
- Clique para editar

### 4. ADICIONE OS REDIRECT URIs (COPIE EXATAMENTE!)

**Para desenvolvimento local (ADICIONE ESTE PRIMEIRO):**
```
http://localhost:8000/google/callback
```

**Para produção no EasyPanel (ADICIONE TAMBÉM):**
```
https://sdr-api-evolution-api.fzvgou.easypanel.host/google/callback
```

### 5. IMPORTANTE - ADICIONE TAMBÉM ESTAS VARIAÇÕES:
```
http://127.0.0.1:8000/google/callback
http://localhost:8000/google/callback/
https://evoapi-evolution-api.fzvgou.easypanel.host/google/callback
```

### 6. SALVE AS ALTERAÇÕES
- Clique em **SALVAR** no final da página
- Aguarde 5 minutos para propagar

## 📝 CHECKLIST DE VERIFICAÇÃO

- [ ] O redirect_uri está EXATAMENTE igual (sem espaços, sem barra extra)
- [ ] Você salvou as alterações no Google Cloud Console
- [ ] Você esperou 5 minutos para propagar

## 🔗 URL PARA TESTAR

Após configurar, teste com esta URL:
```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=834251560398-5bl46u08631rvut5d04pi86bot2des43.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fgoogle%2Fcallback&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar.events+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fmeetings.space.created&access_type=offline&include_granted_scopes=true&prompt=consent
```

## 🎯 RESULTADO ESPERADO
Após configurar corretamente, você verá:
1. Tela de login do Google
2. Tela de consentimento pedindo permissões
3. Redirecionamento para http://localhost:8000/google/callback com o código

## ⚠️ SE AINDA DER ERRO

### Verifique no Google Cloud Console:
1. O app está em modo "Testing" ou "Production"?
2. Se estiver em "Testing", adicione seu email como usuário de teste
3. Verifique se as APIs estão habilitadas:
   - Google Calendar API
   - Google Meet API (se disponível)

### URLs Úteis:
- Credenciais: https://console.cloud.google.com/apis/credentials
- OAuth consent screen: https://console.cloud.google.com/apis/credentials/consent
- APIs habilitadas: https://console.cloud.google.com/apis/dashboard

## 💡 DICA IMPORTANTE
O erro "Missing required parameter: redirect_uri" significa que o Google não reconhece o redirect_uri que estamos enviando. Isso acontece porque ele NÃO está cadastrado no Google Cloud Console.

**A URL está sendo gerada corretamente com o redirect_uri:**
- ✅ redirect_uri está presente na URL
- ✅ Valor: `http://localhost:8000/google/callback`
- ❌ Mas não está cadastrado no Google Cloud Console

## AÇÃO NECESSÁRIA AGORA:
**ADICIONE `http://localhost:8000/google/callback` NO GOOGLE CLOUD CONSOLE!**