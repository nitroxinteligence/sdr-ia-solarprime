# Configuração de Produção - Integração Kommo

## Visão Geral

O sistema **SDR IA SolarPrime** possui descoberta automática inteligente de campos do Kommo CRM. Não é necessário configurar IDs de campos manualmente no `.env` para produção.

## Como Funciona

### 1. Descoberta Automática

O sistema usa o **Long-Lived Token** do Kommo para:
- Buscar todos os campos customizados via API
- Mapear automaticamente por palavras-chave inteligentes
- Criar cache em memória para otimização
- Atualizar cache a cada 1 hora

### 2. Mapeamento Inteligente

O sistema detecta campos automaticamente baseado em palavras-chave:

```python
# Exemplos de mapeamento automático:
"WhatsApp" → whatsapp_number
"Valor Conta Energia" → energy_bill_value
"Score Qualificação" → qualification_score
"Solução Solar" → solution_type
"Link do evento no Google Calendar" → google_calendar_link
"Status atual da reunião" → meeting_status
```

### 3. Uso no Código

No código, sempre use os nomes internos dos campos:

```python
# ✅ Correto - usa nome interno
await kommo_service.update_lead_custom_field(
    lead_id=lead_id,
    field_name='google_calendar_link',  # Nome interno
    value=calendar_link
)

# ❌ Incorreto - não use nome do Kommo
await kommo_service.update_lead_custom_field(
    lead_id=lead_id,
    field_name='Link do evento no Google Calendar',  # Nome do Kommo
    value=calendar_link
)
```

## Configuração para Produção

### 1. Variáveis Obrigatórias

Apenas estas variáveis são necessárias no `.env`:

```env
# Kommo CRM - Configuração Principal
KOMMO_CLIENT_ID=seu-client-id
KOMMO_CLIENT_SECRET=seu-client-secret
KOMMO_SUBDOMAIN=seu-subdominio
KOMMO_PIPELINE_ID=id-do-funil
KOMMO_LONG_LIVED_TOKEN=seu-token-longo
```

### 2. Campos Customizados no Kommo

Crie estes campos no Kommo (os nomes podem variar):

| Campo Interno | Tipo no Kommo | Exemplo de Nome no Kommo |
|--------------|---------------|-------------------------|
| whatsapp_number | Texto | "WhatsApp" ou "Telefone" |
| energy_bill_value | Numérico | "Valor Conta" ou "Fatura" |
| qualification_score | Numérico | "Score" ou "Pontuação" |
| solution_type | Seleção | "Solução" ou "Produto" |
| lead_source | Seleção | "Origem" ou "Fonte" |
| ai_notes | Texto | "Observações IA" |
| google_calendar_link | URL | "Link Calendar" |
| meeting_status | Seleção | "Status Reunião" |

### 3. Verificação

Execute o script de verificação:

```bash
python test_auto_discovery.py
```

Isso mostrará:
- Todos os campos encontrados no Kommo
- Mapeamento automático aplicado
- Teste de funcionamento

## Vantagens da Descoberta Automática

1. **Zero Configuração Manual**: Não precisa adicionar IDs no `.env`
2. **Flexibilidade**: Funciona com qualquer nome de campo
3. **Multi-Idioma**: Detecta campos em português ou inglês
4. **Manutenção Simples**: Adicione campos no Kommo sem alterar código
5. **Pronto para Produção**: Sistema robusto e testado

## Troubleshooting

### Campo não está sendo detectado?

1. Verifique o nome do campo no Kommo
2. Adicione palavras-chave ao nome (ex: "WhatsApp" para telefone)
3. O sistema detecta por palavras parciais

### Cache desatualizado?

O cache é atualizado automaticamente a cada 1 hora. Para forçar:

```python
kommo_service._custom_fields_by_name = None
kommo_service._fields_last_update = None
```

### Logs de Diagnóstico

O sistema registra todos os campos detectados:

```
2025-07-30 02:11:39.931 | INFO | Campo mapeado: 'WhatsApp' (ID: 392802, Tipo: text)
2025-07-30 02:11:39.931 | INFO | Campo mapeado: 'Link do evento no Google Calendar' (ID: 395520, Tipo: url)
```

## Resumo

O sistema **já está 100% pronto para produção** com descoberta automática inteligente de campos. Basta configurar o Long-Lived Token e criar os campos no Kommo com nomes descritivos.