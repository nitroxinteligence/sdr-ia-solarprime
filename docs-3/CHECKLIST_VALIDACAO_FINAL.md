# ✅ CHECKLIST DE VALIDAÇÃO FINAL - PIPELINE CRM

## 🎯 3 VALIDAÇÕES PARA GARANTIR 100%

### 1️⃣ VERIFICAR NOMES DOS CARDS NO KOMMO
```
☐ Abrir Kommo CRM
☐ Ir para o pipeline de vendas
☐ Confirmar que os cards têm EXATAMENTE estes nomes:
   ☐ Novo Lead
   ☐ Em Qualificação
   ☐ Qualificado
   ☐ Reunião Agendada
   ☐ Não Interessado

⚠️ Se algum nome for diferente (ex: "Lead Qualificado" ao invés de "Qualificado"):
   → Editar arquivo: app/teams/agents/crm.py
   → Linhas 252-259
   → Mudar o nome para corresponder EXATAMENTE ao Kommo
```

### 2️⃣ VERIFICAR VARIÁVEIS DE AMBIENTE
```bash
☐ Abrir arquivo .env
☐ Confirmar que existem:
   ☐ KOMMO_PIPELINE_ID=xxxxx        # ID numérico do pipeline
   ☐ KOMMO_LONG_LIVED_TOKEN=xxxxx   # Token de acesso
   ☐ KOMMO_BASE_URL=https://api-c.kommo.com  # (opcional, tem default)
   ☐ KOMMO_SUBDOMAIN=xxxxx          # Subdomínio da conta

⚠️ Se faltar alguma:
   → Pegar valores no Kommo > Configurações > API
```

### 3️⃣ VERIFICAR LOGS DE INICIALIZAÇÃO
```bash
☐ Reiniciar a aplicação
☐ Verificar no console por estas mensagens:
   ☐ "✅ Kommo Auto Sync ready | sync_interval=30s"
   ☐ "✅ Campos e stages do Kommo carregados automaticamente"
   ☐ "Stage 'XXX' mapeado: ID YYY" (para cada card)

⚠️ Se não aparecerem:
   → Verificar token de acesso
   → Verificar conexão com internet
   → Ver logs de erro
```

---

## 🧪 TESTE RÁPIDO DE FUNCIONAMENTO

### Enviar mensagem de teste:
```
1. WhatsApp: "Minha conta de luz é R$ 5.000"
2. Aguardar 30 segundos
3. Verificar no Kommo se lead moveu para "Qualificado"
```

### Verificar nos logs:
```bash
grep "movido para estágio" logs/app.log | tail -5
```

Deve aparecer:
```
📍 Lead XXXX movido para estágio qualificado
```

---

## ✅ CONFIRMAÇÃO FINAL

☐ Todos os 3 itens verificados
☐ Teste rápido funcionou
☐ Logs mostram movimentação

**SE TUDO OK = SISTEMA 100% FUNCIONAL! 🚀**

---

## 📞 SUPORTE

Se algo não funcionar após essas validações:

1. **Verificar logs completos**:
   ```bash
   grep -B5 -A5 "Erro ao mover" logs/app.log
   ```

2. **Testar conexão com Kommo**:
   ```bash
   curl -H "Authorization: Bearer SEU_TOKEN" \
        https://api-c.kommo.com/api/v4/account
   ```

3. **Verificar IDs do pipeline**:
   - No Kommo, abrir Developer Tools (F12)
   - Ir para Network
   - Clicar em um card
   - Ver requisição e pegar pipeline_id

---

*Checklist criado em: 08/08/2025*
*Tempo estimado: 10 minutos*
*Complexidade: ZERO - Apenas validações*