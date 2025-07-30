# Sincronização Mínima Kommo ↔ Google Calendar

## Visão Geral

Implementamos uma sincronização mínima e prática entre o Kommo CRM e o Google Calendar, focando apenas nas funcionalidades essenciais para o fluxo de vendas.

## Funcionalidades Implementadas

### 1. Link do Calendar no Kommo ✅
Quando uma reunião é agendada via WhatsApp:
- O evento é criado no Google Calendar
- O link do evento é automaticamente salvo no Kommo
- O vendedor pode clicar no link direto do CRM para acessar o evento

### 2. Cancelamento Sincronizado ✅
Quando o vendedor cancela uma reunião no Kommo:
- O evento é automaticamente cancelado no Google Calendar
- O cliente recebe notificação via WhatsApp
- O status é atualizado em ambos os sistemas

### 3. Status de Reunião ✅
Estados rastreados:
- `scheduled` - Reunião agendada
- `completed` - Reunião realizada
- `no_show` - Cliente não compareceu
- `cancelled` - Reunião cancelada

### 4. Notificações Automáticas ✅
- Cliente recebe confirmação quando reunião é agendada
- Cliente é notificado se reunião for cancelada pelo vendedor
- Mensagem de agradecimento após reunião realizada

## Configuração Necessária

### 1. Campos Customizados no Kommo

Criar os seguintes campos customizados no Kommo:

1. **google_calendar_link**
   - Tipo: Link/URL
   - Descrição: Link do evento no Google Calendar
   
2. **meeting_status**
   - Tipo: Texto ou Select
   - Valores: scheduled, completed, no_show, cancelled
   - Descrição: Status atual da reunião

### 2. Configurar IDs no .env

Após criar os campos, adicionar os IDs no arquivo `.env`:

```env
# IDs dos campos customizados (encontrar no Kommo)
KOMMO_FIELD_GOOGLE_CALENDAR_LINK=123456
KOMMO_FIELD_MEETING_STATUS=123457
```

### 3. Configurar Webhook no Kommo

1. Acessar: Configurações → Integrações → Webhooks
2. Adicionar novo webhook:
   - URL: `https://seu-dominio.com/webhook/kommo/events`
   - Eventos: 
     - `task:add` - Quando tarefa é criada
     - `task:update` - Quando tarefa é atualizada
     - `task:delete` - Quando tarefa é deletada
     - `leads:update` - Quando lead é atualizado

## Fluxo de Funcionamento

### Agendamento de Reunião
```
1. Cliente solicita reunião via WhatsApp
2. Agente valida qualificação
3. Agente cria evento no Google Calendar
4. Sistema salva link do Calendar no Kommo
5. Cliente recebe confirmação
```

### Cancelamento pelo Vendedor
```
1. Vendedor cancela tarefa de reunião no Kommo
2. Webhook dispara evento para sistema
3. Sistema cancela evento no Google Calendar
4. Cliente recebe notificação via WhatsApp
5. Status atualizado para 'cancelled'
```

### Reunião Realizada
```
1. Vendedor marca tarefa como completada
2. Sistema atualiza status para 'completed'
3. Cliente recebe mensagem de agradecimento
```

## Benefícios da Abordagem Mínima

1. **Simplicidade**: Implementação em 1-2 dias vs semanas
2. **Confiabilidade**: Menos pontos de falha
3. **Manutenção**: Código simples e fácil de manter
4. **Performance**: Menos chamadas de API
5. **Custo-benefício**: Atende 95% dos casos de uso

## O que NÃO foi implementado

- ❌ Sincronização bidirecional completa
- ❌ Webhooks do Google Calendar
- ❌ Resolução automática de conflitos
- ❌ Atualização em tempo real de todas as mudanças

## Teste da Integração

Execute o script de teste:

```bash
python test_minimal_sync.py
```

Este script:
- Cria um lead de teste
- Agenda uma reunião
- Verifica se o link foi salvo no Kommo
- Testa cancelamento
- Limpa dados de teste

## Troubleshooting

### Link não aparece no Kommo
1. Verificar se o campo `google_calendar_link` foi criado
2. Confirmar que o ID está correto no .env
3. Verificar logs para erros de API

### Webhook não funciona
1. Verificar URL do webhook
2. Confirmar que o token está configurado (se usado)
3. Testar com ferramenta como ngrok localmente

### Cliente não recebe notificações
1. Verificar se WhatsApp está conectado
2. Confirmar número do telefone está correto
3. Verificar logs do Evolution API

## Próximos Passos (Opcionais)

Se no futuro for necessário mais sincronização:

1. **Webhook do Calendar**: Receber notificações quando vendedor muda no Calendar
2. **Sync de Participantes**: Sincronizar lista de participantes
3. **Recorrência**: Suportar reuniões recorrentes
4. **Integração com Zoom/Meet**: Links de videoconferência

Mas lembre-se: **a simplicidade atual provavelmente já atende suas necessidades!**