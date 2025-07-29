# 🔧 Como Resolver: Erro 403 access_denied

## ✅ Boa notícia!
O erro de `redirect_uri_mismatch` foi resolvido! Agora é apenas uma questão de permissões.

## 🎯 O que está acontecendo
O app está em modo de teste no Google Cloud Console e apenas usuários aprovados podem acessar.

## 📋 Solução Passo a Passo

### 1. **Acesse o Google Cloud Console**
- Vá para [Google Cloud Console](https://console.cloud.google.com/)
- Selecione seu projeto

### 2. **Configure a Tela de Consentimento OAuth**
1. Menu lateral → "APIs e Serviços" → "Tela de consentimento OAuth"
2. Se ainda não configurou:
   - Tipo de usuário: **Externo** (ou Interno se tiver Google Workspace)
   - Clique em "CRIAR"

### 3. **Informações do App**
Preencha os campos obrigatórios:
- **Nome do app**: SolarPrime IA SDR
- **Email de suporte do usuário**: seu email
- **Logotipo do app**: (opcional)
- **Domínios autorizados**: (deixe vazio por enquanto)
- **Email do desenvolvedor**: seu email

### 4. **Escopos (Scopes)**
1. Clique em "ADICIONAR OU REMOVER ESCOPOS"
2. Procure e adicione estes escopos:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/calendar.events`
3. Clique em "ATUALIZAR"

### 5. **Usuários de Teste** ⚠️ MAIS IMPORTANTE!
1. Na seção "Usuários de teste"
2. Clique em "+ ADICIONAR USUÁRIOS"
3. **Adicione o email**: leonardofvieira00@gmail.com (ou o email que você está usando)
4. Adicione também qualquer outro email que precisará testar
5. Clique em "ADICIONAR"

### 6. **Status do App**
- Por enquanto, mantenha em **"Teste"** (Testing)
- Para produção, será necessário publicar o app (processo mais complexo)

### 7. **Salve e Teste Novamente**
```bash
# Limpe o cache
rm credentials/google_calendar_token.pickle

# Execute o teste
python scripts/test_google_calendar.py --auth-only
```

## 🎯 Resumo Visual

```
Tela de consentimento OAuth
├── Informações do app ✓
├── Escopos ✓
│   ├── calendar ✓
│   └── calendar.events ✓
├── Usuários de teste ✓
│   └── leonardofvieira00@gmail.com ✓ (ADICIONE ESTE!)
└── Status: Teste
```

## 💡 Dicas Importantes

1. **Email correto**: Use o mesmo email que apareceu no erro (leonardofvieira00@gmail.com)
2. **Múltiplos emails**: Você pode adicionar vários emails de teste
3. **Limite**: Máximo de 100 usuários de teste
4. **Validade**: Tokens de teste expiram em 7 dias

## 🚀 Para Produção (Futuro)

Quando quiser usar em produção:
1. Publique o app (botão "PUBLICAR APP")
2. Pode precisar de verificação do Google (para apps com muitos usuários)
3. Considere usar Service Account para automação sem interação

## ❓ Se ainda não funcionar

1. **Verifique o email**: Certifique-se de estar logando com o email adicionado como testador
2. **Aguarde propagação**: Às vezes leva alguns minutos
3. **Limpe cookies**: Tente em aba anônima do navegador
4. **Outro navegador**: Teste em outro navegador

## ✅ Resultado Esperado

Após adicionar seu email como testador, o fluxo OAuth funcionará normalmente:
1. Abrirá o navegador
2. Você fará login
3. Verá a tela de permissões
4. Autorizará o acesso
5. Verá "A autenticação foi concluída!"