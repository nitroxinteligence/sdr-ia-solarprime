"""
Google OAuth 2.0 API Endpoints
Gerencia fluxo de autorização OAuth para Google Calendar
"""

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import Optional
import logging

from app.integrations.google_oauth_handler import get_oauth_handler
from app.utils.logger import emoji_logger

# Configurar logger
logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(
    prefix="/google",
    tags=["Google OAuth"]
)


@router.get("/auth")
async def google_auth():
    """
    Inicia fluxo de autorização OAuth 2.0
    Redireciona o usuário para a tela de consentimento do Google
    
    Este endpoint deve ser acessado manualmente pelo administrador
    uma única vez para autorizar a aplicação.
    """
    try:
        emoji_logger.service_call("GET /google/auth - Iniciando fluxo OAuth")
        
        # Log detalhado para debug
        logger.info("🔍 Verificando configuração OAuth...")
        logger.info(f"   Client ID configurado: {'Sim' if get_oauth_handler().client_id else 'Não'}")
        logger.info(f"   Client Secret configurado: {'Sim' if get_oauth_handler().client_secret else 'Não'}")
        logger.info(f"   Redirect URI: {get_oauth_handler().redirect_uri}")
        
        # Obter handler OAuth
        oauth_handler = get_oauth_handler()
        
        # Verificar configuração
        if not oauth_handler.client_id or not oauth_handler.client_secret:
            error_msg = "OAuth não configurado. Verifique GOOGLE_OAUTH_CLIENT_ID e GOOGLE_OAUTH_CLIENT_SECRET no .env"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Gerar URL de autorização
        auth_url = oauth_handler.get_google_auth_url()
        
        if not auth_url:
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar URL de autorização. Verifique as configurações OAuth."
            )
        
        emoji_logger.system_success(f"Redirecionando para Google OAuth: {auth_url[:50]}...")
        
        # Redirecionar para Google
        return RedirectResponse(url=auth_url)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"❌ Erro detalhado no endpoint /google/auth:\n{error_trace}")
        emoji_logger.service_error(f"Erro no endpoint /google/auth: {e}")
        
        # Retornar erro mais detalhado
        return {
            "error": "Internal Server Error",
            "message": str(e),
            "details": "Verifique os logs para mais informações",
            "configuration": {
                "client_id_configured": bool(get_oauth_handler().client_id),
                "client_secret_configured": bool(get_oauth_handler().client_secret),
                "redirect_uri": get_oauth_handler().redirect_uri
            }
        }


@router.get("/callback")
async def google_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """
    Callback do Google OAuth 2.0
    Recebe o código de autorização e troca por tokens
    
    Este endpoint é chamado automaticamente pelo Google
    após o usuário autorizar a aplicação.
    """
    try:
        emoji_logger.service_call(f"GET /google/callback - Code: {code[:20] if code else 'None'}...")
        
        # Verificar se houve erro
        if error:
            emoji_logger.service_error(f"Erro no callback OAuth: {error}")
            return HTMLResponse(
                content=f"""
                <html>
                <head>
                    <title>Erro na Autorização</title>
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
                            padding: 40px;
                            background: white;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                            max-width: 500px;
                        }}
                        h1 {{ color: #d32f2f; }}
                        p {{ color: #666; margin: 20px 0; }}
                        .error {{ 
                            background: #ffebee; 
                            padding: 15px; 
                            border-radius: 5px;
                            color: #c62828;
                            margin: 20px 0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>❌ Erro na Autorização</h1>
                        <div class="error">{error}</div>
                        <p>A autorização foi cancelada ou ocorreu um erro.</p>
                        <p>Por favor, tente novamente ou contate o suporte.</p>
                    </div>
                </body>
                </html>
                """,
                status_code=400
            )
        
        # Verificar se temos código
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Código de autorização não fornecido"
            )
        
        # Obter handler OAuth
        oauth_handler = get_oauth_handler()
        
        # Processar callback e obter tokens
        result = await oauth_handler.handle_google_callback(code)
        
        if result.get("success"):
            emoji_logger.system_success("✅ Autorização OAuth concluída com sucesso!")
            
            # Testar conexão
            test_result = await oauth_handler.test_connection()
            
            # HTML de sucesso
            return HTMLResponse(
                content=f"""
                <html>
                <head>
                    <title>Autorização Concluída</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .container {{
                            text-align: center;
                            padding: 40px;
                            background: white;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            max-width: 600px;
                            margin: 20px;
                        }}
                        h1 {{ 
                            color: #4caf50; 
                            font-size: 2.5em;
                            margin-bottom: 20px;
                        }}
                        .success-icon {{
                            font-size: 4em;
                            margin-bottom: 20px;
                        }}
                        p {{ 
                            color: #666; 
                            margin: 15px 0;
                            line-height: 1.6;
                        }}
                        .info {{
                            background: #e8f5e9;
                            padding: 20px;
                            border-radius: 5px;
                            margin: 20px 0;
                            text-align: left;
                        }}
                        .info h3 {{
                            color: #2e7d32;
                            margin-top: 0;
                        }}
                        .info ul {{
                            margin: 10px 0;
                            padding-left: 20px;
                        }}
                        .info li {{
                            margin: 5px 0;
                            color: #555;
                        }}
                        .features {{
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                            gap: 20px;
                            margin: 30px 0;
                        }}
                        .feature {{
                            padding: 15px;
                            background: #f5f5f5;
                            border-radius: 5px;
                        }}
                        .feature-icon {{
                            font-size: 2em;
                            margin-bottom: 10px;
                        }}
                        .feature-title {{
                            font-weight: bold;
                            color: #333;
                            margin-bottom: 5px;
                        }}
                        .warning {{
                            background: #fff3e0;
                            padding: 15px;
                            border-radius: 5px;
                            border-left: 4px solid #ff9800;
                            margin: 20px 0;
                            text-align: left;
                        }}
                        .button {{
                            display: inline-block;
                            padding: 12px 30px;
                            background: #4caf50;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            margin-top: 20px;
                            transition: background 0.3s;
                        }}
                        .button:hover {{
                            background: #45a049;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success-icon">✅</div>
                        <h1>Autorização Concluída!</h1>
                        
                        <div class="info">
                            <h3>📧 Conta Conectada</h3>
                            <ul>
                                <li><strong>Email:</strong> {test_result.get('user_email', 'Não disponível')}</li>
                                <li><strong>Calendário ID:</strong> {test_result.get('calendar_id', 'primary')}</li>
                                <li><strong>Calendários disponíveis:</strong> {test_result.get('calendars', 0)}</li>
                            </ul>
                        </div>
                        
                        <div class="features">
                            <div class="feature">
                                <div class="feature-icon">📹</div>
                                <div class="feature-title">Google Meet</div>
                                <div>Criação automática ativada</div>
                            </div>
                            <div class="feature">
                                <div class="feature-icon">👥</div>
                                <div class="feature-title">Participantes</div>
                                <div>Convites automáticos ativados</div>
                            </div>
                            <div class="feature">
                                <div class="feature-icon">📅</div>
                                <div class="feature-title">Calendário</div>
                                <div>Acesso completo concedido</div>
                            </div>
                        </div>
                        
                        <p><strong>O sistema SDR IA SolarPrime agora pode:</strong></p>
                        <ul style="text-align: left; display: inline-block;">
                            <li>✅ Criar eventos no Google Calendar</li>
                            <li>✅ Gerar links do Google Meet automaticamente</li>
                            <li>✅ Convidar participantes para reuniões</li>
                            <li>✅ Enviar lembretes automáticos</li>
                            <li>✅ Gerenciar agendamentos completos</li>
                        </ul>
                        
                        <div class="warning">
                            <strong>⚠️ Importante:</strong> O refresh token foi salvo automaticamente no arquivo .env. 
                            Em produção, considere usar um gerenciador de segredos como HashiCorp Vault ou AWS Secrets Manager.
                        </div>
                        
                        <p style="margin-top: 30px;">
                            <strong>🎉 Tudo pronto!</strong><br>
                            O sistema já está usando OAuth 2.0 para todas as operações de calendário.
                        </p>
                        
                        <a href="/" class="button">Voltar ao Sistema</a>
                    </div>
                </body>
                </html>
                """
            )
        else:
            # Erro ao processar callback
            emoji_logger.service_error(f"Erro ao processar callback: {result.get('message')}")
            
            return HTMLResponse(
                content=f"""
                <html>
                <head>
                    <title>Erro na Autorização</title>
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
                            padding: 40px;
                            background: white;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                            max-width: 600px;
                        }}
                        h1 {{ color: #f44336; }}
                        .error {{
                            background: #ffebee;
                            padding: 20px;
                            border-radius: 5px;
                            margin: 20px 0;
                            text-align: left;
                        }}
                        .suggestion {{
                            background: #e3f2fd;
                            padding: 15px;
                            border-radius: 5px;
                            margin: 20px 0;
                            text-align: left;
                        }}
                        a {{
                            color: #2196f3;
                            text-decoration: none;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>❌ Erro ao Processar Autorização</h1>
                        <div class="error">
                            <strong>Erro:</strong> {result.get('message', 'Erro desconhecido')}
                        </div>
                        <div class="suggestion">
                            <strong>💡 Sugestões:</strong>
                            <ul>
                                <li>Revogue o acesso em <a href="https://myaccount.google.com/permissions" target="_blank">Google Permissions</a></li>
                                <li>Tente autorizar novamente em <a href="/google/auth">/google/auth</a></li>
                                <li>Verifique as configurações OAuth no Google Cloud Console</li>
                            </ul>
                        </div>
                    </div>
                </body>
                </html>
                """,
                status_code=500
            )
            
    except Exception as e:
        emoji_logger.service_error(f"Erro no callback OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def google_oauth_status():
    """
    Verifica status da conexão OAuth com Google Calendar
    """
    try:
        oauth_handler = get_oauth_handler()
        
        # Testar conexão
        result = await oauth_handler.test_connection()
        
        if result.get("success"):
            emoji_logger.system_success(f"OAuth conectado: {result.get('user_email')}")
        else:
            emoji_logger.service_warning("OAuth não configurado ou expirado")
        
        return {
            "oauth_configured": result.get("success", False),
            "user_email": result.get("user_email"),
            "calendar_id": result.get("calendar_id"),
            "can_create_meets": result.get("can_create_meets", False),
            "can_invite_attendees": result.get("can_invite_attendees", False),
            "message": result.get("message"),
            "auth_url": "/google/auth" if not result.get("success") else None
        }
        
    except Exception as e:
        emoji_logger.service_error(f"Erro ao verificar status OAuth: {e}")
        return {
            "oauth_configured": False,
            "message": str(e),
            "auth_url": "/google/auth"
        }