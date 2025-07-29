# Como Corrigir o Erro redirect_uri_mismatch

## ❌ Erro Encontrado
```
Erro 400: redirect_uri_mismatch
```

Este erro ocorre quando a URI de redirecionamento configurada no Google Cloud Console não corresponde à usada pela aplicação.

## ✅ Solução Passo a Passo

### 1. Acesse o Google Cloud Console
1. Vá para [Google Cloud Console](https://console.cloud.google.com/)
2. Selecione seu projeto

### 2. Navegue até as Credenciais OAuth
1. Menu lateral → "APIs e Serviços" → "Credenciais"
2. Encontre suas credenciais OAuth 2.0 (tipo "Aplicativo para desktop")
3. Clique no nome da credencial para editar

### 3. Configure as URIs de Redirecionamento Autorizadas
No campo "URIs de redirecionamento autorizadas", adicione EXATAMENTE estas URIs:

```
http://localhost:8080/
http://localhost:8080
```

⚠️ **IMPORTANTE**: 
- Adicione AMBAS as versões (com e sem barra final)
- Use exatamente `localhost` (não `127.0.0.1`)
- A porta deve ser `8080`

### 4. Salve as Alterações
1. Clique em "Salvar" no final da página
2. Aguarde alguns segundos para as mudanças propagarem

### 5. Baixe as Credenciais Novamente (Opcional)
Se ainda não funcionar:
1. Clique no botão de download (⬇️) ao lado da credencial
2. Substitua o arquivo `credentials/google_calendar_credentials.json`

### 6. Limpe o Cache de Autenticação
```bash
# Remova o token antigo se existir
rm credentials/google_calendar_token.pickle
```

### 7. Execute o Teste Novamente
```bash
python scripts/test_google_calendar.py --auth-only
```

## 🔍 Verificação no Console

Para confirmar que está correto, no Google Cloud Console você deve ver:

**Tipo de aplicativo**: Aplicativo para desktop
**URIs de redirecionamento autorizadas**:
- http://localhost:8080/
- http://localhost:8080

## 💡 Dicas Adicionais

1. **Se estiver usando WSL ou Docker**, pode ser necessário configurar port forwarding
2. **Se a porta 8080 estiver ocupada**, você pode mudar no código e no Console:
   - No código: `flow.run_local_server(port=NOVA_PORTA)`
   - No Console: Adicione `http://localhost:NOVA_PORTA/`
3. **Para produção**, considere usar Service Account em vez de OAuth2

## 🚨 Outros Erros Comuns

### "access_blocked"
- O app pode estar em modo de teste no Google Cloud Console
- Adicione o email do usuário como "Usuário de teste" na tela de consentimento OAuth

### "invalid_client"
- As credenciais baixadas podem estar corrompidas
- Baixe novamente do Google Cloud Console

### "insufficient_scope"
- Verifique se os escopos do Calendar estão habilitados
- Na tela de consentimento OAuth, adicione os escopos necessários