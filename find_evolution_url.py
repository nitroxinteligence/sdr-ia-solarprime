#!/usr/bin/env python3
"""
Script para encontrar a URL correta da Evolution API
"""
import asyncio
import httpx

async def find_evolution():
    """Tenta encontrar a Evolution API em várias URLs possíveis"""
    
    # URLs possíveis baseadas no padrão do EasyPanel
    urls = [
        # Baseadas na URL do .env
        "https://sdr-api-evolution-api.fzvgou.easypanel.host",
        "https://evolution-api.fzvgou.easypanel.host",
        "https://evolution.fzvgou.easypanel.host",
        
        # Variações sem HTTPS
        "http://sdr-api-evolution-api.fzvgou.easypanel.host",
        "http://evolution-api.fzvgou.easypanel.host",
        "http://evolution.fzvgou.easypanel.host",
        
        # Portas alternativas
        "https://sdr-api-evolution-api.fzvgou.easypanel.host:8080",
        "https://evolution-api.fzvgou.easypanel.host:8080",
        
        # Localhost (caso esteja rodando localmente)
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    
    print("🔍 Procurando Evolution API...\n")
    
    for url in urls:
        try:
            print(f"Testando: {url}")
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                # Tenta o endpoint raiz
                response = await client.get(f"{url}/")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if "Evolution" in str(data) or "evolution" in str(data) or "version" in data:
                            print(f"✅ ENCONTRADA! {url}")
                            print(f"   Resposta: {data}")
                            return url
                    except:
                        pass
                
                # Tenta endpoint específico da Evolution
                response2 = await client.get(f"{url}/manager")
                if response2.status_code in [200, 301, 302]:
                    print(f"✅ POSSÍVEL Evolution API em: {url}")
                    print(f"   Manager endpoint respondeu com status {response2.status_code}")
                    
        except httpx.ConnectError:
            print(f"   ❌ Conexão recusada")
        except httpx.TimeoutException:
            print(f"   ❌ Timeout")
        except Exception as e:
            print(f"   ❌ Erro: {type(e).__name__}: {str(e)[:50]}")
    
    print("\n❌ Evolution API não encontrada")
    print("\n📝 Sugestões:")
    print("1. Verifique no painel do EasyPanel a URL correta do serviço Evolution API")
    print("2. Certifique-se que o serviço está rodando")
    print("3. Se for local, execute: docker run -p 8080:8080 evolutionapi/evolution-api")
    
    return None

if __name__ == "__main__":
    url = asyncio.run(find_evolution())
    if url:
        print(f"\n✅ Use esta URL no .env:")
        print(f"EVOLUTION_API_URL={url}")