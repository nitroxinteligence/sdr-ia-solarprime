# 🔑 Como Configurar a API Key do Gemini

## Passo a Passo

### 1. Obter API Key
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a API key gerada

### 2. Configurar no Projeto

#### Opção A: Usar o script de configuração
```bash
python scripts/setup_api_key.py
```

#### Opção B: Editar manualmente o arquivo .env
1. Abra o arquivo `.env`
2. Localize a linha:
   ```
   GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
   ```
3. Substitua `YOUR_GEMINI_API_KEY_HERE` pela sua API key real:
   ```
   GEMINI_API_KEY="AIzaSy..."
   ```

### 3. Testar
```bash
python scripts/test_agent.py
```

## Importante
- A API key é gratuita para uso moderado
- Mantenha sua API key segura e nunca a compartilhe
- O arquivo `.env` já está no `.gitignore` para segurança