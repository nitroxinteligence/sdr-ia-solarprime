"""
Lead Manager - Gerenciamento SIMPLES de leads
ZERO complexidade, funcionalidade total
"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime
from app.utils.logger import emoji_logger
from app.config import settings

class LeadManager:
    """
    Gerenciador SIMPLES de leads e qualificação
    Mantém toda a lógica de extração e scoring
    """
    
    def __init__(self):
        self.is_initialized = False
        self.scoring_enabled = settings.enable_lead_scoring
        
    def initialize(self):
        """Inicialização simples"""
        if self.is_initialized:
            return
            
        emoji_logger.system_ready("📊 LeadManager inicializado")
        self.is_initialized = True
    
    def extract_lead_info(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extrai informações do lead de forma SIMPLES
        
        Args:
            messages: Histórico de mensagens
            
        Returns:
            Informações extraídas do lead
        """
        lead_info = {
            "name": None,
            "phone": None,
            "email": None,
            "bill_value": None,
            "location": None,
            "property_type": None,
            "has_bill_image": False,
            "interests": [],
            "objections": [],
            "qualification_score": 0,
            "stage": "novo",
            "chosen_flow": None  # 🔥 CORREÇÃO: Campo para detectar seleção de fluxo
        }
        
        # Processar cada mensagem
        for msg in messages:
            content = msg.get("content", "").lower()
            
            # Extrair nome
            if not lead_info["name"]:
                name = self._extract_name(content)
                if name:
                    lead_info["name"] = name
            
            # Extrair email
            if not lead_info["email"]:
                email = self._extract_email(content)
                if email:
                    lead_info["email"] = email
            
            # Extrair valor da conta
            if not lead_info["bill_value"]:
                value = self._extract_bill_value(content)
                if value:
                    lead_info["bill_value"] = value
            
            # Detectar tipo de imóvel
            if not lead_info["property_type"]:
                prop_type = self._extract_property_type(content)
                if prop_type:
                    lead_info["property_type"] = prop_type
            
            # Detectar localização
            if not lead_info["location"]:
                location = self._extract_location(content)
                if location:
                    lead_info["location"] = location
            
            # Detectar interesses
            interests = self._extract_interests(content)
            lead_info["interests"].extend(interests)
            
            # Detectar objeções
            objections = self._extract_objections(content)
            lead_info["objections"].extend(objections)
            
            # 🔥 CORREÇÃO CRÍTICA: Detectar seleção de fluxo
            if not lead_info.get("chosen_flow"):
                chosen_flow = self._extract_chosen_flow(content)
                if chosen_flow:
                    lead_info["chosen_flow"] = chosen_flow
        
        # Remover duplicatas
        lead_info["interests"] = list(set(lead_info["interests"]))
        lead_info["objections"] = list(set(lead_info["objections"]))
        
        # Calcular score de qualificação
        if self.scoring_enabled:
            lead_info["qualification_score"] = self.calculate_qualification_score(lead_info)
            lead_info["stage"] = self.determine_stage(lead_info)
        
        return lead_info
    
    def calculate_qualification_score(self, lead_info: Dict[str, Any]) -> float:
        """
        Calcula score de qualificação SIMPLES
        
        Args:
            lead_info: Informações do lead
            
        Returns:
            Score de 0 a 100
        """
        score = 0.0
        
        # Valor da conta (peso 40%)
        bill_value = lead_info.get("bill_value", 0)
        if bill_value:
            if bill_value >= 1000:
                score += 40
            elif bill_value >= 700:
                score += 30
            elif bill_value >= 500:
                score += 20
            elif bill_value >= 300:
                score += 10
        
        # Informações fornecidas (peso 30%)
        if lead_info.get("name"):
            score += 10
        if lead_info.get("phone"):
            score += 10
        if lead_info.get("email"):
            score += 5
        if lead_info.get("location"):
            score += 5
        
        # Tipo de imóvel (peso 15%)
        property_type = lead_info.get("property_type") or ""  # Garante que nunca é None
        if "comercial" in property_type or "empresa" in property_type:
            score += 15
        elif "residencial" in property_type or "casa" in property_type:
            score += 10
        
        # Interesses demonstrados (peso 10%)
        interests = lead_info.get("interests", [])
        if len(interests) >= 3:
            score += 10
        elif len(interests) >= 2:
            score += 7
        elif len(interests) >= 1:
            score += 5
        
        # Objeções (peso -5%)
        objections = lead_info.get("objections", [])
        if len(objections) >= 3:
            score -= 5
        elif len(objections) >= 2:
            score -= 3
        
        # Garantir score entre 0 e 100
        return max(0, min(100, score))
    
    def determine_stage(self, lead_info: Dict[str, Any]) -> str:
        """
        Determina estágio do lead no funil
        
        Args:
            lead_info: Informações do lead
            
        Returns:
            Estágio do lead
        """
        score = lead_info.get("qualification_score", 0)
        
        if score >= 80:
            return "quente"
        elif score >= 60:
            return "morno"
        elif score >= 40:
            return "qualificando"
        elif score >= 20:
            return "interesse"
        else:
            return "novo"
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extrai nome do texto com filtros mais rigorosos"""
        
        # 🔥 CORREÇÃO CRÍTICA: Lista de palavras/frases que NÃO são nomes
        blacklist_phrases = [
            "anúncio", "anuncio", "energia solar", "solar", "energia",
            "propaganda", "publicidade", "oferta", "promoção", "desconto",
            "conta de luz", "conta", "luz", "eletricidade", "kwh",
            "instalação", "sistema", "painel", "placa", "telhado",
            "economia", "economizar", "reduzir", "diminuir",
            "whatsapp", "mensagem", "conversa", "chat", "texto"
        ]
        
        patterns = [
            # Padrões explícitos de apresentação (mais confiáveis)
            r"meu nome [eé] ([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,2})(?:[,\.\!]|$)",
            r"me chamo ([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,2})(?:[,\.\!]|$)",
            r"sou o ([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,2})(?:[,\.\!]|$)",
            r"sou a ([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,2})(?:[,\.\!]|$)",
            r"eu sou ([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,2})(?:[,\.\!]|$)",
            r"(?:^|\s)([A-Z][a-zÀ-ÿ]+\s+[A-Z][a-zÀ-ÿ]+)(?:\s|$)"  # Nomes próprios capitalizados (mais restrito)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip().title()
                
                # Validações rigorosas
                if len(name) < 3 or len(name) > 50:  # Nome muito curto ou muito longo
                    continue
                
                # 🔥 FILTRO PRINCIPAL: Verificar se o nome contém palavras da blacklist
                name_lower = name.lower()
                is_blacklisted = any(phrase in name_lower for phrase in blacklist_phrases)
                
                if is_blacklisted:
                    continue  # Pular nomes que contém palavras proibidas
                
                # Limitar a nomes razoáveis (máximo 3 palavras)
                words = name.split()
                if len(words) > 3:
                    continue
                
                # Verificar se as palavras são apenas letras (sem números ou símbolos estranhos)
                if all(word.isalpha() or any(c in "àáâãäåèéêëìíîïòóôõöùúûüýÿçñ" for c in word.lower()) for word in words):
                    # Verificar tamanho mínimo por palavra
                    if all(len(word) >= 2 for word in words):
                        return name
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extrai email do texto"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0).lower()
        return None
    
    def _extract_bill_value(self, text: str) -> Optional[float]:
        """Extrai valor da conta do texto"""
        patterns = [
            r"conta.{0,20}R?\$?\s*(\d+(?:[.,]\d{0,2})?)",
            r"pago.{0,20}R?\$?\s*(\d+(?:[.,]\d{0,2})?)",
            r"valor.{0,20}R?\$?\s*(\d+(?:[.,]\d{0,2})?)",
            r"(\d+(?:[.,]\d{0,2})?)\s*reais",  # 🔥 FIX: Detectar "450 reais"
            r"uns\s*(\d+(?:[.,]\d{0,2})?)",     # 🔥 FIX: Detectar "uns 450"
            r"R?\$?\s*(\d+(?:[.,]\d{0,2})?)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Pegar o maior valor encontrado
                    values = [float(m.replace(",", ".")) for m in matches]
                    # Filtrar valores razoáveis para conta de luz
                    reasonable_values = [v for v in values if 50 <= v <= 10000]
                    if reasonable_values:
                        return max(reasonable_values)
                except:
                    pass
        
        return None
    
    def _extract_property_type(self, text: str) -> Optional[str]:
        """Extrai tipo de imóvel"""
        # 🔥 FIX: Usar valores exatos aceitos pelo banco de dados
        types = {
            "casa": ["casa", "residência", "moradia"],
            "apartamento": ["apartamento", "apto", "ap"],
            "comercial": ["empresa", "comércio", "loja", "escritório", "comercial"],
            "rural": ["fazenda", "sítio", "chácara", "rural"]
        }
        
        for prop_type, keywords in types.items():
            if any(keyword in text for keyword in keywords):
                return prop_type
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extrai localização"""
        # Padrões de cidades/estados brasileiros
        patterns = [
            r"moro em ([A-Za-z\s]+)",
            r"sou de ([A-Za-z\s]+)",
            r"estou em ([A-Za-z\s]+)",
            r"cidade de ([A-Za-z\s]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        
        return None
    
    def _extract_interests(self, text: str) -> List[str]:
        """Extrai interesses demonstrados"""
        interests = []
        
        interest_keywords = {
            "economia": ["economizar", "economia", "reduzir conta", "conta menor"],
            "sustentabilidade": ["sustentável", "meio ambiente", "verde", "ecológico"],
            "investimento": ["investimento", "retorno", "valorização", "investir"],
            "independência": ["independência", "própria energia", "autossuficiente"],
            "tecnologia": ["tecnologia", "inovação", "moderno", "smart"]
        }
        
        for interest, keywords in interest_keywords.items():
            if any(keyword in text for keyword in keywords):
                interests.append(interest)
        
        return interests
    
    def _extract_objections(self, text: str) -> List[str]:
        """Extrai objeções mencionadas"""
        objections = []
        
        objection_keywords = {
            "preço": ["caro", "muito dinheiro", "não tenho", "sem condições"],
            "desconfiança": ["golpe", "enganação", "não confio", "suspeito"],
            "tempo": ["não é hora", "depois", "mais tarde", "futuro"],
            "propriedade": ["aluguel", "não é meu", "alugado", "inquilino"],
            "dúvidas": ["não entendo", "complicado", "difícil", "não sei"]
        }
        
        for objection, keywords in objection_keywords.items():
            if any(keyword in text for keyword in keywords):
                objections.append(objection)
        
        return objections
    
    def _extract_chosen_flow(self, text: str) -> Optional[str]:
        """
        Extrai escolha de fluxo do usuário
        🔥 CORREÇÃO: Detectar quando usuário seleciona opção (ex: "opção 1", "instalação própria")
        """
        text_lower = text.lower().strip()
        
        # Mapear os fluxos exatos do Kommo
        flow_mapping = {
            # Opções numéricas
            "opção 1": "Instalação Usina Própria",
            "opcao 1": "Instalação Usina Própria",
            "1": "Instalação Usina Própria",
            "instalação própria": "Instalação Usina Própria",
            "instalacao propria": "Instalação Usina Própria",
            "usina própria": "Instalação Usina Própria",
            
            "opção 2": "Aluguel de Lote",
            "opcao 2": "Aluguel de Lote",
            "2": "Aluguel de Lote",
            "aluguel": "Aluguel de Lote",
            "lote": "Aluguel de Lote",
            
            "opção 3": "Compra com Desconto",
            "opcao 3": "Compra com Desconto", 
            "3": "Compra com Desconto",
            "desconto": "Compra com Desconto",
            "compra": "Compra com Desconto",
            
            "opção 4": "Usina Investimento",
            "opcao 4": "Usina Investimento",
            "4": "Usina Investimento",
            "investimento": "Usina Investimento",
            "usina investimento": "Usina Investimento"
        }
        
        # Padrões específicos para detectar escolha de fluxo
        flow_patterns = [
            r"quero\s+(?:a\s+)?opç[ãa]o\s*(\d+)",
            r"escolho\s+(?:a\s+)?opç[ãa]o\s*(\d+)",
            r"opç[ãa]o\s*(\d+)",
            r"quero\s+(?:a\s+)?(\d+)",
            r"escolho\s+(?:a\s+)?(\d+)"
        ]
        
        # Primeiro tentar padrões específicos de opções
        for pattern in flow_patterns:
            match = re.search(pattern, text_lower)
            if match:
                option_num = match.group(1)
                if option_num in ["1", "2", "3", "4"]:
                    # Mapear número para fluxo correto
                    if option_num == "1":
                        return "Instalação Usina Própria"
                    elif option_num == "2":
                        return "Aluguel de Lote"
                    elif option_num == "3":
                        return "Compra com Desconto"
                    elif option_num == "4":
                        return "Usina Investimento"
        
        # Depois verificar palavras-chave específicas
        for key, flow in flow_mapping.items():
            if key in text_lower:
                # Evitar falsos positivos com números soltos
                # Só aceitar números isolados se vierem com contexto de escolha
                if key.isdigit():
                    # Verificar se é uma escolha explícita
                    choice_context = ["quero", "escolho", "opção", "opcao", "número", "numero"]
                    if not any(ctx in text_lower for ctx in choice_context):
                        continue  # Ignorar números sem contexto de escolha
                
                # Evitar pegar valores monetários
                if key.isdigit() and ("r$" in text_lower or "reais" in text_lower or "conta" in text_lower):
                    continue
                    
                return flow
        
        # Não retornar nada se não for uma escolha clara de fluxo
        return None
    
    def format_lead_summary(self, lead_info: Dict[str, Any]) -> str:
        """
        Formata resumo do lead para exibição
        
        Args:
            lead_info: Informações do lead
            
        Returns:
            Resumo formatado
        """
        summary = "📊 **Resumo do Lead**\n\n"
        
        if lead_info.get("name"):
            summary += f"👤 Nome: {lead_info['name']}\n"
        
        if lead_info.get("phone"):
            summary += f"📱 Telefone: {lead_info['phone']}\n"
        
        if lead_info.get("email"):
            summary += f"📧 Email: {lead_info['email']}\n"
        
        if lead_info.get("location"):
            summary += f"📍 Localização: {lead_info['location']}\n"
        
        if lead_info.get("bill_value"):
            summary += f"💰 Valor da conta: R$ {lead_info['bill_value']:.2f}\n"
        
        if lead_info.get("property_type"):
            summary += f"🏠 Tipo de imóvel: {lead_info['property_type']}\n"
        
        if lead_info.get("interests"):
            summary += f"✨ Interesses: {', '.join(lead_info['interests'])}\n"
        
        if lead_info.get("objections"):
            summary += f"⚠️ Objeções: {', '.join(lead_info['objections'])}\n"
        
        if lead_info.get("chosen_flow"):
            summary += f"🎯 Fluxo escolhido: {lead_info['chosen_flow']}\n"
        
        if self.scoring_enabled:
            summary += f"\n🎯 Score: {lead_info['qualification_score']:.0f}/100\n"
            summary += f"📈 Estágio: {lead_info['stage'].upper()}\n"
        
        return summary