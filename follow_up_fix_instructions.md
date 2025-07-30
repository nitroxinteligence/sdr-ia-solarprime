# Instruções para Corrigir o Sistema de Follow-up

## 🔧 Correções Implementadas

### 1. **main_v2.py**
- ✅ Corrigido bug na linha 41
- ✅ Importado `agent_config` corretamente
- ✅ Mudado de `config.enable_follow_up` para `agent_config.enable_follow_up`

### 2. **main.py**
- ✅ Adicionada importação do `follow_up_scheduler`
- ✅ Adicionada inicialização do scheduler no startup
- ✅ Adicionado código para parar o scheduler no shutdown
- ✅ Logs informativos sobre configuração de follow-up

### 3. **follow_up_workflow.py**
- ✅ Reduzido intervalo de verificação de 5 minutos para 1 minuto
- ✅ Mantido tratamento de erros robusto

## 📋 Passos para Aplicar as Correções

### 1. Verificar qual main.py está em uso
```bash
# No servidor, execute:
ps aux | grep uvicorn

# Ou se usando Docker:
docker ps
docker logs <container_id>
```

### 2. Reiniciar o servidor
```bash
# Se usando main.py:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Se usando main_v2.py:
uvicorn api.main_v2:app --reload --host 0.0.0.0 --port 8000

# Ou reiniciar o container Docker
docker-compose restart
```

### 3. Verificar os logs
Procure por estas mensagens nos logs:
- `✅ Follow-up scheduler iniciado`
- `📅 Verificando follow-ups a cada 1 minuto`
- `⏰ Primeiro follow-up após 30 minutos`

### 4. Verificar o status do sistema
```bash
# Execute o script de verificação:
python check_follow_up_status.py

# Para criar um follow-up de teste:
python check_follow_up_status.py --test
```

## 🧪 Testando o Sistema

### Teste Manual Rápido
1. Envie uma mensagem para o bot via WhatsApp
2. O bot responderá e criará um follow-up
3. Aguarde 30 minutos
4. Verifique se recebeu a mensagem de follow-up

### Monitorar em Tempo Real
```bash
# Ver logs do follow-up scheduler:
tail -f logs/app.log | grep -i follow

# Ver follow-ups sendo processados:
watch -n 30 'python check_follow_up_status.py'
```

## ⚠️ Possíveis Problemas

### 1. Scheduler não inicia
- Verifique se `ENABLE_FOLLOW_UP=true` no `.env`
- Verifique os logs por erros de importação
- Certifique-se de que o Redis está rodando

### 2. Follow-ups criados mas não executados
- Verifique se o scheduler está rodando (logs)
- Execute `check_follow_up_status.py` para ver follow-ups atrasados
- Verifique se o Evolution API está conectado

### 3. Mensagens não enviadas
- Verifique conexão com WhatsApp
- Verifique se o número tem o formato correto (+5511...)
- Verifique logs do Evolution API

## 📊 Verificação de Sucesso

O sistema está funcionando corretamente quando:
1. ✅ Logs mostram "Follow-up scheduler iniciado"
2. ✅ Follow-ups pendentes são processados a cada minuto
3. ✅ Mensagens são enviadas nos tempos configurados
4. ✅ Status muda de 'pending' para 'executed' no banco

## 🆘 Suporte

Se ainda houver problemas:
1. Execute `check_follow_up_status.py` e compartilhe o output
2. Verifique os logs completos do servidor
3. Verifique a tabela `follow_ups` no Supabase
4. Confirme que todas as variáveis de ambiente estão corretas