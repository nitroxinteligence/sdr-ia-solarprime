# Análise e Solução do Erro: `invalid input syntax for type uuid: "None"`

## 1. Diagnóstico do Problema

O erro `invalid input syntax for type uuid: "None"` é um erro clássico do PostgreSQL que ocorre quando sua aplicação tenta inserir ou atualizar uma coluna do tipo `UUID` com um valor que não é um UUID válido. 

No seu caso específico, o valor problemático é a string `"None"`.

**Causa Raiz:**

O problema não está no banco de dados, mas na forma como a aplicação Python está enviando os dados. Em algum ponto do seu código, um valor `None` do Python está sendo convertido para a string `"None"` antes de ser enviado para o Supabase (que usa PostgreSQL). O PostgreSQL não sabe como converter a string `"None"` para o formato `UUID`, resultando no erro `22P02` (invalid text representation).

O correto seria enviar o valor `None` do Python, que a biblioteca `supabase-python` traduziria corretamente para o valor `NULL` do SQL.

## 2. Análise do Código e Localização da Falha

O log de erro `❌ Erro ao enviar lembrete de reunião` aponta diretamente para a funcionalidade de lembretes. Analisando a estrutura do seu projeto, os arquivos mais prováveis onde o erro pode estar ocorrendo são:

1.  **`app/services/followup_executor_service.py`**: Este serviço parece ser o responsável por processar e enviar lembretes. A falha provavelmente está na lógica que envia os lembretes de reunião (`_send_meeting_reminder` ou uma função similar).
2.  **`app/services/calendar_sync_service.py`**: Este serviço também lida com eventos de calendário e pode estar envolvido no processo de criação ou atualização de lembretes.
3.  **`app/teams/agents/calendar.py`**: O agente de calendário é quem orquestra as operações de agendamento e pode estar passando um valor `None` de forma incorreta para uma função de atualização no banco.
4.  **`app/integrations/supabase_client.py`**: Embora menos provável que seja a origem do erro, é aqui que a chamada final para o banco de dados é feita. Uma análise deste arquivo pode revelar como os dados estão sendo formatados antes do `INSERT` ou `UPDATE`.

**Hipótese Principal:**

A função que envia o lembrete de reunião tenta atualizar uma tabela no Supabase (provavelmente `calendar_events` ou `follow_ups`). Nessa operação de `UPDATE` ou `INSERT`, ela está passando um dicionário onde uma das chaves, que corresponde a uma coluna `UUID` no banco, tem o valor `None`. Em algum momento antes da chamada final, esse `None` é convertido para a string `"None"`.

Um cenário comum é a tentativa de associar o lembrete a um `lead_id` ou `conversation_id` que, por algum motivo, não foi encontrado e resultou em uma variável com valor `None`.

**Exemplo de Código Problemático (Hipotético):**

```python
# Em algum lugar do código...

lead_id = find_lead_id_for_event(event) # Esta função pode retornar None

# ...

update_data = {
    'status': 'reminder_sent',
    'lead_id': str(lead_id)  # <<<< ERRO AQUI! str(None) se torna 'None'
}

# Esta chamada falhará se a coluna 'lead_id' for do tipo UUID
await supabase_client.client.table('reminders').update(update_data).eq('id', reminder_id).execute()
```

## 3. Estratégia de Solução Inteligente

A solução correta é garantir que o valor `None` do Python seja sempre passado como `None` para a biblioteca do Supabase, permitindo que ela o converta para `NULL` no SQL. Nunca se deve converter um valor que pode ser `None` para string (`str()`) quando ele se destina a uma coluna de banco de dados que não é do tipo texto.

### Passo 1: Identificar a Operação de Banco de Dados Exata

É crucial encontrar a linha de código exata que está fazendo a chamada `insert` ou `update` para a tabela que contém a coluna `UUID` problemática. Use a busca no seu editor de código para procurar por `update` e `insert` nos arquivos mencionados (`followup_executor_service.py`, `calendar_sync_service.py`, etc.) e analise os dados que estão sendo passados.

### Passo 2: Corrigir a Passagem de Parâmetros

Uma vez identificada a operação, a correção envolve garantir que a variável que pode ser `None` não seja convertida para string.

**Exemplo de Correção:**

```python
# Código CORRIGIDO

lead_id = find_lead_id_for_event(event) # Retorna None ou um UUID válido

# ...

update_data = {
    'status': 'reminder_sent',
    'lead_id': lead_id  # <<<< CORREÇÃO: Passe o valor None diretamente
}

# Esta chamada agora funcionará corretamente
await supabase_client.client.table('reminders').update(update_data).eq('id', reminder_id).execute()
```

### Passo 3: Adicionar Validação e Tratamento de Erros (Robustez)

Para tornar o sistema mais robusto, adicione validações para garantir que IDs essenciais existam antes de prosseguir. Isso evita que o erro ocorra em primeiro lugar.

**Exemplo de Código Robusto:**

```python
# Em followup_executor_service.py ou similar

async def _send_reminder(self, event: Dict[str, Any]):
    try:
        lead_id = event.get('lead_id')
        
        # VALIDAÇÃO: Garantir que o lead_id existe e é um UUID válido
        if not lead_id:
            logger.error(f"❌ Erro crítico: Tentativa de enviar lembrete para evento sem lead_id. Evento: {event.get('id')}")
            # Marcar o evento como falho para não tentar novamente
            await self._mark_reminder_as_failed(event.get('id'), "lead_id ausente")
            return

        # Buscar dados do lead
        lead_result = await self.db.get_lead_by_id(lead_id)
        
        if not lead_result:
            logger.error(f"❌ Lead {lead_id} não encontrado no banco para envio de lembrete.")
            await self._mark_reminder_as_failed(event.get('id'), "Lead não encontrado no DB")
            return

        phone = lead_result.get('phone_number')
        if not phone:
            # ... (tratamento de erro)
            return

        # ... (lógica de envio da mensagem)

        # Atualizar o status do lembrete no banco
        await self.db.client.table('calendar_events').update({
            'reminder_sent': True
        }).eq('id', event['id']).execute()

    except Exception as e:
        logger.error(f"❌ Erro ao enviar lembrete para evento {event.get('id')}: {e}")
        # Opcional: marcar como falho no banco
        await self._mark_reminder_as_failed(event.get('id'), str(e))

```

## 4. Resumo da Solução

1.  **Localize a Falha:** Investigue os arquivos `followup_executor_service.py` e `calendar_sync_service.py` para encontrar a chamada de `insert` ou `update` que está causando o erro.
2.  **Corrija a Conversão:** Certifique-se de que qualquer variável que possa conter um `UUID` ou `None` **não** seja convertida para `str()` antes de ser passada para a biblioteca do Supabase.
3.  **Implemente Validações:** Adicione checagens para garantir que variáveis de ID (como `lead_id`) não sejam `None` antes de tentar usá-las em operações de banco de dados. Se forem `None`, registre um erro claro e evite a chamada ao banco.

Seguindo estes passos, você resolverá o erro atual e tornará seu sistema mais seguro contra falhas semelhantes no futuro.
