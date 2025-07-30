# Correção do Processamento de PDF - SDR IA SolarPrime

## 🔍 Problema Identificado

O processamento de PDF está falhando com a mensagem "Conteúdo do PDF vazio". Analisando os logs:

```
2025-07-30 06:11:16.829 | INFO     | agents.sdr_agent:_process_pdf_with_ocr:1498 - 📄 Processamento de PDF iniciado
2025-07-30 06:11:16.829 | ERROR    | agents.sdr_agent:_process_pdf_with_ocr:1524 - ❌ Não foi possível obter conteúdo do PDF
```

## 🎯 Causa Raiz

O problema ocorre porque:
1. O WhatsApp service salva o PDF em um arquivo temporário e passa o `path`
2. O `_process_pdf_with_ocr` tenta ler o arquivo mas ele pode não existir mais ou estar vazio
3. O fluxo de dados entre o download da mídia e o processamento não está funcionando corretamente

## ✅ Correções Aplicadas

### 1. Logging Aprimorado
Adicionei logs mais detalhados para diagnosticar o problema:
```python
logger.debug(f"🔍 Dados recebidos para processamento: {list(pdf_data.keys())}")
```

### 2. Verificação de Arquivo
Adicionei verificação se o arquivo realmente existe:
```python
if os.path.exists(pdf_data['path']):
    with open(pdf_data['path'], 'rb') as f:
        pdf_content = f.read()
    logger.info(f"✅ PDF lido com sucesso: {len(pdf_content)} bytes")
else:
    logger.error(f"❌ Arquivo PDF não encontrado: {pdf_data['path']}")
```

## 🔧 Solução Completa

### Opção 1: Passar o conteúdo diretamente (Recomendada)

Modificar o `_process_media` no `whatsapp_service.py` para incluir o conteúdo:

```python
# Em whatsapp_service.py, linha 521
return {
    "path": filepath,
    "base64": base64.b64encode(media_data).decode(),  # Sempre incluir base64
    "mimetype": media_info.get("mimetype", ""),
    "filename": media_info.get("filename", filename),
    "content": media_data  # Adicionar conteúdo binário
}
```

### Opção 2: Usar base64 para todos os tipos

Modificar para sempre incluir base64, não apenas para imagens:

```python
# Em whatsapp_service.py, linha 523
"base64": base64.b64encode(media_data).decode(),  # Remover condição if media_type == "image"
```

### Opção 3: Garantir que o arquivo temporário persista

Usar `delete=False` ao criar arquivos temporários e limpar depois:

```python
import tempfile

# Criar arquivo temporário que não será deletado automaticamente
with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp_file:
    tmp_file.write(media_data)
    filepath = tmp_file.name
```

## 📋 Passos para Implementar

1. **Aplicar a correção no whatsapp_service.py:**
```bash
# Editar o arquivo para incluir o conteúdo binário no retorno
```

2. **Reiniciar o servidor:**
```bash
# Reiniciar para aplicar as mudanças
```

3. **Testar com o script de diagnóstico:**
```bash
python test_pdf_processing.py
```

4. **Monitorar os logs:**
```bash
tail -f logs/app.log | grep -E "PDF|pdf|document"
```

## 🧪 Teste Manual

1. Envie um PDF de conta de luz via WhatsApp
2. Observe os logs para ver:
   - Se o arquivo é salvo corretamente
   - O tamanho do arquivo em bytes
   - Se o path existe quando o agente tenta processar

## 💡 Melhorias Adicionais

### 1. Instalar dependências para conversão PDF
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Python
pip install pdf2image
```

### 2. Implementar retry com backoff
Se o arquivo não for encontrado, aguardar e tentar novamente.

### 3. Usar processamento assíncrono
Processar o PDF em uma task separada para não bloquear a resposta.

## 🚨 Logs de Debug

Para debug completo, adicione estas linhas:

```python
# No início do _process_pdf_with_ocr
logger.debug(f"PDF data keys: {list(pdf_data.keys())}")
logger.debug(f"PDF data values: {pdf_data}")

# Após ler o arquivo
logger.debug(f"PDF content size: {len(pdf_content) if pdf_content else 0}")
logger.debug(f"PDF first 100 bytes: {pdf_content[:100] if pdf_content else 'Empty'}")
```

## 📊 Resultado Esperado

Após aplicar as correções:
1. ✅ O PDF será lido corretamente
2. ✅ O conteúdo será extraído com sucesso
3. ✅ A análise da conta de luz funcionará
4. ✅ O usuário receberá a resposta com os valores identificados