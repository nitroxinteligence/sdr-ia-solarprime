# Instruções para Corrigir Deploy no EasyPanel

## Problema
O erro "Failed to pull changes" ocorre porque fizemos um force push para remover arquivos sensíveis do histórico do Git.

## Solução no EasyPanel

### Opção 1: Reset do Repositório (Recomendado)
No painel de configuração do seu app no EasyPanel:

1. Vá em **Source** ou **Git Configuration**
2. Procure por uma opção de **"Force Pull"** ou **"Reset Repository"**
3. Se não houver, tente estas alternativas:

### Opção 2: Via Terminal/SSH do EasyPanel
Se você tem acesso SSH ao container:

```bash
cd /app
git fetch --all
git reset --hard origin/main
```

### Opção 3: Recriar o Deploy
1. Delete o app atual no EasyPanel
2. Crie um novo app com a mesma configuração
3. Configure novamente:
   - Repository: https://github.com/nitroxinteligence/sdr-ia-solarprime.git
   - Branch: main
   - Build Command: (deixar vazio ou usar Dockerfile)
   - Port: 8000

### Opção 4: Webhook Manual
Se o EasyPanel permite comandos customizados:

```bash
git fetch origin
git reset --hard origin/main
git clean -fd
```

## Verificação
Após resolver, o deploy deve mostrar o último commit:
- Hash: 8606220
- Mensagem: "feat: Implementar correções completas e integrações para produção"

## Importante
- Todos os arquivos .env foram removidos do repositório
- Configure as variáveis de ambiente diretamente no EasyPanel
- O arquivo Dockerfile está atualizado e funcionando corretamente