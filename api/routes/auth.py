"""
Auth Routes
===========
Rotas de autenticação OAuth2 para Kommo CRM
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import Optional
from loguru import logger
from config.config import get_config
# Usar versão corrigida sem dependência de Redis síncrono
try:
    from services.kommo_auth_fixed import KommoAuthFixed as KommoAuth
except ImportError:
    from services.kommo_auth import KommoAuth
from services.kommo_service import kommo_service


router = APIRouter(prefix="/auth", tags=["authentication"])


def get_kommo_auth() -> KommoAuth:
    """Dependency para obter instância do KommoAuth"""
    config = get_config()
    return KommoAuth(config)


@router.get("/kommo/login")
async def kommo_login(
    redirect_after: Optional[str] = Query(None, description="URL para redirecionar após login"),
    kommo_auth: KommoAuth = Depends(get_kommo_auth)
):
    """
    Inicia fluxo OAuth2 do Kommo
    
    Returns:
        Redireciona para página de autorização do Kommo
    """
    try:
        # Gera URL de autorização
        auth_url = kommo_auth.get_auth_url()
        
        # Salva URL de redirecionamento se fornecida
        if redirect_after:
            # TODO: Implementar salvamento seguro do redirect_after
            pass
        
        logger.info("Redirecionando para autorização Kommo")
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar login Kommo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar autenticação")


@router.get("/kommo/callback")
async def kommo_callback(
    code: str = Query(..., description="Código de autorização"),
    state: str = Query(..., description="Estado da requisição"),
    kommo_auth: KommoAuth = Depends(get_kommo_auth)
):
    """
    Callback OAuth2 do Kommo
    
    Recebe código de autorização e troca por tokens
    """
    try:
        # Verifica state para prevenir CSRF
        if not kommo_auth.verify_state(state):
            raise HTTPException(status_code=400, detail="Estado inválido")
        
        # Troca código por tokens
        tokens = await kommo_auth.exchange_code_for_token(code)
        
        # Obtém informações da conta
        account_info = await kommo_auth.get_account_info()
        
        # Página de sucesso
        success_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Autenticação Kommo - Sucesso</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .success {{
                    color: #4CAF50;
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 10px;
                }}
                p {{
                    color: #666;
                    margin-bottom: 20px;
                }}
                .account-info {{
                    background: #f9f9f9;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 20px;
                    text-align: left;
                }}
                .close-btn {{
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-top: 20px;
                }}
                .close-btn:hover {{
                    background: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✓</div>
                <h1>Autenticação Realizada!</h1>
                <p>Conexão com Kommo CRM estabelecida com sucesso.</p>
                {f'''
                <div class="account-info">
                    <strong>Conta:</strong> {account_info.get('name', 'N/A')}<br>
                    <strong>Subdomínio:</strong> {account_info.get('subdomain', 'N/A')}<br>
                    <strong>Token válido por:</strong> {tokens.get('expires_in', 0) // 3600} horas
                </div>
                ''' if account_info else ''}
                <button class="close-btn" onclick="window.close()">Fechar</button>
            </div>
            <script>
                // Notifica janela pai se foi aberta como popup
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'kommo_auth_success',
                        expires_in: {tokens.get('expires_in', 0)}
                    }}, '*');
                }}
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=success_html)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no callback OAuth: {str(e)}")
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro na Autenticação</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .error {{
                    color: #f44336;
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 10px;
                }}
                p {{
                    color: #666;
                    margin-bottom: 20px;
                }}
                .error-details {{
                    background: #fff3cd;
                    color: #856404;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">✗</div>
                <h1>Erro na Autenticação</h1>
                <p>Não foi possível completar a autenticação com Kommo.</p>
                <div class="error-details">
                    {str(e)}
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=error_html, status_code=400)


@router.get("/kommo/status")
async def kommo_auth_status(
    kommo_auth: KommoAuth = Depends(get_kommo_auth)
):
    """
    Verifica status da autenticação Kommo
    
    Returns:
        Status da autenticação e informações da conta
    """
    try:
        # Verifica se está autenticado
        is_authenticated = await kommo_auth.is_authenticated()
        
        if is_authenticated:
            # Obtém informações da conta
            account_info = await kommo_auth.get_account_info()
            
            return {
                "authenticated": True,
                "message": "Autenticado com sucesso",
                "account": {
                    "id": account_info.get("id") if account_info else None,
                    "name": account_info.get("name") if account_info else None,
                    "subdomain": account_info.get("subdomain") if account_info else None,
                    "currency": account_info.get("currency") if account_info else None
                }
            }
        else:
            return {
                "authenticated": False,
                "message": "Não autenticado. Use /auth/kommo/login para autenticar.",
                "account": None
            }
            
    except Exception as e:
        logger.error(f"Erro ao verificar status de autenticação: {str(e)}")
        return {
            "authenticated": False,
            "message": f"Erro ao verificar autenticação: {str(e)}",
            "account": None
        }


@router.post("/kommo/refresh")
async def kommo_refresh_token(
    kommo_auth: KommoAuth = Depends(get_kommo_auth)
):
    """
    Força renovação do access token
    
    Returns:
        Novo token e tempo de expiração
    """
    try:
        tokens = await kommo_auth.refresh_access_token()
        
        return {
            "success": True,
            "message": "Token renovado com sucesso",
            "expires_in": tokens.get("expires_in", 0)
        }
        
    except Exception as e:
        logger.error(f"Erro ao renovar token: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Erro ao renovar token: {str(e)}"
        )


@router.get("/kommo/pipeline-config")
async def get_kommo_pipeline_config():
    """
    Obtém a configuração do pipeline do Kommo (estágios e campos)
    
    Esta rota é útil para verificar se a configuração automática está funcionando.
    Mostra todos os estágios e campos detectados automaticamente.
    
    Returns:
        Configuração completa do pipeline, estágios e campos personalizados
    """
    try:
        if not kommo_service:
            raise HTTPException(
                status_code=503,
                detail="Serviço Kommo não inicializado. Verifique as credenciais."
            )
        
        # Verificar autenticação primeiro
        is_authenticated = await kommo_service.auth.is_authenticated()
        if not is_authenticated:
            return {
                "error": "Não autenticado",
                "message": "Use /auth/kommo/login primeiro para autenticar",
                "authenticated": False
            }
        
        # Obter configuração
        config = await kommo_service.get_pipeline_configuration()
        
        # Adicionar informações úteis
        config["authenticated"] = True
        config["message"] = "Configuração carregada com sucesso!"
        config["instructions"] = {
            "env_minimal": "Você só precisa configurar KOMMO_PIPELINE_ID no .env",
            "example": "KOMMO_PIPELINE_ID=11672895",
            "note": "Os IDs dos estágios e campos são detectados automaticamente!"
        }
        
        return config
        
    except Exception as e:
        logger.error(f"Erro ao obter configuração do pipeline: {str(e)}")
        return {
            "error": str(e),
            "authenticated": False,
            "message": "Erro ao carregar configuração. Verifique os logs."
        }


@router.post("/kommo/logout")
async def kommo_logout(
    kommo_auth: KommoAuth = Depends(get_kommo_auth)
):
    """
    Remove tokens e faz logout do Kommo
    
    Returns:
        Confirmação de logout
    """
    try:
        await kommo_auth._clear_tokens()
        
        return {
            "success": True,
            "message": "Logout realizado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer logout: {str(e)}"
        )