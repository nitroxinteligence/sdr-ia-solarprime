# Documentação: Warning de Service Account no Google Calendar

## Data: 08/08/2025

## Sobre o Warning

O warning **"Service Account não pode convidar participantes sem Domain-Wide Delegation. Ignorando attendees."** é uma mensagem informativa, **não é um erro**. Ele aparece quando o sistema tenta adicionar participantes a um evento do Google Calendar usando uma Service Account sem configuração de Domain-Wide Delegation.

## O que é Domain-Wide Delegation?

Domain-Wide Delegation é uma configuração avançada do Google Workspace que permite que uma Service Account aja em nome de usuários do domínio. Sem esta configuração, a Service Account tem limitações:

- ✅ **Pode**: Criar eventos no calendário
- ✅ **Pode**: Adicionar descrições, locais, horários
- ✅ **Pode**: Gerar links de reunião alternativos (Jitsi Meet)
- ❌ **Não pode**: Enviar convites por email para participantes
- ❌ **Não pode**: Criar Google Meet nativamente (em alguns casos)

## Impacto no Sistema

### Funcionalidades que Continuam Funcionando:
1. **Criação de Eventos**: Eventos são criados normalmente no Google Calendar
2. **Informações do Evento**: Todas as informações (data, hora, descrição) são salvas
3. **Links de Reunião**: Sistema gera automaticamente links Jitsi Meet como alternativa
4. **Sincronização**: Eventos aparecem no calendário configurado

### Limitações:
1. **Sem Convites Automáticos**: Participantes não recebem email automático do Google
2. **Sem Google Meet Nativo**: Em alguns casos, Google Meet pode não ser criado

## Como Resolver (Opcional)

Se quiser remover o warning e habilitar todas as funcionalidades, você precisa:

1. **Ter uma conta Google Workspace** (não funciona com contas Gmail pessoais)

2. **Configurar Domain-Wide Delegation**:
   - Acessar o Admin Console do Google Workspace
   - Ir para Segurança > Controles de API
   - Configurar delegação para a Service Account
   - Adicionar os escopos necessários

3. **Adicionar variável de ambiente**:
   ```bash
   GOOGLE_WORKSPACE_USER_EMAIL=admin@suaempresa.com
   ```

## Recomendação

**Para a maioria dos casos, o warning pode ser ignorado com segurança**. O sistema está configurado para funcionar perfeitamente sem Domain-Wide Delegation:

- ✅ Eventos são criados normalmente
- ✅ Links de reunião alternativos são gerados automaticamente
- ✅ Todas as informações importantes são preservadas
- ✅ O agente informa o cliente sobre a reunião agendada

O warning é apenas informativo e não afeta a funcionalidade principal do sistema de agendamento.

## Conclusão

Este é um warning esperado e não representa um problema. O sistema foi projetado para trabalhar com ou sem Domain-Wide Delegation, adaptando-se automaticamente às limitações e fornecendo alternativas quando necessário.