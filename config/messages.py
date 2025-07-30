"""
Mensagens Humanizadas - Helen Vieira
=====================================
Centralização de todas as mensagens do sistema
com tom natural e acolhedor da consultora Helen
"""

import random
from typing import List, Dict, Optional
from datetime import datetime

class HumanizedMessages:
    """Mensagens humanizadas para a Helen Vieira"""
    
    # Mensagens de erro técnico - mais naturais e menos robóticas
    ERRO_TECNICO = [
        "Opa, me perdi um pouquinho aqui 😊 Pode repetir, por favor?",
        "Nossa, acho que me confundi... Vamos tentar de novo?",
        "Hmm, deixa eu organizar melhor aqui... Pode me dizer novamente?",
        "Xiii, travou alguma coisa aqui do meu lado... Me dá um segundinho?",
        "Eita, preciso de uma ajudinha sua... Pode reformular a pergunta?",
        "Desculpa, acho que não captei direito... Pode explicar de outro jeito?",
        "Opa, tive um pequeno contratempo aqui... Vamos recomeçar?",
        "Me confundi aqui 😅 Pode me ajudar repetindo?",
        "Parece que algo não funcionou como esperado... Tentamos de novo?"
    ]
    
    # Mensagens para processamento de imagens
    ERRO_IMAGEM = [
        "A foto chegou meio escurinha aqui... Consegue tirar outra com mais luz? O flash ajuda bastante! 📸",
        "Parece que o WhatsApp comprimiu demais a imagem... Tenta enviar como documento, fica melhor!",
        "A imagem não veio muito nítida... Pode tirar outra foto focando bem na conta? 📱",
        "Hmm, não consegui ver direito os números... Uma foto mais de perto ajudaria!",
        "A qualidade da imagem ficou baixa na transmissão... Vamos tentar de novo?",
        "Não consegui ler alguns dados da conta na foto... Pode mandar outra mais clarinha?",
        "Opa, a imagem chegou cortada aqui... Tenta enquadrar a conta inteira na foto!"
    ]
    
    # Mensagens para processamento de PDFs
    ERRO_PDF = [
        "O PDF está pesadinho para abrir... Uma foto da conta funciona super bem também! Que tal? 📱",
        "Hmm, não consegui abrir o PDF direito... Às vezes uma foto simples da conta resolve melhor!",
        "O arquivo PDF está demorando para processar... Que tal enviar uma foto? É mais rápido! 📸",
        "Parece que o PDF está com algum problema... Uma foto da primeira página já me ajuda muito!",
        "Tive dificuldade com o PDF... Mas se você tirar uma foto da conta, consigo analisar na hora!",
        "O PDF não quer colaborar comigo hoje 😅 Manda uma foto que eu analiso rapidinho!"
    ]
    
    # Mensagens para processamento de áudio
    ERRO_AUDIO = [
        "O áudio chegou cortado aqui... Que tal me contar por mensagem? Respondo rapidinho! 💬",
        "Parece que teve uma interferência no áudio... Pode digitar? Assim não perdemos nada!",
        "Não consegui entender direito o áudio... Me escreve que fica mais fácil de eu te ajudar! 😊",
        "O áudio veio com chiado... Pode me mandar por texto? Prometo responder rápido!",
        "Hmm, o som não ficou muito claro... Que tal escrever? Assim garanto que entendo tudo!",
        "Tive problema para ouvir o áudio... Mas se digitar, respondo na mesma hora!"
    ]
    
    # Mensagens de fallback por estágio - múltiplas variações
    FALLBACK_POR_ESTAGIO = {
        "INITIAL_CONTACT": [
            "Oi! Sou a Helen da Solar Prime 😊 Estava organizando umas coisas aqui, mas já estou com você! Como posso te chamar?",
            "Olá! Helen Vieira aqui, da Solar Prime! Desculpa a demora, estava finalizando outro atendimento. Qual seu nome?",
            "Oii! Aqui é a Helen da Solar Prime! Tive um pequeno delay aqui, mas agora estou 100% com você! Como prefere ser chamado?",
            "Opa! Helen aqui 👋 Me desculpe a espera, já estou disponível! Antes de tudo, como é seu nome?",
            "Olá! Sou a Helen, consultora da Solar Prime! Pequeno contratempo resolvido, vamos conversar? Me diz seu nome!"
        ],
        
        "IDENTIFICATION": [
            "{name}, mil perdões pela pausa! Agora sim, me conta: você quer economizar na conta ou instalar painéis solares?",
            "Desculpa {name}! Precisei resolver uma coisinha rápida. Então, seu interesse é economia ou usina própria?",
            "{name}, voltei! 😊 Agora me diz: está buscando reduzir a conta de luz ou quer sua própria usina?",
            "Oi {name}, desculpe a demora! Vamos lá: você prefere economizar na conta atual ou ter energia solar própria?",
            "Eita {name}, me perdoa! Agora estou 100% aqui. Me conta qual sua necessidade com energia solar?"
        ],
        
        "QUALIFICATION": [
            "Ops, me distraí aqui! 😅 Mas vamos ao que interessa: me conta qual o valor da sua conta de luz?",
            "{name}, desculpa! Precisei resolver uma coisinha aqui. Agora me diz: quanto você paga de energia por mês?",
            "Mil perdões pela pausa! Estava calculando umas economias aqui... Falando nisso, qual o valor da sua conta?",
            "{name}, voltei! Agora sim, para eu preparar sua proposta: qual o valor médio da conta de luz?",
            "Desculpe a interrupção! Vamos continuar: me passa o valor aproximado da sua fatura de energia?"
        ],
        
        "DISCOVERY": [
            "Opa, me perdi aqui! 😅 {name}, você já tem algum desconto na conta de luz atualmente?",
            "Desculpe {name}! Voltando... Você já recebe algum benefício ou desconto na energia?",
            "{name}, mil perdões! Agora me conta: tem algum desconto ou benefício na sua conta hoje?",
            "Eita, pequena pausa técnica! 😊 {name}, você já tem alguma economia na conta de luz?",
            "Voltei {name}! Me diz uma coisa: sua conta já tem algum tipo de desconto?"
        ],
        
        "SCHEDULING": [
            "Desculpe {name}! Estava verificando a agenda... Temos estes horários:\n\n*Segunda*: 10h ou 14h\n*Terça*: 9h ou 16h\n\nQual prefere?",
            "{name}, perdão pela espera! Consultei os horários disponíveis:\n\n*Amanhã*: 11h ou 15h\n*Quinta*: 10h ou 14h\n\nQual fica melhor?",
            "Opa, demorei verificando a agenda! Tenho estes horários:\n\n*Quarta*: 9h ou 13h\n*Sexta*: 10h ou 15h\n\nQual combina melhor?",
            "Mil desculpas {name}! Os horários disponíveis são:\n\n*Segunda*: 11h ou 16h\n*Terça*: 9h ou 14h\n\nPode ser algum destes?",
            "{name}, voltei com os horários! Temos:\n\n*Amanhã*: 10h ou 15h\n*Depois*: 9h ou 14h\n\nQual encaixa melhor pra você?"
        ],
        
        "NURTURING": [
            "Oi {name}! Lembrei de você e vim ver se ainda precisa economizar na conta de luz 😊",
            "{name}, passando para saber se repensou sobre aquela economia que conversamos!",
            "E aí {name}? Ainda com interesse em reduzir a conta de luz? Estou por aqui!",
            "Olá {name}! Voltei para ver se posso te ajudar com a economia de energia!",
            "{name}, oi! Aquela conta de luz continua pesando? Podemos resolver isso!"
        ]
    }
    
    # Mensagens de follow-up mais naturais
    FOLLOW_UP_TEMPLATES = {
        "30_minutos": [
            "Oi {name}! Vi que paramos nossa conversa no meio... Tudo bem aí? 😊",
            "{name}, ficou alguma dúvida sobre o que conversamos? Estou por aqui!",
            "E aí, {name}? Nossa conversa ficou pela metade... Posso ajudar em algo?",
            "{name}, percebi que você sumiu... Aconteceu alguma coisa? Continuo disponível!",
            "Opa {name}! Acho que perdemos a conexão... Quer continuar de onde paramos?"
        ],
        
        "24_horas": [
            "{name}, passando pra ver se você teve tempo de pensar sobre aquela economia... Qualquer dúvida, só chamar!",
            "Oi {name}! Lembrei da nossa conversa ontem... Se precisar de mais informações, me avisa!",
            "{name}, boa tarde! Se ainda tiver interesse naquela economia que falamos, estou à disposição 😊",
            "E aí {name}? Conseguiu conversar com a família sobre a proposta? Fico no aguardo!",
            "{name}, ontem ficou alguma dúvida? Estou aqui para esclarecer o que precisar!"
        ],
        
        "48_horas": [
            "{name}, oi! Ainda dá tempo de aproveitar aquela economia que conversamos... Que tal?",
            "Olá {name}! Passaram 2 dias e vim ver se repensou sobre reduzir a conta de luz 😊",
            "{name}, lembra de mim? Helen da Solar Prime! Ainda posso te ajudar com a economia!",
            "Oi {name}! Aquela proposta de economia ainda está de pé... Vamos conversar?",
            "{name}, voltei! 😊 Se quiser retomar nossa conversa sobre economia, é só chamar!"
        ],
        
        "7_dias": [
            "{name}, uma semana se passou... Ainda tempo de começar a economizar! Vamos conversar?",
            "Oi {name}! Lembra da economia na conta de luz? A oportunidade continua disponível!",
            "{name}, boa tarde! Passando para ver se mudou de ideia sobre a energia solar 😊",
            "E aí {name}? Aquela conta de luz continua alta? Ainda posso te ajudar!",
            "{name}, oi! Uma semana depois e a oferta de economia continua valendo!"
        ]
    }
    
    # Mensagens para situações específicas
    SITUACOES_ESPECIAIS = {
        "multiplas_mensagens": [
            "{name}, recebi várias mensagens suas! 😊 Vou responder tudo juntinho, tá?",
            "Opa, chegou um montão de mensagens! Me dá um segundinho para ler tudo, {name}!",
            "{name}, vi que mandou várias coisas! Já li tudo e vou te responder!",
            "Eita, quantas mensagens! 😅 Calma {name}, já processei tudo!"
        ],
        
        "comando_clear": [
            "Prontinho {name}! Conversa limpa, começamos do zero! Como posso ajudar?",
            "Tudo limpo! 🧹 Vamos recomeçar nossa conversa, {name}?",
            "Feito! Histórico apagado. Em que posso te ajudar hoje, {name}?",
            "Conversa resetada com sucesso! O que deseja saber sobre energia solar?"
        ],
        
        "horario_comercial": [
            "Oi {name}! Vi sua mensagem. Como é fora do horário comercial, te respondo amanhã cedo, tá? 😊",
            "{name}, recebi sua mensagem! Amanhã pela manhã te respondo com toda atenção!",
            "Opa {name}! Mensagem recebida. Te retorno amanhã no primeiro horário!",
            "Oi {name}! Anotei aqui. Amanhã cedinho continuo nosso papo!"
        ],
        
        "agradecimento": [
            "Por nada, {name}! 😊 Estou aqui pra isso!",
            "Imagine, {name}! Foi um prazer ajudar!",
            "Que isso, {name}! Fico feliz em poder ajudar!",
            "Sempre às ordens, {name}! 💚"
        ]
    }
    
    @staticmethod
    def get_random_message(category: str, subcategory: Optional[str] = None) -> str:
        """Retorna uma mensagem aleatória da categoria especificada"""
        if subcategory:
            messages = getattr(HumanizedMessages, category, {}).get(subcategory, [])
        else:
            messages = getattr(HumanizedMessages, category, [])
        
        if not messages:
            return "Opa, algo não saiu como esperado... Vamos tentar de novo?"
        
        return random.choice(messages)
    
    @staticmethod
    def get_fallback_by_stage(stage: str, name: str = "") -> str:
        """Retorna uma mensagem fallback apropriada para o estágio"""
        messages = HumanizedMessages.FALLBACK_POR_ESTAGIO.get(stage, [])
        if not messages:
            messages = HumanizedMessages.FALLBACK_POR_ESTAGIO["INITIAL_CONTACT"]
        
        message = random.choice(messages)
        return message.format(name=name) if "{name}" in message else message
    
    @staticmethod
    def get_follow_up(interval: str, name: str) -> str:
        """Retorna uma mensagem de follow-up humanizada"""
        messages = HumanizedMessages.FOLLOW_UP_TEMPLATES.get(interval, [])
        if not messages:
            return f"Oi {name}! Ainda posso te ajudar com economia na conta de luz?"
        
        return random.choice(messages).format(name=name)
    
    @staticmethod
    def get_time_aware_greeting() -> str:
        """Retorna uma saudação baseada no horário"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greetings = ["Bom dia!", "Opa, bom dia!", "Olá, bom dia!"]
        elif 12 <= hour < 18:
            greetings = ["Boa tarde!", "Oi, boa tarde!", "Olá, boa tarde!"]
        else:
            greetings = ["Boa noite!", "Oi, boa noite!", "Olá, boa noite!"]
        
        return random.choice(greetings)
    
    @staticmethod
    def personalize_error(error_type: str, name: str = "", context: Dict = None) -> str:
        """Personaliza mensagem de erro com contexto"""
        base_message = HumanizedMessages.get_random_message(error_type)
        
        # Adiciona nome se disponível
        if name and "{name}" not in base_message:
            base_message = f"{name}, {base_message.lower()}"
        elif name:
            base_message = base_message.format(name=name)
        
        # Adiciona contexto temporal se for tarde da noite
        hour = datetime.now().hour
        if hour >= 22 or hour < 6:
            base_message += " Já está tarde, mas prometo resolver isso rapidinho!"
        
        return base_message

# Aliases para facilitar imports
ERROR_MESSAGES = HumanizedMessages.ERRO_TECNICO
IMAGE_ERRORS = HumanizedMessages.ERRO_IMAGEM
PDF_ERRORS = HumanizedMessages.ERRO_PDF
AUDIO_ERRORS = HumanizedMessages.ERRO_AUDIO
FALLBACK_MESSAGES = HumanizedMessages.FALLBACK_POR_ESTAGIO
FOLLOW_UP_MESSAGES = HumanizedMessages.FOLLOW_UP_TEMPLATES
SPECIAL_SITUATIONS = HumanizedMessages.SITUACOES_ESPECIAIS

# Funções helper
get_error_message = HumanizedMessages.get_random_message
get_fallback_message = HumanizedMessages.get_fallback_by_stage
get_follow_up_message = HumanizedMessages.get_follow_up
get_greeting = HumanizedMessages.get_time_aware_greeting
personalize_message = HumanizedMessages.personalize_error

def get_special_message(situation: str, name: str = "") -> str:
    """Retorna uma mensagem especial humanizada"""
    messages = HumanizedMessages.SITUACOES_ESPECIAIS.get(situation, [])
    if not messages:
        return "Opa, algo não saiu como esperado... Vamos tentar de novo?"
    
    message = random.choice(messages)
    return message.format(name=name) if "{name}" in message else message

__all__ = [
    "HumanizedMessages",
    "ERROR_MESSAGES",
    "IMAGE_ERRORS", 
    "PDF_ERRORS",
    "AUDIO_ERRORS",
    "FALLBACK_MESSAGES",
    "FOLLOW_UP_MESSAGES",
    "SPECIAL_SITUATIONS",
    "get_error_message",
    "get_fallback_message",
    "get_follow_up_message",
    "get_greeting",
    "personalize_message",
    "get_special_message"
]