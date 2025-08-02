# 📋 Guia Completo de Configuração Kommo CRM (Atualizado 2025)

Este guia detalha passo a passo como obter todas as credenciais e IDs necessários do Kommo CRM para configurar a integração com o SDR IA SolarPrime.

## 🚀 Nova Abordagem: Configuração Automática!

O sistema agora detecta automaticamente os IDs dos estágios e campos personalizados! Você só precisa configurar o mínimo necessário.

## 🔐 Parte 1: Criando a Integração Privada (OAuth2)

### 1.1 Pré-requisitos

- Você precisa ter **direitos de administrador** na conta Kommo
- A integração será atribuída à conta onde foi criada

### 1.2 Acessar o Painel de Integrações

1. Faça login no seu Kommo CRM: `https://SEU_SUBDOMINIO.kommo.com`
2. Vá para **Configurações** (ícone de engrenagem)
3. Clique em **Integrações**
4. Clique em **"Criar Integração"**
5. Quando perguntado, selecione **"Privada"**

### 1.3 Configurar a Nova Integração

Preencha os campos:
- **Nome da Integração**: `SDR IA SolarPrime`
- **Descrição**: `Integração do agente de vendas inteligente WhatsApp`
- **URL de Redirecionamento**: 
  - Desenvolvimento: `http://localhost:8000/auth/kommo/callback`
  - Produção: `https://SEU_DOMINIO.com/auth/kommo/callback`
  - EasyPanel: `https://sdr-api-evolution-api.fzvgou.easypanel.host/auth/kommo/callback`
- **Permissões**: Marque **"Permitir acesso: Todos"**

### 1.4 Obter as Credenciais OAuth2

1. Após criar a integração, vá para a aba **"Chaves e Escopos"**
2. Copie os seguintes valores:
   - **"ID da Integração"** (Integration ID) → `KOMMO_CLIENT_ID`
   - **"Chave Secreta"** (Secret Key) → `KOMMO_CLIENT_SECRET`

```env
KOMMO_CLIENT_ID=SEU_INTEGRATION_ID_AQUI
KOMMO_CLIENT_SECRET=SUA_SECRET_KEY_AQUI
KOMMO_SUBDOMAIN=seu_subdominio
KOMMO_REDIRECT_URI=https://SEU_DOMINIO.com/auth/kommo/callback
```

**⚠️ IMPORTANTE**: 
- Copie o `CLIENT_SECRET` imediatamente! Ele só é mostrado uma vez
- Integrações privadas não requerem moderação e não são publicadas no Marketplace
- Qualquer administrador da conta pode gerenciar a integração

## 🏗️ Parte 2: Configurando o Pipeline de Vendas

### 2.1 Acessar Configuração do Pipeline

1. Vá para a seção **Leads**
2. Clique em **"Configurar Pipeline"** no canto superior direito
3. Você entrará no modo de edição do pipeline

### 2.2 Criar/Configurar Pipeline

**Limites do Kommo:**
- Máximo de **50 pipelines** por conta
- Cada pipeline pode ter até **100 estágios** (incluindo os do sistema)
- Todos os pipelines terminam com 2 estágios que não podem ser deletados (mas podem ser renomeados)

**Como configurar:**
1. Use o botão **"+"** para adicionar novos estágios
2. Clique em um estágio existente para renomeá-lo ou mudar sua cor
3. **Arraste e solte** para reorganizar a posição dos estágios
4. Arraste para a **lixeira** (canto inferior direito) para deletar

**Estágios sugeridos para SolarPrime:**
1. **Novo Lead** (primeiro contato)
2. **Em Qualificação** (coletando informações)
3. **Qualificado** (lead aprovado)
4. **Reunião Agendada** (aguardando reunião)
5. **Em Negociação** (proposta enviada)
6. **Ganho** (venda fechada) - ID do sistema: 142
7. **Perdido** (lead descartado) - ID do sistema: 143
8. **Não Interessado** (recusou oferta)

**💡 Dica**: Comece com poucos estágios essenciais. Você pode adicionar mais conforme sua necessidade evolui.

### 2.3 Obter ID do Pipeline

#### Método Simplificado (Recomendado)

Com a nova implementação, você só precisa do ID do pipeline:

1. **Via Interface Web**:
   - Abra o pipeline
   - Observe a URL: `https://SEU_SUBDOMINIO.kommo.com/leads/pipeline/PIPELINE_ID`
   - Copie apenas o `PIPELINE_ID`

2. **Configuração Mínima**:
   ```env
   # Apenas isto é necessário!
   KOMMO_PIPELINE_ID=1234567
   ```

**✨ O sistema detecta automaticamente:**
- Todos os IDs dos estágios
- Nomes dos estágios e mapeamento inteligente
- Campos personalizados por nome
- Valores de campos select

### 2.4 Como Funciona a Detecção Automática

O sistema analisa os nomes dos estágios e mapeia automaticamente:

| Palavras-chave | Mapeado para |
|----------------|--------------|
| "novo", "inicial", "primeiro" | `new` |
| "qualifica", "análise", "avalia" | `in_qualification` |
| "qualificado" (sem "não") | `qualified` |
| "reunião", "agendado", "meeting" | `meeting_scheduled` |
| "negociação", "proposta", "orçamento" | `in_negotiation` |
| "ganho", "won", "fechado", "vendido" | `won` |
| "perdido", "lost", "cancelado" | `lost` |
| "não interessado", "desistiu", "recusou" | `not_interested` |

### 2.5 Digital Pipeline (Automação)

O Kommo oferece o **Digital Pipeline** para automação:
- Configure triggers para mover leads automaticamente
- Crie tarefas baseadas em processos de negócio
- Envie notificações automáticas
- Integre com outras ferramentas

Para acessar: **Configurar Pipeline** → **Digital Pipeline**

## 📝 Parte 3: Criando Campos Personalizados

### 3.1 Pré-requisitos

- Você precisa ter **direitos de administrador** para criar campos
- Os campos criados afetam **toda a conta** (todos os leads/contatos)

### 3.2 Como Criar Campos Personalizados

1. **Acesse a seção Leads**
2. **Abra qualquer lead** existente ou clique em **"Quick add"** / **"Criar novo lead"**
3. **Clique na aba "Setup"** no lado esquerdo da tela
4. **Escolha onde criar o campo**: Lead, Contato ou Empresa
5. **Role até a seção desejada** e clique em **"+ Add field"**

### 3.3 Tipos de Campos Disponíveis

| Tipo | Descrição | Uso |
|------|-----------|-----|
| **Text** | Aceita letras e números | Nome, código, referência |
| **Text area** | Texto longo com quebra de linha | Observações, descrições |
| **Numeric** | Apenas números positivos | Valores, quantidades |
| **Select** | Lista com uma opção | Status, tipo, categoria |
| **Multiselect** | Lista com múltiplas opções | Tags, características |
| **Date** | Data com calendário | Datas importantes |
| **URL** | Links clicáveis | Sites, documentos |
| **Checkbox** | Sim/Não | Flags, confirmações |
| **Radio button** | Similar ao select (botões) | Opções exclusivas |
| **Birthday** | Data especial com lembretes | Aniversários |
| **Short address** | Endereço com mapa | Localização |

**⚠️ IMPORTANTE**: 
- O tipo do campo **não pode ser alterado** depois de criado
- Deletar um campo **remove todos os dados** associados em todos os registros

### 3.4 Campos Recomendados para SDR IA

1. **WhatsApp**
   - Tipo: **Text**
   - Nome: `WhatsApp`
   - Tornar obrigatório para estágio "Qualificado"

2. **Valor da Conta de Energia**
   - Tipo: **Numeric**
   - Nome: `Valor Conta Energia`
   - Sem valores negativos

3. **Score de Qualificação**
   - Tipo: **Numeric**
   - Nome: `Score Qualificação`

4. **Solução Solar**
   - Tipo: **Select**
   - Nome: `Solução Solar`
   - Opções: Usina Própria, Fazenda Solar, Consórcio, Consultoria, Não Definido

5. **Fonte do Lead**
   - Tipo: **Select**
   - Nome: `Fonte`
   - Opções: WhatsApp SDR, WhatsApp Manual, Site, Indicação

6. **Mensagem Original**
   - Tipo: **Text area**
   - Nome: `Primeira Mensagem`

7. **ID Conversa WhatsApp**
   - Tipo: **Text**
   - Nome: `ID Conversa`

### 3.5 Configurar Campos Obrigatórios por Estágio

Você pode tornar campos obrigatórios a partir de determinados estágios:

1. No modo de edição do campo, clique em **"Optional"**
2. Escolha a partir de qual estágio o campo deve ser obrigatório
3. O sistema impedirá mudança de estágio sem preencher o campo

### 3.6 Detecção Automática de Campos

**✨ Com a nova implementação, o sistema detecta campos automaticamente!**

| Palavras-chave no nome | Mapeado para |
|------------------------|--------------|
| "whatsapp", "telefone" | Campo WhatsApp |
| "energia", "conta", "valor" | Valor da conta |
| "score", "qualificação" | Score de qualificação |
| "solução", "tipo", "plano" | Tipo de solução |
| "origem", "fonte", "source" | Fonte do lead |
| "primeira", "mensagem" | Primeira mensagem |
| "conversa", "chat", "id" | ID da conversa |

**Não é necessário configurar IDs manualmente!** O sistema encontra os campos pelos nomes.

### 3.7 Para Desenvolvedores

Se precisar obter IDs específicos:

1. **Via Interface**: 
   - Vá ao lead → Setup → seu campo → copie o ID

2. **Via API**:
   ```bash
   curl -X GET https://SEU_SUBDOMINIO.kommo.com/api/v4/leads/custom_fields \
     -H "Authorization: Bearer SEU_ACCESS_TOKEN"
   ```

3. **Via Endpoint de Debug**:
   ```
   GET /auth/kommo/pipeline-config
   ```
   Retorna todos os campos detectados automaticamente.

## 👥 Parte 4: Configurando Usuários Responsáveis

### 4.1 Listar Usuários

1. Vá para **Configurações** → **Usuários e direitos**
2. Anote os nomes dos vendedores que receberão leads

### 4.2 Obter IDs dos Usuários

Via API:
```bash
curl -X GET https://SEU_SUBDOMINIO.kommo.com/api/v4/users \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

Resposta:
```json
{
  "_embedded": {
    "users": [
      {"id": 4001, "name": "João Vendedor", "email": "joao@solarprime.com"},
      {"id": 4002, "name": "Maria Premium", "email": "maria@solarprime.com"},
      {"id": 4003, "name": "Carlos SDR", "email": "carlos@solarprime.com"}
    ]
  }
}
```

Adicione ao .env:
```
KOMMO_USER_DEFAULT=4001
KOMMO_USER_HIGH_VALUE=4002
KOMMO_USER_SALES_MANAGER=4003
```

## 🔗 Parte 5: Configurando Webhooks (Opcional)

Webhooks permitem sincronização bidirecional entre Kommo e sua aplicação.

### 5.1 Configurar URL do Webhook

1. Acesse sua integração privada em **Configurações** → **Integrações**
2. Na seção **Webhooks**, configure:
   - **URL do Webhook**: `https://SEU_DOMINIO.com/webhook/kommo/events`
   - **Eventos a monitorar**:
     - ✅ Lead atualizado (mudança de estágio)
     - ✅ Lead criado
     - ✅ Nota adicionada
     - ✅ Tarefa criada/completada
     - ✅ Contato atualizado

### 5.2 Segurança do Webhook

Configure um secret para validar requisições:
```env
KOMMO_WEBHOOK_SECRET=seu_webhook_secret_aqui
```

**Validação**: Kommo envia um header `X-Signature` que você deve validar.

## 🏷️ Parte 6: Configurando Tags

### 6.1 Criar Tags Padrão

No Kommo, crie as seguintes tags:
- `whatsapp-lead`
- `lead-quente`
- `lead-morno`
- `lead-frio`
- `qualificado-ia`
- `follow-up-automatico`
- `agendamento-pendente`
- `sem-resposta`
- `numero-invalido`

### 6.2 Obter IDs das Tags (Opcional)

```bash
curl -X GET https://SEU_SUBDOMINIO.kommo.com/api/v4/leads/tags \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

## 📋 Configuração do .env

### Configuração Mínima (Recomendada)

```env
# === KOMMO CRM - CONFIGURAÇÃO MÍNIMA ===

# OAuth2 (Obrigatório)
KOMMO_CLIENT_ID=seu_integration_id_aqui
KOMMO_CLIENT_SECRET=sua_secret_key_aqui
KOMMO_SUBDOMAIN=seusubdominio
KOMMO_REDIRECT_URI=https://seu-dominio.com/auth/kommo/callback

# Pipeline (Único ID necessário!)
KOMMO_PIPELINE_ID=1234567

# Pronto! O sistema detecta todo o resto automaticamente! 🎉
```

### Configuração Completa (Opcional)

Se você quiser sobrescrever a detecção automática:

```env
# === KOMMO CRM - CONFIGURAÇÃO COMPLETA ===

# OAuth2 Credentials
KOMMO_CLIENT_ID=seu_integration_id_aqui
KOMMO_CLIENT_SECRET=sua_secret_key_aqui
KOMMO_SUBDOMAIN=seusubdominio
KOMMO_REDIRECT_URI=https://seu-dominio.com/auth/kommo/callback

# Pipeline
KOMMO_PIPELINE_ID=1234567

# Stage IDs (opcional - detectados automaticamente)
KOMMO_STAGE_NEW=1001
KOMMO_STAGE_IN_QUALIFICATION=1002
KOMMO_STAGE_QUALIFIED=1003
KOMMO_STAGE_MEETING_SCHEDULED=1004
KOMMO_STAGE_IN_NEGOTIATION=1005
KOMMO_STAGE_WON=142  # ID do sistema
KOMMO_STAGE_LOST=143  # ID do sistema
KOMMO_STAGE_NOT_INTERESTED=1008

# Custom Field IDs (opcional - detectados automaticamente)
KOMMO_FIELD_WHATSAPP=2001
KOMMO_FIELD_ENERGY_BILL=2002
KOMMO_FIELD_QUALIFICATION_SCORE=2003
KOMMO_FIELD_SOLUTION=2004
KOMMO_FIELD_SOURCE=2005
KOMMO_FIELD_FIRST_MESSAGE=2006
KOMMO_FIELD_CONVERSATION_ID=2007

# Responsible Users (opcional)
KOMMO_USER_DEFAULT=4001
KOMMO_USER_HIGH_VALUE=4002
KOMMO_USER_SALES_MANAGER=4003

# Webhook (opcional)
KOMMO_WEBHOOK_SECRET=seu_webhook_secret

# Follow-up Configuration
KOMMO_FOLLOW_UP_DELAYS=30m,24h,72h,7d
KOMMO_MAX_FOLLOW_UPS=4
```

## 🚀 Próximos Passos

### 1. Autenticação OAuth2

1. **Iniciar o servidor**:
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Fazer login no Kommo**:
   ```
   http://localhost:8000/auth/kommo/login
   ```

3. **Verificar autenticação**:
   ```bash
   curl http://localhost:8000/auth/kommo/status
   ```

### 2. Verificar Configuração Automática

Acesse o endpoint de debug para ver tudo que foi detectado:
```
http://localhost:8000/auth/kommo/pipeline-config
```

Resposta esperada:
```json
{
  "authenticated": true,
  "message": "Configuração carregada com sucesso!",
  "pipeline_id": 1234567,
  "stages": {
    "new": 1001,
    "in_qualification": 1002,
    "qualified": 1003,
    ...
  },
  "custom_fields": {
    "whatsapp_number": 2001,
    "energy_bill_value": 2002,
    ...
  }
}
```

### 3. Testar Integração

```bash
# Criar lead de teste
curl -X POST http://localhost:8000/api/leads/test \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste Integração",
    "phone": "+5511999999999",
    "energy_bill_value": 500
  }'
```

### 4. Monitoramento

```bash
# Logs gerais
tail -f logs/app.log | grep -i kommo

# Logs de autenticação
tail -f logs/app.log | grep -i "kommo.*auth"

# Logs de detecção automática
tail -f logs/app.log | grep -i "mapeado"
```

## 🔍 Troubleshooting

### Problema: "Invalid client credentials"
- Verifique se copiou corretamente o **Integration ID** e **Secret Key**
- Confirme que está usando os valores da aba **"Chaves e Escopos"**
- A integração deve estar **ativa** no Kommo

### Problema: "Invalid redirect URI"
- O REDIRECT_URI deve ser **EXATAMENTE** igual ao configurado no Kommo
- Para desenvolvimento: inclua a porta `:8000`
- Para produção: use HTTPS
- Sem barra final (`/`) no fim da URL

### Problema: "Access denied"
- Verifique se marcou **"Permitir acesso: Todos"**
- O usuário deve ter **direitos de administrador**
- Tente fazer logout e login novamente

### Problema: "Custom field not found"
- Verifique se os campos foram criados com os **nomes exatos** sugeridos
- Use `/auth/kommo/pipeline-config` para ver campos detectados
- O sistema detecta por palavras-chave nos nomes

### Problema: "Stage not found"
- Verifique os nomes dos estágios no pipeline
- Use palavras-chave sugeridas (novo, qualificação, etc.)
- Configure manualmente no .env se necessário

### Problema: Token expirado
- **Access token** expira em **24 horas**
- **Refresh token** expira em **3 meses**
- O sistema renova automaticamente
- Se expirou completamente, faça login novamente

## 🔄 Sobre Tokens OAuth2

### Ciclo de Vida dos Tokens
- **Access Token**: Válido por 24 horas
- **Refresh Token**: Válido por 3 meses
- A cada renovação, um **novo refresh token** é gerado
- Se não usar por 3 meses, precisa autenticar novamente

### Tokens de Longa Duração
Para integrações privadas, você pode solicitar:
- Tokens válidos de 1 dia a 5 anos
- Não precisam de refresh token
- Ideal para automações

## 📞 Suporte

### Recursos Úteis
1. **Documentação Oficial**: https://developers.kommo.com
2. **Status da API**: https://status.kommo.com
3. **Comunidade**: https://community.kommo.com

### Logs para Debug
```bash
# Ver todos os logs do Kommo
grep -i kommo logs/app.log

# Ver mapeamentos automáticos
grep -i "mapeado\|detectado" logs/app.log

# Ver erros de API
grep -i "erro.*kommo" logs/app.log
```

## ✅ Checklist de Configuração

### Essencial (Mínimo)
- [ ] Conta Kommo com direitos de administrador
- [ ] Integração privada criada
- [ ] CLIENT_ID e CLIENT_SECRET no .env
- [ ] KOMMO_SUBDOMAIN configurado
- [ ] KOMMO_REDIRECT_URI configurado
- [ ] KOMMO_PIPELINE_ID configurado

### Pipeline e Campos
- [ ] Pipeline criado com estágios necessários
- [ ] Campos personalizados criados
- [ ] Nomes dos campos seguem padrão sugerido

### Validação
- [ ] Login OAuth2 funcionando
- [ ] `/auth/kommo/pipeline-config` mostra configuração
- [ ] Lead de teste criado com sucesso

### Opcional
- [ ] Webhooks configurados
- [ ] Tags padrão criadas
- [ ] Usuários responsáveis mapeados

**🎉 Parabéns! Com apenas 5 variáveis no .env, sua integração está pronta!**