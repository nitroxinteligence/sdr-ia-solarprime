# 🚀 Configuração das Variáveis de Ambiente no EasyPanel

## Google Calendar Service Account

Copie e cole estas variáveis no EasyPanel com os valores já extraídos do JSON:

```bash
# Ativar Service Account (IMPORTANTE!)
GOOGLE_USE_SERVICE_ACCOUNT=true

# Email do Service Account
GOOGLE_SERVICE_ACCOUNT_EMAIL=sdr-calendar-service-886@solarprime-ia-sdr.iam.gserviceaccount.com

# Chave privada (COPIE EXATAMENTE COMO ESTÁ ABAIXO, COM AS QUEBRAS DE LINHA)
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/xxKt00VGBZgO\nOLcMxQ5/GSuMe3oVybhDelZjkqsbLv8nj3b/cVhUyJBdG0d5NwxOVIUuuGP3I2Lk\nTOVdta/udEFOyc9WHCbN0pQ9FOMeI2kobhqQhUbu48NfopUNz0TelYgq9kbfq3Ih\nvOUDY1/QVr4LhY1tS56yAFtHawtRMJgFXf3aiZNU5XaRzgAw/KuinSfpIlIAroP3\nPCA7cMIj7dDiQ3jWqvD6/ImueW9fCoCw5x2qt9HLcZb9L8AsIiVF+nqcXi3cfLzq\n76LbdaRo+hsmS6Cbwa0eJQjuy9SIvQCKyUO3LBtNbXaQlMV3Ow/RWLZAdTPBPpi3\nW+c1UULXAgMBAAECggEAAV92TEVEwTASuxiqgs5kVgJC9AysPpIE84K23Jv1BUr3\nAPxUxeu0o1gTjym9/2mmo7w/fyqgbelUcL2g2g9jajRt2pe07XENJrsOXEjqfqbn\n6VCvIwAOlnDjT1YgIAsEULLxrcZj59UCilL1BsBZiWnIOYKOv8y4nvNECVpZqI6f\n0SO7r/2SKyDCsMyBnlY4MMa0BPDw134PmcqLmXFDSFAenOXhSuTS1kJ2uBspJN74\nNViIfzuPOHQxwQvSqEyJJHwRIsqx0HzDT7ZK/1H3ywUQyOHVBQVFYUyHoeDXz9GZ\nBo1F/imtkCzDQ6NYqSnJAw33BVtuHMDwlEHDVEhOUQKBgQDwXavZntwCUGxH6bEx\nCjrSJoCfdlUYqoq4d4o7qYxp3sqf2rY/65q7V8BA+B2GygST5oaQFc/dWobDm4vR\ng445Fam6Y1DrtsrNViGZysVgbBDSY2YCymwhGNPC4x7cj7NPj1AVwP6jPp9y9CDo\n69EJhF84GfsbRjUj/MzAKS2vBwKBgQDMQFvuun28Sbfwmi6WfVS0eVmqkEnXVo6C\nXyYs90ae4+I1ed5rg5l++2AgYx9LyClCAyy2FmA0dN/MnIdD/GlNk2sO35EoCept\n6ZihJfzeDKFdhkQofiVm+C4d5k/sPnm5oY0SQmJdT3fVvWdr3O1W3woAv47Yz/Kh\nRg74GMwJsQKBgFaNdGdNo+2VZhhTF0IQa/Pmd2R0aNoT9xXLvdQUDoLE/fOn/v5v\naW1SgOEkNwWlUxaq6QOTRyFvCp3/Mc7E736wxUhfoPDwBoEAJeNKN96rqzcHIeGZ\nYGxek0pXHHLRsADTG0RqFYdU8nejXwJggApMRzldaaV9l38Y9eWwLkobAoGATS0I\nT6UBu3JzYSMw9UX4CpVLryoD7KzU/ifrqdPpSEI9CA27YA6Cojtjb/lkKuM/y6Sd\ncVP1F/0NTyfZ6HNoapqIOj95fpJ4lP1N4Z4T9Ob61fbUrCQ2B7lA26VZj59vqReE\n0WBqAG31jrqZaGU6/Lcb9XpsBDpWqF9rao0cE5ECgYEAtmhTSNfyKtAU+qD691jB\nnJOV/pDM+i7kvywjb6MFNIr52XpEM8cWsdpqOwMYqWVUAjleLY1LT+dXruCqSjck\neD2FHp1g/b4R7lhp64Po3cfN/O1AyFHgIzAx17NHUNM4lQS4+S7ucWMMrhIK/HNu\n3bYT4KVaMf6JdWpA079elmg=\n-----END PRIVATE KEY-----\n"

# ID do projeto
GOOGLE_PROJECT_ID=solarprime-ia-sdr

# ID da chave privada
GOOGLE_PRIVATE_KEY_ID=3917e7e4540ec09bea5bfa3e12cccb9b699e5dc4
# ID do cliente
GOOGLE_CLIENT_ID=101231464262429936896
# ID do calendário (IMPORTANTE: Use o email do usuário que compartilhou o calendário)
GOOGLE_CALENDAR_ID=leonardofvieira00@gmail.com

```

## ⚠️ IMPORTANTE - Próximos Passos

### 1. Compartilhar o Calendário (OBRIGATÓRIO!)

1. Abra o Google Calendar do usuário que terá os eventos
2. Vá em **Configurações** ⚙️ > **Configurações do meu calendário**
3. Clique no calendário desejado
4. Em **Compartilhar com pessoas específicas**, clique em **Adicionar pessoas**
5. Cole este email: `sdr-calendar-service-886@solarprime-ia-sdr.iam.gserviceaccount.com`
6. Defina a permissão: **Fazer alterações em eventos**
7. Clique em **Enviar**

### 2. Configurar GOOGLE_CALENDAR_ID

Substitua `seu-email@empresa.com.br` pelo email do usuário que compartilhou o calendário.

Por exemplo:
- Se o calendário é de maria@solarprime.com.br, use: `GOOGLE_CALENDAR_ID=maria@solarprime.com.br`
- Se o calendário é de vendas@solarprime.com.br, use: `GOOGLE_CALENDAR_ID=vendas@solarprime.com.br`

### 3. Deploy no EasyPanel

1. Copie todas as variáveis acima
2. No EasyPanel, vá em **Environment**
3. Cole as variáveis
4. Clique em **Save**
5. Faça o **Deploy**

## 🔍 Verificação

Após o deploy, verifique os logs para confirmar:

```
✅ Google Calendar service inicializado com Service Account
📅 Usando calendário: seu-email@empresa.com.br
```

Se aparecer algum erro de permissão, verifique se compartilhou o calendário corretamente.

## 📝 Notas

- A chave privada deve ser copiada EXATAMENTE como está, incluindo os `\n`
- O sistema criará automaticamente o arquivo JSON a partir dessas variáveis
- Não é necessário fazer upload de nenhum arquivo
- Esta configuração é permanente - não expira como tokens OAuth