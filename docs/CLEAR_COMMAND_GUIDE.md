# Guia do Comando #CLEAR

## Visão Geral

O comando `#CLEAR` é uma funcionalidade especial do SDR IA SolarPrime que permite limpar completamente o histórico de conversa e dados de um usuário. Ideal para testes e desenvolvimento.

## Como Usar

### Via WhatsApp

1. Abra uma conversa com o bot no WhatsApp
2. Envie a mensagem: `#CLEAR`
3. O bot irá:
   - Deletar todo o histórico de mensagens
   - Limpar a memória do agente
   - Remover dados de qualificação
   - Cancelar follow-ups pendentes
   - Enviar uma confirmação

### Resposta do Bot

Após executar o comando, você receberá:

```
✅ *Comando #CLEAR executado com sucesso!*

🧹 Todas as informações foram limpas:
• Histórico de mensagens deletado
• Memória do agente resetada
• Dados de qualificação removidos
• Follow-ups cancelados

💬 Você pode iniciar uma nova conversa agora.
Olá! Como posso ajudá-lo hoje?
```

## O que é Limpo

### 1. Banco de Dados (Supabase)
- **Mensagens**: Todas as mensagens da conversa são deletadas
- **Conversa**: Status resetado para INITIAL_CONTACT
- **Lead**: Registro do lead é completamente removido
- **Follow-ups**: Todos os follow-ups pendentes são cancelados

### 2. Cache (Redis)
- Estado da conversa
- Métricas de reasoning
- Dados do lead em cache
- Informações de estágio
- Contexto da conversa

### 3. Memória do Agente
- Sessão do agente é removida
- Memória de contexto é limpa
- Agente será recriado na próxima mensagem

## Casos de Uso

### 1. Testes de Desenvolvimento
- Testar diferentes fluxos de conversa
- Simular novos usuários
- Validar comportamento inicial do bot

### 2. Demonstrações
- Limpar dados antes de uma demonstração
- Garantir experiência limpa para apresentações

### 3. Solução de Problemas
- Resetar conversas com problemas
- Limpar estados corrompidos
- Reiniciar qualificação

## Script de Teste

Para testar o comando sem usar WhatsApp:

```bash
python test_clear_command.py
```

O script irá:
1. Pedir o número de telefone
2. Mostrar dados existentes
3. Executar o comando #CLEAR
4. Verificar se os dados foram limpos

## Segurança

### Considerações
- O comando é irreversível
- Todos os dados são permanentemente deletados
- Não há confirmação adicional via WhatsApp

### Recomendações para Produção
1. Adicionar lista de números autorizados
2. Implementar confirmação dupla
3. Registrar uso do comando em logs de auditoria
4. Considerar desabilitar em produção

### Configuração de Segurança (Opcional)

Para restringir o comando a números específicos, adicione ao `.env`:

```env
CLEAR_COMMAND_ENABLED=true
CLEAR_COMMAND_ALLOWED_PHONES=5511999999999,5511888888888
```

## Troubleshooting

### Comando não funciona
1. Verifique se o texto é exatamente `#CLEAR` (maiúsculas)
2. Confirme que não há espaços extras
3. Verifique os logs para erros

### Dados não foram limpos completamente
1. Verifique conexão com Supabase
2. Confirme permissões no banco de dados
3. Verifique se Redis está acessível

### Erro ao executar
1. Verifique os logs em `logs/`
2. Confirme que todos os serviços estão rodando
3. Execute o script de teste para diagnóstico

## Implementação Técnica

### Arquivo Principal
`services/whatsapp_service.py` - Método `_handle_clear_command`

### Fluxo de Execução
1. Detecta comando `#CLEAR` no processamento de mensagem
2. Chama `_handle_clear_command`
3. Executa limpeza em ordem:
   - Mensagens do banco
   - Reset da conversa
   - Cache Redis
   - Memória do agente
   - Dados do lead
   - Follow-ups
4. Envia confirmação ao usuário

### Métodos Adicionados
- `MessageRepository.delete_conversation_messages()`
- `ConversationRepository.reset_conversation()`
- `ConversationRepository.get_conversation_by_phone()`
- `LeadRepository.delete_lead()`
- `RedisFallbackService.clear_conversation_state()`
- `FollowUpService.cancel_all_follow_ups_for_phone()`