# Guia de Suporte Multimodal - SDR IA SolarPrime

## Visão Geral

O agente SDR agora suporta análise multimodal de contas de luz usando o AGnO Framework com Gemini 2.5 Pro. Isso permite que o agente:

- 📸 Analise imagens de contas de luz automaticamente
- 📊 Extraia dados relevantes (valor, consumo, titular, etc.)
- 💬 Use essas informações na conversa de forma natural
- 📈 Acelere o processo de qualificação de leads

## Arquitetura da Implementação

### 1. Integração com AGnO Framework

O suporte multimodal foi implementado 100% usando as capacidades do AGnO Framework:

```python
# Imports tentam usar módulos AGnO quando disponíveis
try:
    from agno.media import Image, Audio, Document
    AGNO_MEDIA_AVAILABLE = True
except ImportError:
    AGNO_MEDIA_AVAILABLE = False
```

### 2. Processamento de Imagens

O método `_process_media` agora:
- Cria um prompt específico para análise de contas de luz
- Usa Gemini 2.5 Pro Vision para extrair dados
- Retorna informações estruturadas em JSON

### 3. Fluxo de Dados

1. **Recepção**: WhatsApp envia imagem via webhook
2. **Processamento**: `_process_media` analisa com Gemini Vision
3. **Extração**: Dados como valor, consumo, titular são extraídos
4. **Integração**: Informações são adicionadas ao `lead_info`
5. **Resposta**: Agente menciona os dados na conversa

## Formatos Suportados

### Imagens
- **URL**: Links diretos para imagens
- **Base64**: Dados codificados em base64
- **Arquivo Local**: Caminhos para arquivos no servidor

### Documentos
- **PDF**: Com suporte a OCR via PDFImageReader (quando disponível)
- **Fallback**: PDFs são tratados como imagens se módulos não estiverem disponíveis

## Dados Extraídos

O agente extrai automaticamente:

```json
{
    "bill_value": "R$ 450,00",
    "consumption_kwh": "350",
    "reference_period": "10/2024",
    "customer_name": "João Silva",
    "address": "Rua das Flores, 123",
    "document": "123.456.789-00",
    "distributor": "CELPE",
    "consumption_history": []
}
```

## Comportamento do Agente

Quando uma conta de luz é analisada:

1. **Confirmação Natural**: "Vi aqui que sua conta está vindo R$ 450,00..."
2. **Cálculo de Economia**: "Com energia solar, você economizaria cerca de R$ 427,50!"
3. **Personalização**: Usa o nome do titular se extraído
4. **Urgência**: Se conta > R$ 500, enfatiza a economia potencial

## Testando o Sistema

Use o script `test_agent.py` com opção 3:

```bash
python scripts/test_agent.py
# Escolha opção 3 - Simular envio de imagem
```

### Cenários de Teste

1. **URL de Imagem**: Simula envio via URL
2. **Base64**: Simula dados codificados
3. **Arquivo Local**: Simula upload direto
4. **PDF**: Simula documento PDF

## Configuração

### Requisitos
- AGnO Framework 1.7.6+
- Gemini 2.5 Pro API Key configurada
- Python 3.8+

### Variáveis de Ambiente
```bash
GEMINI_API_KEY=sua_chave_aqui
```

## Tratamento de Erros

O sistema possui fallbacks robustos:

1. **Imagem Inválida**: Retorna status de falha
2. **PDF sem OCR**: Trata como imagem
3. **Erro de Análise**: Usa resposta genérica
4. **Timeout**: Resposta de fallback

## Melhorias Futuras

- [ ] Suporte para múltiplas imagens
- [ ] Análise de histórico de consumo
- [ ] Transcrição de áudio
- [ ] Análise de outros documentos

## Debug e Logs

Ative modo debug para ver detalhes:

```python
config.debug = True
```

Logs importantes:
- "Processando imagem de conta de luz..."
- "Dados extraídos da conta: {...}"
- "Enviando imagem para análise com Gemini Vision..."

## Exemplo de Conversa

```
Lead: "Aqui está minha conta de luz" [envia imagem]
Agente: "Opa! Recebi sua conta aqui. Deixa eu dar uma olhada... 

Caramba! Vi que sua conta está vindo R$ 680,00! 😱

Com energia solar, você poderia economizar até R$ 646,00 por mês!

Esses dados estão corretos? É realmente esse valor que vem na sua conta?"
```

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs em modo debug
2. Confirme que a API Key do Gemini está configurada
3. Teste com diferentes formatos de imagem
4. Consulte a documentação do AGnO Framework