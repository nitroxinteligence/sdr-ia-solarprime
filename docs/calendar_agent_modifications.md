# CalendarAgent - Modificações para Coleta de Emails

## Resumo das Modificações

O arquivo `app/teams/agents/calendar.py` foi modificado para incluir funcionalidade de coleta de emails dos participantes durante o agendamento de reuniões.

## Principais Alterações

### 1. Nova Tool: `collect_attendee_emails_tool`

- **Função**: Coleta emails dos participantes antes do agendamento
- **Contexto**: Personaliza a mensagem baseada no tipo de reunião
- **Localização**: Linha 172-183 no arquivo

### 2. Modificação na Tool: `schedule_meeting_tool`

- **Novo parâmetro**: `attendee_emails: str = ""`
- **Funcionalidade**: Aceita emails separados por vírgula
- **Conversão**: Transforma string em lista automaticamente
- **Localização**: Linha 105-137 no arquivo

### 3. Método: `collect_attendee_emails()`

- **Objetivo**: Solicita emails dos participantes de forma contextual
- **Contextos suportados**: 
  - Visita técnica
  - Assinatura de contrato
  - Reunião padrão
- **Localização**: Linha 223-290 no arquivo

### 4. Atualização do `schedule_meeting()`

- **Novo parâmetro**: `attendee_emails: List[str] = None`
- **Logs**: Registra emails coletados para debug
- **Descrição**: Inclui participantes na descrição do evento
- **Retorno**: Adiciona informações dos participantes na resposta

### 5. Atualização do `_build_description()`

- **Novo parâmetro**: `attendee_emails: List[str] = None`
- **Funcionalidade**: Adiciona lista de participantes na descrição
- **Aviso**: Informa sobre convites não automáticos

### 6. Atualização do `_save_meeting_to_db()`

- **Novo parâmetro**: `attendee_emails: List[str] = None`
- **Campos salvos**: 
  - `meeting_attendees`: Lista de emails
  - `attendees_count`: Número de participantes

### 7. Instruções do Agente

- **Nova regra**: SEMPRE coletar emails antes de agendar
- **Novo fluxo obrigatório**:
  1. Use `collect_attendee_emails_tool`
  2. Verifique disponibilidade
  3. Agende incluindo emails coletados

## Fluxo de Uso

```python
# 1. Coleta de emails (obrigatório)
await calendar_agent.collect_attendee_emails("apresentação inicial")

# 2. Agendamento com emails
await calendar_agent.schedule_meeting(
    lead_id="123",
    title="Reunião Solar Prime",
    date="15/12/2024",
    time="14:00",
    attendee_emails=["joao@empresa.com", "maria@empresa.com"]
)
```

## Benefícios

### Para o Sistema
- **Rastreamento**: Emails salvos no banco de dados
- **Logs**: Registro detalhado para debug
- **Flexibilidade**: Suporte a múltiplos participantes

### Para o Usuário
- **Contextualização**: Mensagens personalizadas por tipo de reunião
- **Transparência**: Aviso sobre convites não automáticos
- **Organização**: Lista de participantes na descrição

### Para o Negócio
- **Profissionalismo**: Reuniões bem estruturadas
- **Eficiência**: Processo padronizado
- **Rastreabilidade**: Histórico de participantes

## Limitações Conhecidas

- **Google Calendar**: Service accounts não enviam convites automáticos
- **Solução**: Links devem ser compartilhados manualmente
- **Documentação**: Participantes listados na descrição

## Campos do Banco de Dados

### Tabela `leads`
- `meeting_attendees`: JSONB - Lista de emails
- `attendees_count`: INTEGER - Número de participantes

### Exemplo de Dados Salvos
```json
{
  "meeting_attendees": ["joao@empresa.com", "maria@empresa.com"],
  "attendees_count": 2,
  "google_event_id": "abc123",
  "meeting_scheduled_at": "2024-12-15T14:00:00"
}
```

## Logs de Debug

```
📧 Coletando emails dos participantes - Contexto: apresentação
📧 Emails dos participantes coletados: joao@empresa.com, maria@empresa.com
✅ Reunião salva no lead 123 com 2 participantes
```

## Compatibilidade

- ✅ Mantém compatibilidade com agendamentos sem emails
- ✅ Framework AGnO preservado
- ✅ Estrutura existente mantida
- ✅ Logs e error handling aprimorados

## Próximos Passos

1. **Teste**: Validar coleta de emails em cenários reais
2. **Integração**: Conectar com Evolution API para compartilhar links
3. **UI**: Criar interface para visualizar participantes
4. **Automação**: Implementar envio automático de links via WhatsApp