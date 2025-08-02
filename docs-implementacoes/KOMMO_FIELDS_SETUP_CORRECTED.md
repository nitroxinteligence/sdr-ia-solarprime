# 📝 Como Criar Campos Personalizados no Kommo CRM (Versão Corrigida)

## ⚠️ Importante: Você precisa ter permissões de Administrador

## 📍 Onde Criar os Campos

### Método 1: Através de um Lead (Mais Fácil)

1. **Acesse a seção de Leads**:
   - Entre no Kommo: `https://leonardofvieira00.kommo.com`
   - Vá para a seção **Leads**

2. **Abra qualquer Lead**:
   - Clique em qualquer lead existente
   - Ou crie um novo clicando em **"Quick add"** ou **"Criar novo lead"**

3. **Acesse a aba Setup**:
   - Com o lead aberto, clique na aba **"Setup"** no lado esquerdo da tela
   - Um template para criar campos será aberto

4. **Adicione os campos**:
   - Escolha onde criar o campo: Lead, Contato ou Empresa
   - Role até a seção desejada
   - Clique no botão **"+ Add field"** (ou "+ Adicionar campo")

### Método 2: Durante a Importação de Dados

Se você estiver importando dados e não tiver um campo correspondente:
- Role para cima até a opção **"New custom field"**
- Nomeie o campo
- Escolha o tipo
- Selecione a seção (Lead, Contato ou Empresa)

## 🔧 Campos Necessários para o SDR IA

### 1. WhatsApp
- **Tipo**: Text (Texto)
- **Nome**: `WhatsApp`
- **Seção**: Lead

### 2. Valor da Conta de Energia
- **Tipo**: Numeric (Numérico)
- **Nome**: `Valor Conta Energia`
- **Seção**: Lead

### 3. Score de Qualificação
- **Tipo**: Numeric (Numérico)
- **Nome**: `Score Qualificação`
- **Seção**: Lead

### 4. Solução Solar
- **Tipo**: Select (Seleção)
- **Nome**: `Solução Solar`
- **Opções**:
  - Usina Própria
  - Fazenda Solar
  - Consórcio
  - Consultoria
  - Não Definido
- **Seção**: Lead

### 5. Fonte do Lead
- **Tipo**: Select (Seleção)
- **Nome**: `Fonte`
- **Opções**:
  - WhatsApp SDR
  - WhatsApp Manual
  - Site
  - Indicação
- **Seção**: Lead

### 6. Primeira Mensagem
- **Tipo**: Text area (Área de texto)
- **Nome**: `Primeira Mensagem`
- **Seção**: Lead

### 7. ID da Conversa
- **Tipo**: Text (Texto)
- **Nome**: `ID Conversa`
- **Seção**: Lead

## 📋 Tipos de Campos Disponíveis

- **Text**: Aceita letras e números (texto curto)
- **Text area**: Texto longo com quebra de linha
- **Numeric**: Apenas números (sem negativos)
- **Select**: Lista com uma opção selecionável
- **Multiselect**: Lista com múltiplas opções
- **Date**: Campo de data com calendário
- **URL**: Links clicáveis
- **Checkbox**: Caixa de seleção sim/não
- **Birthday**: Data especial com lembretes automáticos

## ⚠️ Avisos Importantes

1. **Tipo do campo é permanente**: Uma vez criado, você não pode mudar o tipo. Precisa deletar e recriar.

2. **Deletar campo = Deletar dados**: Ao deletar um campo, TODOS os dados associados em TODOS os leads são perdidos.

3. **Sistema detecta automaticamente**: Com nossa implementação, o sistema detecta os campos por nome, então use os nomes exatos sugeridos.

## 🎯 Alternativa: Deixe o Sistema Detectar!

Como implementamos detecção automática, você pode:

1. Criar os campos com nomes similares
2. O sistema tentará mapear automaticamente
3. Use `/auth/kommo/pipeline-config` para verificar o mapeamento

Por exemplo, se você criar um campo chamado "Telefone WhatsApp", o sistema detectará como campo de WhatsApp automaticamente!

## 📸 Passo Visual Simplificado

1. Abra um Lead → 2. Clique em "Setup" → 3. Clique em "+ Add field" → 4. Configure o campo → 5. Salve

É mais simples do que parece! O Kommo esconde essa funcionalidade dentro da visualização de leads para manter a interface limpa.