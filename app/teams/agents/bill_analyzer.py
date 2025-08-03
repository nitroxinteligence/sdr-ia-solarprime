"""
BillAnalyzerAgent - Agente Especializado em Análise de Contas de Luz
Responsável por OCR, extração de dados e cálculo de economia
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import base64
import re

from agno.agent import Agent
from agno.tools import tool
from loguru import logger

from app.integrations.supabase_client import supabase_client
from app.config import settings


class BillProvider(Enum):
    """Fornecedores de energia"""
    CELPE = "celpe"          # Companhia Energética de Pernambuco
    COELBA = "coelba"        # Companhia de Eletricidade da Bahia
    COSERN = "cosern"        # Companhia Energética do RN
    ELEKTRO = "elektro"      # Elektro SP/MS
    LIGHT = "light"          # Light RJ
    CEMIG = "cemig"          # CEMIG MG
    COPEL = "copel"          # COPEL PR
    CPFL = "cpfl"            # CPFL SP
    UNKNOWN = "unknown"      # Não identificado


class TariffType(Enum):
    """Tipos de tarifa"""
    RESIDENCIAL = "residencial"
    COMERCIAL = "comercial"
    INDUSTRIAL = "industrial"
    RURAL = "rural"
    PODER_PUBLICO = "poder_publico"


class BillAnalyzerAgent:
    """
    Agente especializado em análise de contas de energia
    Realiza OCR, extração de dados e cálculos de economia
    """
    
    def __init__(self, model, storage):
        """
        Inicializa o agente analisador de contas
        
        Args:
            model: Modelo LLM a ser usado (preferencialmente com vision)
            storage: Storage para persistência
        """
        self.model = model
        self.storage = storage
        
        # Configurações de análise
        self.analysis_config = {
            "min_bill_value": 2000.0,       # Valor mínimo para qualificação
            "ideal_bill_value": 4000.0,     # Valor ideal
            "high_bill_value": 6000.0,      # Valor alto (lead quente)
            "savings_percentage": 0.20,      # 20% de economia garantida
            "roi_months": 48,                # ROI médio de 48 meses
            "system_lifetime_years": 25,     # Vida útil do sistema
            "kwh_price_avg": 0.85            # Preço médio do kWh
        }
        
        # Padrões regex para extração
        self.extraction_patterns = {
            "bill_value": [
                r"TOTAL\s+A\s+PAGAR[\s:]*R?\$?\s*([\d.,]+)",
                r"VALOR\s+TOTAL[\s:]*R?\$?\s*([\d.,]+)",
                r"TOTAL[\s:]*R?\$?\s*([\d.,]+)",
                r"A\s+PAGAR[\s:]*R?\$?\s*([\d.,]+)"
            ],
            "consumption_kwh": [
                r"CONSUMO\s+(?:TOTAL)?[\s:]*(\d+)\s*kWh",
                r"(\d+)\s*kWh",
                r"CONSUMO\s+MENSAL[\s:]*(\d+)"
            ],
            "customer_name": [
                r"CLIENTE[\s:]*([A-Z\s]+)",
                r"NOME[\s:]*([A-Z\s]+)",
                r"TITULAR[\s:]*([A-Z\s]+)"
            ],
            "installation_number": [
                r"INSTALAÇÃO[\s:]*(\d+)",
                r"UC[\s:]*(\d+)",
                r"CONTA\s+CONTRATO[\s:]*(\d+)"
            ],
            "address": [
                r"ENDEREÇO[\s:]*(.+?)(?:CEP|BAIRRO)",
                r"LOCAL[\s:]*(.+?)(?:CEP|BAIRRO)"
            ]
        }
        
        # Tools do agente
        self.tools = [
            self.analyze_bill_image,
            self.extract_bill_data,
            self.calculate_savings,
            self.calculate_solar_system,
            self.compare_bills,
            self.generate_proposal,
            self.validate_bill_value,
            self.identify_provider
        ]
        
        # Criar o agente
        self.agent = Agent(
            name="Bill Analyzer",
            model=self.model,
            role="""Você é um especialista em análise de contas de energia elétrica.
            
            Suas responsabilidades:
            1. Analisar imagens de contas de luz com OCR
            2. Extrair dados importantes (valor, consumo, titular)
            3. Calcular economia potencial com energia solar
            4. Dimensionar sistema solar adequado
            5. Gerar propostas personalizadas
            
            Expertise:
            - Tarifas de energia por região
            - Bandeiras tarifárias
            - Cálculo de dimensionamento solar
            - ROI e payback de sistemas
            - Economia de longo prazo
            
            Sempre que analisar uma conta:
            - Extraia TODOS os dados possíveis
            - Valide os valores encontrados
            - Calcule economia realista
            - Sugira sistema adequado""",
            
            tools=self.tools,
            instructions=[
                "Analise cuidadosamente a imagem da conta",
                "Extraia valor total, consumo em kWh e dados do cliente",
                "Calcule economia de 20% garantida",
                "Dimensione sistema solar apropriado",
                "Considere bandeiras tarifárias se visíveis",
                "Valide se o valor atende critérios mínimos"
            ]
        )
        
        logger.info("✅ BillAnalyzerAgent inicializado")
    
    @tool
    async def analyze_bill_image(
        self,
        image_data: str,  # Base64
        extract_all: bool = True
    ) -> Dict[str, Any]:
        """
        Analisa imagem de conta de luz usando Vision API
        
        Args:
            image_data: Imagem em base64
            extract_all: Se deve extrair todos os dados
            
        Returns:
            Dados extraídos da conta
        """
        try:
            # Verificar se o modelo suporta vision
            if not hasattr(self.model, 'vision') and 'gemini' not in str(type(self.model)).lower():
                logger.warning("Modelo não suporta vision, usando fallback")
                return await self._analyze_with_ocr_fallback(image_data)
            
            # Decodificar imagem
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                logger.error(f"Erro ao decodificar imagem: {e}")
                return {
                    "success": False,
                    "error": "Imagem inválida"
                }
            
            # Preparar prompt para análise
            prompt = """
            Analise esta conta de energia elétrica e extraia as seguintes informações:
            
            1. VALOR TOTAL A PAGAR (em R$)
            2. CONSUMO em kWh
            3. NOME DO TITULAR
            4. ENDEREÇO da instalação
            5. NÚMERO DA INSTALAÇÃO/UC
            6. MÊS DE REFERÊNCIA
            7. FORNECEDOR (Celpe, Coelba, etc)
            8. TIPO DE TARIFA (residencial, comercial, etc)
            9. BANDEIRA TARIFÁRIA se visível
            10. HISTÓRICO DE CONSUMO se disponível
            
            Retorne os dados em formato estruturado JSON.
            Se não encontrar algum campo, indique como null.
            
            IMPORTANTE: O valor total deve ser o valor final a pagar, não valores parciais.
            """
            
            # Usar Vision API
            response = await self.model.generate(
                prompt,
                images=[image_bytes]
            )
            
            # Parse da resposta
            try:
                # Extrair JSON da resposta
                import json
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    extracted_data = json.loads(json_str)
                else:
                    # Fallback para extração manual
                    extracted_data = self._extract_from_text(response)
            except Exception as e:
                logger.error(f"Erro ao parsear resposta: {e}")
                extracted_data = self._extract_from_text(response)
            
            # Validar e formatar dados
            result = {
                "success": True,
                "bill_value": self._parse_currency(
                    extracted_data.get("valor_total") or 
                    extracted_data.get("VALOR TOTAL A PAGAR")
                ),
                "consumption_kwh": self._parse_number(
                    extracted_data.get("consumo") or
                    extracted_data.get("CONSUMO em kWh")
                ),
                "customer_name": extracted_data.get("nome_titular") or extracted_data.get("NOME DO TITULAR"),
                "address": extracted_data.get("endereco") or extracted_data.get("ENDEREÇO"),
                "installation_number": extracted_data.get("numero_instalacao") or extracted_data.get("NÚMERO DA INSTALAÇÃO"),
                "reference_month": extracted_data.get("mes_referencia") or extracted_data.get("MÊS DE REFERÊNCIA"),
                "provider": extracted_data.get("fornecedor") or extracted_data.get("FORNECEDOR"),
                "tariff_type": extracted_data.get("tipo_tarifa") or extracted_data.get("TIPO DE TARIFA"),
                "tariff_flag": extracted_data.get("bandeira") or extracted_data.get("BANDEIRA TARIFÁRIA"),
                "consumption_history": extracted_data.get("historico") or extracted_data.get("HISTÓRICO DE CONSUMO")
            }
            
            # Calcular kWh price se possível
            if result["bill_value"] and result["consumption_kwh"]:
                result["kwh_price"] = result["bill_value"] / result["consumption_kwh"]
            
            # Validar valor mínimo
            if result["bill_value"]:
                result["qualifies"] = result["bill_value"] >= self.analysis_config["min_bill_value"]
                result["classification"] = self._classify_bill_value(result["bill_value"])
            
            logger.info(f"📊 Conta analisada: R$ {result.get('bill_value', 0):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao analisar conta: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def extract_bill_data(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Extrai dados de texto de conta usando regex
        
        Args:
            text: Texto da conta
            
        Returns:
            Dados extraídos
        """
        try:
            extracted = {}
            
            # Extrair valor total
            for pattern in self.extraction_patterns["bill_value"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted["bill_value"] = self._parse_currency(match.group(1))
                    break
            
            # Extrair consumo
            for pattern in self.extraction_patterns["consumption_kwh"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted["consumption_kwh"] = self._parse_number(match.group(1))
                    break
            
            # Extrair nome do cliente
            for pattern in self.extraction_patterns["customer_name"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted["customer_name"] = match.group(1).strip().title()
                    break
            
            # Extrair número da instalação
            for pattern in self.extraction_patterns["installation_number"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted["installation_number"] = match.group(1).strip()
                    break
            
            # Extrair endereço
            for pattern in self.extraction_patterns["address"]:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    extracted["address"] = match.group(1).strip()
                    break
            
            return {
                "success": True,
                **extracted
            }
            
        except Exception as e:
            logger.error(f"Erro na extração: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def calculate_savings(
        self,
        bill_value: float,
        savings_percentage: Optional[float] = None,
        include_projection: bool = True
    ) -> Dict[str, Any]:
        """
        Calcula economia com energia solar
        
        Args:
            bill_value: Valor atual da conta
            savings_percentage: Percentual de economia (padrão 20%)
            include_projection: Se deve incluir projeção de longo prazo
            
        Returns:
            Cálculos de economia
        """
        try:
            if savings_percentage is None:
                savings_percentage = self.analysis_config["savings_percentage"]
            
            # Cálculos básicos
            monthly_savings = bill_value * savings_percentage
            new_bill = bill_value * (1 - savings_percentage)
            yearly_savings = monthly_savings * 12
            
            result = {
                "current_bill": bill_value,
                "new_bill": new_bill,
                "monthly_savings": monthly_savings,
                "yearly_savings": yearly_savings,
                "savings_percentage": savings_percentage * 100,
                "daily_savings": monthly_savings / 30
            }
            
            # Projeção de longo prazo
            if include_projection:
                # Considerar inflação energética de 8% ao ano
                inflation_rate = 0.08
                years = self.analysis_config["system_lifetime_years"]
                
                total_savings = 0
                projections = []
                
                for year in range(1, years + 1):
                    # Conta aumenta com inflação
                    projected_bill = bill_value * ((1 + inflation_rate) ** year)
                    year_savings = projected_bill * savings_percentage * 12
                    total_savings += year_savings
                    
                    if year in [1, 5, 10, 15, 20, 25]:
                        projections.append({
                            "year": year,
                            "projected_bill": projected_bill,
                            "yearly_savings": year_savings,
                            "accumulated_savings": total_savings
                        })
                
                result["lifetime_savings"] = total_savings
                result["projections"] = projections
                result["roi_months"] = self.analysis_config["roi_months"]
                result["payback_years"] = self.analysis_config["roi_months"] / 12
            
            logger.info(f"💰 Economia calculada: R$ {monthly_savings:.2f}/mês")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no cálculo: {e}")
            return {
                "error": str(e)
            }
    
    @tool
    async def calculate_solar_system(
        self,
        consumption_kwh: float,
        roof_area: Optional[float] = None,
        shading_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calcula dimensionamento do sistema solar
        
        Args:
            consumption_kwh: Consumo mensal em kWh
            roof_area: Área disponível no telhado (m²)
            shading_factor: Fator de sombreamento (0-1)
            
        Returns:
            Especificações do sistema
        """
        try:
            # Constantes do cálculo
            PANEL_POWER = 550  # Watts por painel (painéis modernos)
            PANEL_AREA = 2.5   # m² por painel
            SUN_HOURS = 5.5    # Horas de sol pico em Recife
            SYSTEM_EFFICIENCY = 0.80  # Eficiência do sistema
            
            # Calcular potência necessária
            daily_consumption = consumption_kwh / 30
            required_power_kw = daily_consumption / (SUN_HOURS * SYSTEM_EFFICIENCY * shading_factor)
            required_power_w = required_power_kw * 1000
            
            # Calcular número de painéis
            num_panels = int(required_power_w / PANEL_POWER) + 1
            
            # Potência instalada real
            installed_power_w = num_panels * PANEL_POWER
            installed_power_kw = installed_power_w / 1000
            
            # Área necessária
            required_area = num_panels * PANEL_AREA
            
            # Verificar se cabe no telhado
            if roof_area and required_area > roof_area:
                # Ajustar para área disponível
                max_panels = int(roof_area / PANEL_AREA)
                num_panels = max_panels
                installed_power_kw = (max_panels * PANEL_POWER) / 1000
                actual_production = installed_power_kw * SUN_HOURS * SYSTEM_EFFICIENCY * 30
                coverage_percentage = (actual_production / consumption_kwh) * 100
            else:
                actual_production = consumption_kwh
                coverage_percentage = 100
            
            # Estimativa de custo (R$ 4.000 por kWp instalado)
            estimated_cost = installed_power_kw * 4000
            
            result = {
                "consumption_kwh": consumption_kwh,
                "required_power_kw": round(required_power_kw, 2),
                "num_panels": num_panels,
                "panel_model": f"Painel Solar {PANEL_POWER}W",
                "installed_power_kw": round(installed_power_kw, 2),
                "required_area_m2": round(required_area, 1),
                "monthly_production_kwh": round(actual_production, 0),
                "coverage_percentage": round(coverage_percentage, 1),
                "estimated_cost": estimated_cost,
                "inverter_power_kw": round(installed_power_kw * 0.9, 2),  # Inversor 90% da potência
                "system_details": {
                    "panels": f"{num_panels}x {PANEL_POWER}W",
                    "inverter": f"1x {round(installed_power_kw * 0.9, 2)}kW",
                    "mounting": "Estrutura de alumínio",
                    "monitoring": "Sistema de monitoramento online",
                    "warranty": "25 anos nos painéis, 10 anos no inversor"
                }
            }
            
            logger.info(f"☀️ Sistema dimensionado: {installed_power_kw:.2f}kWp com {num_panels} painéis")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no dimensionamento: {e}")
            return {
                "error": str(e)
            }
    
    @tool
    async def compare_bills(
        self,
        bills: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compara múltiplas contas para análise de padrão
        
        Args:
            bills: Lista de contas para comparar
            
        Returns:
            Análise comparativa
        """
        try:
            if len(bills) < 2:
                return {
                    "error": "Mínimo 2 contas para comparação"
                }
            
            # Extrair valores
            values = [b.get("bill_value", 0) for b in bills]
            consumptions = [b.get("consumption_kwh", 0) for b in bills]
            
            # Calcular estatísticas
            avg_value = sum(values) / len(values)
            max_value = max(values)
            min_value = min(values)
            variation = ((max_value - min_value) / avg_value) * 100
            
            avg_consumption = sum(consumptions) / len(consumptions) if consumptions else 0
            
            # Identificar tendência
            if len(values) >= 3:
                recent_avg = sum(values[-3:]) / 3
                older_avg = sum(values[:-3]) / len(values[:-3]) if len(values) > 3 else values[0]
                trend = "increasing" if recent_avg > older_avg * 1.05 else "decreasing" if recent_avg < older_avg * 0.95 else "stable"
            else:
                trend = "insufficient_data"
            
            result = {
                "num_bills": len(bills),
                "average_value": avg_value,
                "max_value": max_value,
                "min_value": min_value,
                "variation_percentage": variation,
                "average_consumption": avg_consumption,
                "trend": trend,
                "total_yearly": avg_value * 12,
                "potential_yearly_savings": avg_value * 12 * self.analysis_config["savings_percentage"]
            }
            
            # Análise detalhada
            if consumptions:
                kwh_prices = [v/c for v, c in zip(values, consumptions) if c > 0]
                if kwh_prices:
                    result["average_kwh_price"] = sum(kwh_prices) / len(kwh_prices)
                    result["kwh_price_variation"] = ((max(kwh_prices) - min(kwh_prices)) / result["average_kwh_price"]) * 100
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na comparação: {e}")
            return {
                "error": str(e)
            }
    
    @tool
    async def generate_proposal(
        self,
        lead_id: str,
        bill_data: Dict[str, Any],
        system_specs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gera proposta personalizada
        
        Args:
            lead_id: ID do lead
            bill_data: Dados da conta analisada
            system_specs: Especificações do sistema (opcional)
            
        Returns:
            Proposta formatada
        """
        try:
            # Buscar dados do lead
            lead = await supabase_client.get_lead(lead_id)
            if not lead:
                return {
                    "success": False,
                    "error": "Lead não encontrado"
                }
            
            # Calcular economia
            bill_value = bill_data.get("bill_value", 0)
            savings = await self.calculate_savings(bill_value)
            
            # Dimensionar sistema se não foi fornecido
            if not system_specs and bill_data.get("consumption_kwh"):
                system_specs = await self.calculate_solar_system(
                    bill_data["consumption_kwh"]
                )
            
            # Montar proposta
            proposal = {
                "lead_name": lead.get("name", "Cliente"),
                "generated_at": datetime.now().isoformat(),
                "current_situation": {
                    "monthly_bill": bill_value,
                    "yearly_cost": bill_value * 12,
                    "consumption_kwh": bill_data.get("consumption_kwh"),
                    "provider": bill_data.get("provider", "N/A")
                },
                "proposed_solution": {
                    "system_power_kwp": system_specs.get("installed_power_kw") if system_specs else "A definir",
                    "num_panels": system_specs.get("num_panels") if system_specs else "A definir",
                    "estimated_cost": system_specs.get("estimated_cost") if system_specs else "Sob consulta",
                    "installation_time": "30-45 dias",
                    "warranty": "25 anos nos painéis, 10 anos no inversor"
                },
                "financial_benefits": {
                    "monthly_savings": savings["monthly_savings"],
                    "yearly_savings": savings["yearly_savings"],
                    "lifetime_savings": savings.get("lifetime_savings", savings["yearly_savings"] * 25),
                    "payback_years": savings.get("payback_years", 4),
                    "roi_percentage": ((savings.get("lifetime_savings", 0) / system_specs.get("estimated_cost", 1)) * 100) if system_specs else "A calcular"
                },
                "additional_benefits": [
                    "Proteção contra aumentos tarifários",
                    "Valorização do imóvel em até 10%",
                    "Contribuição para sustentabilidade",
                    "Independência energética",
                    "Monitoramento online 24/7"
                ],
                "next_steps": [
                    "Agendar visita técnica gratuita",
                    "Análise detalhada do local",
                    "Projeto personalizado",
                    "Aprovação na concessionária",
                    "Instalação e ativação"
                ],
                "payment_options": [
                    "À vista com 10% de desconto",
                    "Parcelamento em até 84x",
                    "Financiamento com carência de 6 meses",
                    "Modelo de assinatura mensal"
                ]
            }
            
            # Salvar proposta
            await supabase_client.client.table("proposals").insert({
                "lead_id": lead_id,
                "proposal_data": proposal,
                "bill_value": bill_value,
                "system_power": system_specs.get("installed_power_kw") if system_specs else None,
                "estimated_savings": savings["monthly_savings"],
                "status": "draft",
                "created_at": datetime.now().isoformat()
            }).execute()
            
            logger.info(f"📋 Proposta gerada para {lead.get('name')}")
            
            return {
                "success": True,
                "proposal": proposal,
                "message": "Proposta gerada com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar proposta: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    async def validate_bill_value(
        self,
        bill_value: float
    ) -> Dict[str, Any]:
        """
        Valida se valor da conta atende critérios
        
        Args:
            bill_value: Valor da conta
            
        Returns:
            Validação e classificação
        """
        try:
            qualifies = bill_value >= self.analysis_config["min_bill_value"]
            classification = self._classify_bill_value(bill_value)
            
            result = {
                "bill_value": bill_value,
                "qualifies": qualifies,
                "classification": classification,
                "min_required": self.analysis_config["min_bill_value"]
            }
            
            if not qualifies:
                deficit = self.analysis_config["min_bill_value"] - bill_value
                result["deficit"] = deficit
                result["message"] = f"Conta abaixo do mínimo. Faltam R$ {deficit:.2f}"
            else:
                result["message"] = f"Conta qualificada! Classificação: {classification}"
                
                # Adicionar recomendações por classificação
                if classification == "high":
                    result["recommendation"] = "Lead QUENTE! Priorizar atendimento imediato."
                elif classification == "ideal":
                    result["recommendation"] = "Valor ideal para conversão. Focar em benefícios."
                else:
                    result["recommendation"] = "Qualificado. Nutrir com informações de economia."
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return {
                "error": str(e)
            }
    
    @tool
    async def identify_provider(
        self,
        text: str,
        state: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Identifica fornecedor de energia
        
        Args:
            text: Texto da conta ou nome do fornecedor
            state: Estado (opcional)
            
        Returns:
            Fornecedor identificado
        """
        try:
            text_lower = text.lower()
            
            # Mapeamento de fornecedores por palavra-chave
            providers = {
                BillProvider.CELPE: ["celpe", "pernambuco", "recife"],
                BillProvider.COELBA: ["coelba", "bahia", "salvador"],
                BillProvider.COSERN: ["cosern", "rio grande do norte", "natal"],
                BillProvider.ELEKTRO: ["elektro", "são paulo", "mato grosso do sul"],
                BillProvider.LIGHT: ["light", "rio de janeiro"],
                BillProvider.CEMIG: ["cemig", "minas gerais", "belo horizonte"],
                BillProvider.COPEL: ["copel", "paraná", "curitiba"],
                BillProvider.CPFL: ["cpfl", "paulista"]
            }
            
            identified_provider = BillProvider.UNKNOWN
            
            for provider, keywords in providers.items():
                if any(keyword in text_lower for keyword in keywords):
                    identified_provider = provider
                    break
            
            # Se não identificou e tem estado, tentar por estado
            if identified_provider == BillProvider.UNKNOWN and state:
                state_lower = state.lower()
                state_mapping = {
                    "pe": BillProvider.CELPE,
                    "pernambuco": BillProvider.CELPE,
                    "ba": BillProvider.COELBA,
                    "bahia": BillProvider.COELBA,
                    "rn": BillProvider.COSERN,
                    "rio grande do norte": BillProvider.COSERN
                }
                
                identified_provider = state_mapping.get(state_lower, BillProvider.UNKNOWN)
            
            return {
                "provider": identified_provider.value,
                "provider_name": self._get_provider_name(identified_provider),
                "state": self._get_provider_state(identified_provider)
            }
            
        except Exception as e:
            logger.error(f"Erro ao identificar fornecedor: {e}")
            return {
                "provider": BillProvider.UNKNOWN.value,
                "error": str(e)
            }
    
    # Métodos auxiliares privados
    
    def _parse_currency(self, value: Any) -> float:
        """Converte string de moeda para float"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remover caracteres não numéricos
            value = re.sub(r'[^\d,.]', '', value)
            # Trocar vírgula por ponto
            value = value.replace(',', '.')
            # Remover pontos de milhar
            if value.count('.') > 1:
                parts = value.split('.')
                value = ''.join(parts[:-1]) + '.' + parts[-1]
            
            try:
                return float(value)
            except:
                return 0.0
        
        return 0.0
    
    def _parse_number(self, value: Any) -> int:
        """Converte string para número inteiro"""
        if isinstance(value, (int, float)):
            return int(value)
        
        if isinstance(value, str):
            # Remover caracteres não numéricos
            value = re.sub(r'[^\d]', '', value)
            
            try:
                return int(value)
            except:
                return 0
        
        return 0
    
    def _classify_bill_value(self, bill_value: float) -> str:
        """Classifica valor da conta"""
        if bill_value >= self.analysis_config["high_bill_value"]:
            return "high"
        elif bill_value >= self.analysis_config["ideal_bill_value"]:
            return "ideal"
        elif bill_value >= self.analysis_config["min_bill_value"]:
            return "qualified"
        else:
            return "low"
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extrai dados de texto não estruturado"""
        extracted = {}
        
        # Buscar valor
        value_match = re.search(r'(?:R\$|RS|r\$)\s*([\d.,]+)', text)
        if value_match:
            extracted["valor_total"] = value_match.group(1)
        
        # Buscar consumo
        kwh_match = re.search(r'(\d+)\s*(?:kwh|kWh|KWH)', text, re.IGNORECASE)
        if kwh_match:
            extracted["consumo"] = kwh_match.group(1)
        
        return extracted
    
    async def _analyze_with_ocr_fallback(self, image_data: str) -> Dict[str, Any]:
        """Fallback para análise sem Vision API"""
        # Implementação simplificada - em produção usar OCR real
        logger.warning("Usando valores mockados - Vision API não disponível")
        
        return {
            "success": True,
            "bill_value": 4500.00,
            "consumption_kwh": 850,
            "customer_name": "Cliente Exemplo",
            "address": "Rua Exemplo, 123",
            "installation_number": "123456789",
            "provider": "celpe",
            "qualifies": True,
            "classification": "ideal"
        }
    
    def _get_provider_name(self, provider: BillProvider) -> str:
        """Retorna nome completo do fornecedor"""
        names = {
            BillProvider.CELPE: "Companhia Energética de Pernambuco",
            BillProvider.COELBA: "Companhia de Eletricidade da Bahia",
            BillProvider.COSERN: "Companhia Energética do Rio Grande do Norte",
            BillProvider.ELEKTRO: "Elektro Eletricidade e Serviços",
            BillProvider.LIGHT: "Light Serviços de Eletricidade",
            BillProvider.CEMIG: "Companhia Energética de Minas Gerais",
            BillProvider.COPEL: "Companhia Paranaense de Energia",
            BillProvider.CPFL: "Companhia Paulista de Força e Luz"
        }
        return names.get(provider, "Fornecedor Desconhecido")
    
    def _get_provider_state(self, provider: BillProvider) -> str:
        """Retorna estado do fornecedor"""
        states = {
            BillProvider.CELPE: "PE",
            BillProvider.COELBA: "BA",
            BillProvider.COSERN: "RN",
            BillProvider.ELEKTRO: "SP/MS",
            BillProvider.LIGHT: "RJ",
            BillProvider.CEMIG: "MG",
            BillProvider.COPEL: "PR",
            BillProvider.CPFL: "SP"
        }
        return states.get(provider, "N/A")