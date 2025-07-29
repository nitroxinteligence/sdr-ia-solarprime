# 🔧 SOLUÇÃO DEFINITIVA: Erro redirect_uri_mismatch

## ⚠️ CAUSA DO PROBLEMA

O erro está ocorrendo porque você criou credenciais do tipo **"Aplicativo Web"** em vez de **"Aplicativo para desktop"**.

## ✅ SOLUÇÃO COMPLETA

### 1. **Excluir as Credenciais Antigas**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Vá para "APIs e Serviços" → "Credenciais"
3. **DELETE** a credencial OAuth 2.0 atual

### 2. **Criar NOVAS Credenciais (Tipo Correto)**
1. Clique em "+ CRIAR CREDENCIAIS"
2. Selecione "ID do cliente OAuth"
3. **IMPORTANTE**: Escolha o tipo de aplicativo: **"Aplicativo para computador"** (Desktop)
   - ❌ NÃO escolha "Aplicativo da Web"
   - ✅ ESCOLHA "Aplicativo para computador" ou "Desktop"
4. Nome: "SDR Calendar Desktop"
5. Clique em "Criar"

### 3. **Baixar o Novo Arquivo JSON**
1. Após criar, clique no botão de download (⬇️)
2. Renomeie o arquivo para `google_calendar_credentials.json`
3. Substitua o arquivo antigo em `credentials/`:
   ```bash
   mv ~/Downloads/client_secret_*.json credentials/google_calendar_credentials.json
   ```

### 4. **Verificar o Tipo de Credencial**
Abra o arquivo `credentials/google_calendar_credentials.json` e verifique:

**❌ ERRADO (Aplicativo Web)**:
```json
{
  "web": {
    "client_id": "...",
    "client_secret": "...",
    "redirect_uris": ["..."]
  }
}
```

**✅ CORRETO (Aplicativo Desktop)**:
```json
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

### 5. **Limpar Cache e Testar**
```bash
# Remover token antigo
rm -f credentials/google_calendar_token.pickle

# Testar autenticação
python scripts/test_google_calendar.py --auth-only
```

## 🎯 Por que isso funciona?

- **Aplicativos Desktop** usam `InstalledAppFlow` e não precisam de URIs de redirecionamento específicas
- **Aplicativos Web** precisam de URIs exatas configuradas, o que causa o erro
- O método `run_local_server(port=0)` funciona automaticamente com credenciais Desktop

## 📋 Checklist Rápido

- [ ] Deletou as credenciais antigas no Google Cloud Console
- [ ] Criou novas credenciais tipo **"Aplicativo para computador"**
- [ ] Baixou o novo arquivo JSON
- [ ] Verificou que o JSON tem `"installed"` e não `"web"`
- [ ] Removeu o token.pickle antigo
- [ ] Executou o teste novamente

## 🚨 Se ainda não funcionar

1. **Verifique a tela de consentimento OAuth**:
   - Certifique-se de que está configurada
   - Adicione seu email como "Usuário de teste" se estiver em modo de teste

2. **Tente com outra conta Google**:
   - Às vezes há restrições de organização

3. **Use o método alternativo**:
   ```python
   # Em vez de run_local_server, use:
   creds = flow.run_console()
   ```

## 🎉 Resultado Esperado

Após seguir estes passos, o navegador abrirá normalmente, você fará login, autorizará o acesso, e verá a mensagem de sucesso!