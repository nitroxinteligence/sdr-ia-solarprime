# 🚀 Guia Simplificado - Configuração Kommo CRM

## ✨ Nova Abordagem: Configuração Automática!

Agora o sistema detecta automaticamente os IDs dos estágios e campos personalizados! Você só precisa configurar o mínimo necessário.

## 📋 Configuração Mínima Necessária

### 1. Credenciais OAuth2 (Obrigatório)
```env
# Credenciais da integração privada
KOMMO_CLIENT_ID=0dd96bf8-4ab8-4d4e-b43e-68dab6270348
KOMMO_CLIENT_SECRET=Z8O7amBqdszgQ2ckCKlLpTaOmouSdegG8CWbyoucMtjJXa48cBo3TQ07qLlP6hWF
KOMMO_SUBDOMAIN=leonardofvieira00
KOMMO_REDIRECT_URI=https://sdr-api-evolution-api.fzvgou.easypanel.host/auth/kommo/callback

# Pipeline (único ID necessário!)
KOMMO_PIPELINE_ID=11672895
```

### 2. Só isso! 🎉

O sistema agora:
- ✅ Detecta automaticamente todos os estágios do pipeline
- ✅ Mapeia campos personalizados por nome
- ✅ Identifica valores de campos select
- ✅ Configura usuários responsáveis

## 🔍 Como Funciona

### Detecção Automática de Estágios

O sistema analisa os nomes dos estágios e mapeia automaticamente:

| Palavras-chave | Mapeado para |
|----------------|--------------|
| "novo", "inicial", "primeiro" | `new` |
| "qualifica", "análise" | `in_qualification` |
| "qualificado" | `qualified` |
| "reunião", "agendado" | `meeting_scheduled` |
| "negociação", "proposta" | `in_negotiation` |
| "ganho", "fechado" | `won` |
| "perdido", "cancelado" | `lost` |
| "não interessado" | `not_interested` |

### Detecção de Campos Personalizados

Campos são mapeados por palavras-chave no nome:

| Palavras-chave | Mapeado para |
|----------------|--------------|
| "whatsapp", "telefone" | Campo WhatsApp |
| "energia", "conta", "valor" | Valor da conta |
| "score", "qualificação" | Score de qualificação |
| "solução", "tipo" | Tipo de solução |

## 🛠️ Verificando a Configuração

### 1. Faça o login OAuth2
```
https://sdr-api-evolution-api.fzvgou.easypanel.host/auth/kommo/login
```

### 2. Verifique a configuração detectada
```
https://sdr-api-evolution-api.fzvgou.easypanel.host/auth/kommo/pipeline-config
```

Resposta esperada:
```json
{
  "authenticated": true,
  "message": "Configuração carregada com sucesso!",
  "pipeline_id": 11672895,
  "stages": {
    "new": 12345,
    "in_qualification": 12346,
    "qualified": 12347,
    ...
  },
  "custom_fields": {
    "whatsapp_number": 2001,
    "energy_bill_value": 2002,
    ...
  }
}
```

## 🎯 Sobrescrevendo Configurações (Opcional)

Se necessário, você ainda pode definir IDs específicos no .env:

```env
# Sobrescrever estágios específicos (opcional)
KOMMO_STAGE_NEW=12345
KOMMO_STAGE_QUALIFIED=12347

# Sobrescrever campos específicos (opcional)
KOMMO_FIELD_WHATSAPP=2001
```

## 📝 Exemplo de .env Completo (Produção)

```env
# === APLICAÇÃO ===
ENVIRONMENT=production
API_BASE_URL=https://sdr-api-evolution-api.fzvgou.easypanel.host

# === KOMMO CRM (Configuração Mínima) ===
KOMMO_CLIENT_ID=0dd96bf8-4ab8-4d4e-b43e-68dab6270348
KOMMO_CLIENT_SECRET=Z8O7amBqdszgQ2ckCKlLpTaOmouSdegG8CWbyoucMtjJXa48cBo3TQ07qLlP6hWF
KOMMO_SUBDOMAIN=leonardofvieira00
KOMMO_REDIRECT_URI=https://sdr-api-evolution-api.fzvgou.easypanel.host/auth/kommo/callback
KOMMO_PIPELINE_ID=11672895

# === OUTROS SERVIÇOS ===
EVOLUTION_API_URL=http://evolution-api:8080
REDIS_URL=redis://evolution-api-redis:6379/0
# ... resto das configurações
```

## ✅ Vantagens da Nova Abordagem

1. **Menos Configuração**: De 30+ variáveis para apenas 5!
2. **Mais Flexível**: Se mudar estágios no Kommo, funciona automaticamente
3. **Menos Erros**: Não precisa copiar dezenas de IDs manualmente
4. **Debug Fácil**: Use `/auth/kommo/pipeline-config` para ver o que foi detectado

## 🔧 Troubleshooting

### Problema: "Estágio não encontrado"
- O sistema mostrará no log qual estágio não foi mapeado
- Verifique o nome do estágio no Kommo
- Se necessário, adicione o ID manualmente no .env

### Problema: "Campo personalizado não encontrado"
- Verifique se o campo existe no Kommo
- O nome deve conter palavras-chave esperadas
- Use `/auth/kommo/pipeline-config` para ver campos detectados

## 🎉 Pronto!

Com apenas 5 variáveis de ambiente, sua integração Kommo está configurada e funcionando!