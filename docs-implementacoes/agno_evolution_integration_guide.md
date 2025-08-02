# Guia Completo: Integração AGnO Framework + Evolution API para Processamento de Mídia

## 🎯 Problema Real Identificado

Analisando o log do teste, o problema **NÃO** é com o AGnO Framework - ele está funcionando corretamente:

```
✅ Objeto Image criado com sucesso
📦 Usando conteúdo binário
```

O problema real é que:
1. O conteúdo binário não está sendo baixado corretamente da Evolution API
2. O teste está usando dados falsos (`fake_image_content_binary`)
3. A integração entre Evolution API → WhatsApp Service → AGnO Agent não está completa

## 🔍 Como o AGnO Framework Funciona

### Importação Correta
```python
from agno.media import Image, Audio
from agno.agent import Agent
```

### Criação de Objetos Image
O AGnO aceita imagens de 3 formas:

1. **Conteúdo Binário** (mais confiável):
```python
image_bytes = b"...dados binários da imagem..."
image = Image(content=image_bytes)
```

2. **URL** (não funciona com URLs do WhatsApp):
```python
image = Image(url="https://example.com/image.jpg")
```

3. **Base64** (através de conversão):
```python
import base64
image_bytes = base64.b64decode(base64_string)
image = Image(content=image_bytes)
```

## 🛠️ Solução Completa: Pipeline de Processamento

### 1. Download Correto da Mídia (Evolution API)
```python
async def download_media_complete(self, message_id: str, webhook_data: dict) -> Optional[bytes]:
    """Download completo com múltiplas estratégias"""
    
    # Extrair informações do webhook
    media_info = webhook_data.get("message", {}).get("imageMessage", {})
    
    # 1. Tentar baixar via Evolution API
    try:
        media_bytes = await self.download_media(message_id)
        if media_bytes and len(media_bytes) > 0:
            return media_bytes
    except Exception as e:
        logger.warning(f"Falha no download via API: {e}")
    
    # 2. Tentar download direto da URL se disponível
    if media_info.get("url"):
        try:
            # Precisa de autenticação do WhatsApp
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}"  # Se disponível
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(media_info["url"], headers=headers)
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            logger.warning(f"Falha no download direto: {e}")
    
    return None
```

### 2. Processamento no WhatsApp Service
```python
async def _process_media_with_validation(
    self, 
    message_id: str, 
    media_type: str,
    media_info: Dict[str, Any],
    webhook_data: Dict[str, Any]  # Dados completos do webhook
) -> Optional[Dict[str, Any]]:
    """Processa mídia com validação completa"""
    
    try:
        # Download com estratégias múltiplas
        media_data = await evolution_client.download_media_complete(
            message_id, 
            webhook_data
        )
        
        if not media_data:
            logger.error("Falha em todas as tentativas de download")
            return None
        
        # Validar conteúdo
        if len(media_data) < 100:  # Muito pequeno
            logger.error(f"Conteúdo suspeito: apenas {len(media_data)} bytes")
            return None
        
        # Verificar se é realmente uma imagem/documento
        import magic
        mime_type = magic.from_buffer(media_data, mime=True)
        logger.info(f"Tipo MIME detectado: {mime_type}")
        
        # Salvar e retornar dados completos
        return {
            "content": media_data,  # CRÍTICO: Conteúdo binário real
            "base64": base64.b64encode(media_data).decode(),
            "mimetype": mime_type,
            "size": len(media_data),
            "validated": True
        }
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        return None
```

### 3. Criação Correta do Objeto AGnO Image
```python
def _create_agno_image_validated(self, image_data: Any) -> Optional[Image]:
    """Cria objeto Image com validação completa"""
    
    if isinstance(image_data, dict):
        # Verificar se temos conteúdo real
        if 'content' in image_data and image_data['content']:
            content = image_data['content']
            
            # Validar que é conteúdo binário real
            if isinstance(content, bytes) and len(content) > 100:
                logger.info(f"✅ Conteúdo binário válido: {len(content)} bytes")
                
                # Validar tipo de imagem
                try:
                    from PIL import Image as PILImage
                    import io
                    
                    # Tentar abrir como imagem
                    img = PILImage.open(io.BytesIO(content))
                    logger.info(f"✅ Imagem válida: {img.format} {img.size}")
                    
                    # Criar objeto AGnO Image
                    return Image(content=content)
                    
                except Exception as e:
                    logger.error(f"Conteúdo não é uma imagem válida: {e}")
                    return None
            else:
                logger.error("Conteúdo binário inválido ou muito pequeno")
                return None
    
    return None
```

### 4. Integração Completa no Agent
```python
async def process_image_with_agno(self, media_data: dict) -> dict:
    """Processa imagem usando AGnO Framework"""
    
    # Criar objeto Image validado
    image_obj = self._create_agno_image_validated(media_data)
    
    if not image_obj:
        return {"error": "Não foi possível criar objeto Image válido"}
    
    # Processar com o agente
    try:
        # Usar o agente AGnO para análise
        response = await self.agno_agent.process(
            message="Analise esta imagem",
            images=[image_obj]
        )
        
        return {
            "success": True,
            "analysis": response
        }
        
    except Exception as e:
        logger.error(f"Erro no processamento AGnO: {e}")
        return {"error": str(e)}
```

## 📋 Checklist de Implementação

### 1. Verificações Essenciais
- [ ] Evolution API está retornando conteúdo real (não vazio)
- [ ] WhatsApp Service está passando `webhook_data` completo
- [ ] Conteúdo binário está sendo incluído no retorno
- [ ] Validação de tipo MIME está funcionando
- [ ] AGnO Image está sendo criado com `content=bytes`

### 2. Logs para Debug
```python
# No Evolution API
logger.info(f"Download iniciado para {message_id}")
logger.info(f"Resposta da API: {response.status_code}")
logger.info(f"Conteúdo baixado: {len(content)} bytes")

# No WhatsApp Service
logger.info(f"Processando mídia: {media_type}")
logger.info(f"Dados disponíveis: {list(media_data.keys())}")
logger.info(f"Tamanho do conteúdo: {len(media_data.get('content', b''))} bytes")

# No AGnO Agent
logger.info(f"Criando Image AGnO com {len(content)} bytes")
logger.info(f"Objeto criado: {type(image_obj)}")
```

## 🧪 Teste Real Funcional

```python
async def test_real_media_processing():
    """Teste com mídia real do WhatsApp"""
    
    # 1. Simular webhook real do WhatsApp
    webhook_data = {
        "event": "messages.upsert",
        "data": {
            "key": {"id": "REAL_MESSAGE_ID"},
            "message": {
                "imageMessage": {
                    "url": "https://mmg.whatsapp.net/...",
                    "mimetype": "image/jpeg",
                    "fileLength": "123456",
                    "mediaKey": "...",
                    "fileEncSha256": "...",
                    "directPath": "/v/t62.7119-24/..."
                }
            }
        }
    }
    
    # 2. Processar com o sistema real
    result = await whatsapp_service.process_webhook(webhook_data)
    
    # 3. Verificar resultados
    assert result['status'] == 'success'
    assert 'analysis' in result
    print(f"Análise: {result['analysis']}")
```

## 🚨 Problemas Comuns e Soluções

### 1. "cannot identify image file"
**Causa**: Dados não são uma imagem válida
**Solução**: Verificar se o download está completo e o conteúdo é real

### 2. "Unable to process input image"
**Causa**: URL sendo usada ao invés de conteúdo binário
**Solução**: Sempre usar `Image(content=bytes)`

### 3. "Conteúdo vazio"
**Causa**: Evolution API não está baixando corretamente
**Solução**: Implementar múltiplas estratégias de download

## 🎯 Resultado Final Esperado

Quando tudo estiver funcionando:

```
📥 Nova mensagem com imagem recebida
🔄 Baixando mídia via Evolution API...
✅ Mídia baixada: 245632 bytes
🔍 Tipo MIME: image/jpeg
✅ Imagem válida: JPEG (1080, 1920)
🏗️ Criando objeto Image AGnO...
✅ Objeto Image criado com sucesso
🤖 Processando com AGnO Agent...
✅ Análise concluída: "Conta de luz identificada..."
```

## 📚 Referências

- [AGnO Documentation](https://docs.agno.com)
- [Evolution API v2 Docs](https://doc.evolution-api.com/v2)
- [WhatsApp Media Handling](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media/)
- [AGnO GitHub Examples](https://github.com/agno-agi/agno/tree/main/cookbook)