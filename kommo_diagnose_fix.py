
import os
import requests
from dotenv import load_dotenv
from loguru import logger

def diagnose_kommo_auth():
    """
    Script de diagnóstico para testar a autenticação com a API do Kommo
    usando o Long-Lived Token.
    """
    # Carregar variáveis de ambiente do arquivo .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        logger.error(f"Arquivo .env não encontrado em: {env_path}")
        logger.error("Certifique-se de que o script está na raiz do projeto.")
        return

    load_dotenv(dotenv_path=env_path)

    # Obter credenciais do ambiente
    base_url = os.getenv("KOMMO_BASE_URL")
    token = os.getenv("KOMMO_LONG_LIVED_TOKEN")
    subdomain = os.getenv("KOMMO_SUBDOMAIN")

    # --- Validação das Variáveis ---
    if not all([base_url, token, subdomain]):
        logger.error("Uma ou mais variáveis de ambiente do Kommo não foram encontradas.")
        logger.error(f"Verifique se KOMMO_BASE_URL, KOMMO_LONG_LIVED_TOKEN e KOMMO_SUBDOMAIN existem no seu arquivo .env")
        return

    logger.info("Credenciais carregadas com sucesso do arquivo .env")
    logger.info(f"Subdomínio: {subdomain}")
    logger.info(f"URL Base: {base_url}")
    logger.info(f"Token (primeiros 15 chars): {token[:15]}...")

    # --- Construção da Requisição ---
    # Usando um endpoint simples que requer autenticação
    # A documentação do Kommo sugere que a URL base já é o endpoint da API
    # Vamos tentar o endpoint /api/v4/account que é um bom teste de autenticação
    
    # Corrigindo a URL para garantir que não haja barras duplas
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    # O endpoint da conta é /api/v4/account, mas a URL base já pode ser a API
    # Vamos construir a URL completa para ter certeza
    # A URL completa deve ser https://{subdominio}.kommo.com
    
    request_url = f"https://{subdomain}.kommo.com/api/v4/account"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    logger.info(f"Enviando requisição GET para: {request_url}")

    # --- Execução da Requisição ---
    try:
        response = requests.get(request_url, headers=headers, timeout=15)

        # --- Análise da Resposta ---
        logger.info(f"Status da Resposta: {response.status_code}")
        
        if response.status_code == 200:
            logger.success("✅ SUCESSO! A autenticação com o Kommo CRM foi bem-sucedida.")
            logger.info("O seu Long-Lived Token é válido.")
            logger.info("Resposta da API:")
            try:
                print(response.json())
            except requests.exceptions.JSONDecodeError:
                print(response.text)
            logger.info("Conclusão: O problema não está no token, mas sim em como a aplicação está fazendo a requisição (possivelmente um erro no código, na construção da URL ou nos headers).")

        elif response.status_code == 401:
            logger.error("❌ FALHA DE AUTENTICAÇÃO (Erro 401 Unauthorized).")
            logger.error("O servidor do Kommo rejeitou o seu Long-Lived Token.")
            logger.error("Causas Prováveis:")
            logger.error("1. O token foi revogado ou regenerado na interface do Kommo.")
            logger.error("2. O token expirou (alguns tokens de 'longa duração' ainda expiram).")
            logger.error("3. O subdomínio no .env está incorreto.")
            logger.error("Ação Imediata: Gere um novo Long-Lived Token na interface do Kommo e atualize o arquivo .env.")
            try:
                print(response.json())
            except requests.exceptions.JSONDecodeError:
                print(response.text)

        else:
            logger.warning(f"⚠️ Resposta inesperada da API: Status {response.status_code}")
            logger.warning("Isso pode indicar um problema de rede, um erro no servidor do Kommo ou um endpoint incorreto.")
            logger.info("Resposta da API:")
            try:
                print(response.json())
            except requests.exceptions.JSONDecodeError:
                print(response.text)

    except requests.exceptions.RequestException as e:
        logger.error(f"💥 Erro de Conexão: Não foi possível conectar à API do Kommo.")
        logger.error(f"Detalhes: {e}")
        logger.error("Verifique sua conexão com a internet e se a URL base do Kommo está correta e acessível.")

if __name__ == "__main__":
    diagnose_kommo_auth()
