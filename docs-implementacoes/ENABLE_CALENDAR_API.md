# 🚀 Ativar Google Calendar API - Último Passo!

## ✅ Status Atual
- ✅ Credenciais corretas (Desktop App)
- ✅ Autenticação funcionando
- ❌ API do Calendar não está ativada

## 📋 Solução Rápida (2 minutos)

### Opção 1: Link Direto (Mais Rápido)
Clique neste link que o erro forneceu:
https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=834251560398

1. Clique em **"ATIVAR"** (botão azul)
2. Aguarde a confirmação
3. Pronto!

### Opção 2: Pelo Console
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Verifique se está no projeto correto (ID: 834251560398)
3. Menu lateral → **"APIs e Serviços"** → **"Biblioteca"**
4. Pesquise: **"Google Calendar API"**
5. Clique no resultado
6. Clique em **"ATIVAR"**

## ⏱️ Aguarde 1-2 minutos

A API pode levar alguns segundos para propagar. Aguarde um pouco antes de testar.

## 🔄 Teste Novamente

```bash
python scripts/test_google_calendar.py
```

## ✅ Resultado Esperado

Após ativar a API, o teste deve:
1. ✅ Inicializar o serviço
2. ✅ Listar eventos (mesmo que vazio)
3. ✅ Criar evento de teste
4. ✅ Mostrar link do evento criado
5. ✅ Atualizar o evento
6. ✅ Cancelar o evento

## 🎉 Sucesso!

Depois de ativar a API, tudo funcionará perfeitamente. Você verá algo como:

```
✅ Evento criado com sucesso!
   ID: abc123...
   Link: https://calendar.google.com/calendar/u/0/r/eventedit/...
```

## 💡 Dica Extra

Se quiser verificar se a API está ativa:
1. No Console, vá para "APIs e Serviços" → "APIs ativadas"
2. Procure por "Google Calendar API"
3. Deve aparecer na lista com status "Ativada"

---

**Você está a apenas 1 clique de concluir a integração!** 🚀