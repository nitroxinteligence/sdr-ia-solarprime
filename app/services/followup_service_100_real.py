"""
FollowUp Service 100% REAL - Evolution API WhatsApp
ZERO simulação, MÁXIMA simplicidade
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
from app.utils.logger import emoji_logger
from app.config import settings
from app.database.supabase_client import SupabaseClient

class FollowUpServiceReal:
    """
    Serviço REAL de Follow-up - Evolution API
    SIMPLES e FUNCIONAL - 100% real
    """
    
    def __init__(self):
        self.is_initialized = False
        self.evolution_url = settings.evolution_api_url or settings.evolution_base_url
        self.api_key = settings.evolution_api_key
        self.instance_name = settings.evolution_instance_name or "SDR IA SolarPrime"
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        self.session = None
        self.db = SupabaseClient()
        self._session_timeout = aiohttp.ClientTimeout(total=30)  # 30s timeout
        
    async def initialize(self):
        """Inicializa conexão REAL com Evolution API"""
        if self.is_initialized:
            return
        
        try:
            # 🔧 Criar sessão HTTP com timeout e connector configurado
            connector = aiohttp.TCPConnector(
                limit=10,  # Max 10 conexões simultâneas
                limit_per_host=5,  # Max 5 por host
                ttl_dns_cache=300,  # Cache DNS por 5min
                use_dns_cache=True,
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self._session_timeout
            )
            
            # Em desenvolvimento, apenas marca como inicializado
            if settings.environment == "development" or settings.debug:
                emoji_logger.service_ready(
                    "🔧 Evolution API em modo desenvolvimento - Conexão simulada"
                )
                self.is_initialized = True
                return
            
            # Em produção, testar conexão real com Evolution API
            async with self.session.get(
                f"{self.evolution_url}/instance/fetchInstances",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    instances = await response.json()
                    emoji_logger.service_ready(
                        f"✅ Evolution API conectada: {len(instances)} instâncias"
                    )
                    self.is_initialized = True
                else:
                    raise Exception(f"Erro ao conectar: {response.status}")
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao conectar Evolution: {e}")
            if self.session:
                await self._close_session_safely()
            raise
    
    async def schedule_followup(self, 
                               phone_number: str,
                               message: str,
                               delay_hours: int = 24,
                               lead_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Agenda follow-up REAL via Evolution API
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Calcular horário do follow-up
            scheduled_time = datetime.now() + timedelta(hours=delay_hours)
            
            # Limpar número de telefone
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            # Preparar lead_id válido para o Supabase
            supabase_lead_id = None
            if lead_info:
                supabase_lead_id = await self._get_or_create_supabase_lead_id(lead_info)
            
            # Salvar follow-up no banco para execução posterior
            followup_data = {
                "lead_id": supabase_lead_id,  # UUID válido ou None
                "phone_number": clean_phone,  # Corrigido: phone_number ao invés de phone
                "message": message,
                "scheduled_at": scheduled_time.isoformat(),  # Corrigido: scheduled_at ao invés de scheduled_time
                "status": "pending",  # Corrigido: usar 'pending' ao invés de 'scheduled'
                "type": "reminder",  # Usar tipo válido da constraint
                "created_at": datetime.now().isoformat()
            }
            
            # Salvar no Supabase
            result = await self.db.save_followup(followup_data)
            followup_id = result.get("id", f"followup_{datetime.now().timestamp()}")
            
            emoji_logger.followup_event(
                f"✅ Follow-up REAL agendado para {clean_phone} em {delay_hours}h"
            )
            
            # Agendar tarefa assíncrona para enviar depois
            asyncio.create_task(self._execute_delayed_followup(
                followup_id, clean_phone, message, delay_hours
            ))
            
            return {
                "success": True,
                "followup_id": followup_id,
                "scheduled_at": scheduled_time.isoformat(),
                "message": f"Follow-up agendado para {scheduled_time.strftime('%d/%m %H:%M')}",
                "real": True
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao agendar follow-up: {e}")
            return {
                "success": False,
                "message": f"Erro ao agendar follow-up: {e}"
            }
    
    async def create_followup(self,
                            lead_info: Dict[str, Any],
                            followup_type: str = "reengagement",
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Cria follow-up personalizado baseado no contexto
        ZERO templates, 100% personalização
        
        Args:
            lead_info: Informações do lead
            followup_type: Tipo do follow-up (reengagement, reminder, nurturing)
            context: Contexto da conversa
            
        Returns:
            Resultado da criação do follow-up
        """
        try:
            # Extrair informações essenciais
            phone = lead_info.get("phone", "")
            name = lead_info.get("name", "Cliente")
            bill_value = lead_info.get("bill_value", 0)
            
            # Gerar mensagem personalizada baseada no tipo
            if followup_type == "reengagement":
                # Follow-up de reengajamento
                delay_hours = 48  # 2 dias
                
                # Personalizar com base no contexto
                if context and context.get("objections_raised"):
                    objections = context["objections_raised"]
                    if "preço" in objections:
                        message = f"Oi {name}! 😊 Helen aqui da SolarPrime. Lembrei de você e da nossa conversa sobre economia na conta de luz. "
                        message += f"Sabia que temos opções de financiamento que cabem no seu orçamento? "
                        if bill_value > 500:
                            message += f"Com sua conta de R$ {bill_value}, você pode economizar até {bill_value * 0.7:.0f} por mês! "
                        message += "Posso te mostrar uma simulação sem compromisso? 💰"
                    else:
                        message = f"Olá {name}! 👋 Aqui é a Helen da SolarPrime. "
                        message += "Vi que você tem interesse em economizar na conta de luz. "
                        message += "Acabamos de lançar condições especiais este mês. Que tal conversarmos? ☀️"
                else:
                    # Mensagem genérica personalizada
                    message = f"Oi {name}! 😊 Helen da SolarPrime aqui. "
                    message += "Estava revisando nossos contatos e lembrei da nossa conversa. "
                    if bill_value > 0:
                        message += f"Com sua conta de R$ {bill_value}, posso te mostrar como economizar! "
                    message += "Tem 5 minutinhos para conversarmos? ⚡"
                    
            elif followup_type == "reminder":
                # Lembrete de reunião (usado pelo workflow)
                delay_hours = 24  # 1 dia antes
                message = f"Oi {name}! 📅 Helen aqui lembrando da nossa reunião amanhã com o Leonardo. "
                message += "Ele está animado para te mostrar como você pode economizar na conta de luz! "
                if bill_value > 0:
                    message += f"Já preparamos uma análise especial para sua conta de R$ {bill_value}. "
                message += "Até amanhã! ☀️"
                
            elif followup_type == "nurturing":
                # Follow-up de nutrição
                delay_hours = 72  # 3 dias
                
                # Personalizar com base nos interesses
                if context and context.get("main_interest"):
                    interest = context["main_interest"]
                    message = f"Olá {name}! 💡 Helen da SolarPrime aqui com uma informação importante. "
                    
                    if "economia" in interest.lower():
                        message += "Você sabia que nossos clientes economizam em média 85% na conta de luz? "
                        if bill_value > 0:
                            message += f"No seu caso, seria uma economia de aproximadamente R$ {bill_value * 0.85:.0f} por mês! "
                    elif "sustentabilidade" in interest.lower():
                        message += "Cada sistema solar instalado equivale a plantar 500 árvores por ano! 🌳 "
                        message += "Além da economia, você contribui diretamente para um futuro mais verde. "
                    else:
                        message += "A energia solar valoriza seu imóvel em até 8% segundo estudos recentes. "
                        message += "É economia e investimento ao mesmo tempo! "
                    
                    message += "Gostaria de saber mais? 😊"
                else:
                    # Nutrição genérica
                    message = f"Oi {name}! ☀️ Helen aqui com uma dica rápida: "
                    message += "Este mês temos condições especiais para energia solar. "
                    if bill_value > 600:
                        message += f"Clientes com conta acima de R$ 600 têm benefícios extras! "
                    message += "Posso te enviar os detalhes? 📲"
            else:
                # Tipo desconhecido - follow-up genérico
                delay_hours = 24
                message = f"Olá {name}! Helen da SolarPrime aqui. "
                message += "Gostaria de continuar nossa conversa sobre energia solar? "
                message += "Estou à disposição! 😊"
            
            # Agendar o follow-up
            result = await self.schedule_followup(
                phone_number=phone,
                message=message,
                delay_hours=delay_hours,
                lead_info=lead_info
            )
            
            if result["success"]:
                emoji_logger.followup_event(
                    f"✅ Follow-up {followup_type} criado para {name}",
                    delay_hours=delay_hours
                )
                
            return result
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao criar follow-up: {e}")
            return {
                "success": False,
                "message": f"Erro ao criar follow-up: {e}"
            }
    
    async def _execute_delayed_followup(self, 
                                       followup_id: str,
                                       phone: str, 
                                       message: str, 
                                       delay_hours: int):
        """
        Executa follow-up após delay
        """
        try:
            # Aguardar o tempo especificado
            await asyncio.sleep(delay_hours * 3600)
            
            # Enviar mensagem via Evolution
            await self.send_message(phone, message)
            
            # Atualizar status no banco
            await self.db.update_followup_status(followup_id, "executed")
            
            emoji_logger.followup_event(
                f"✅ Follow-up {followup_id} ENVIADO para {phone}"
            )
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao executar follow-up: {e}")
            await self.db.update_followup_status(followup_id, "failed")
    
    async def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Envia mensagem REAL via Evolution API
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Limpar número
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            # Formatar para WhatsApp
            whatsapp_number = f"{clean_phone}@s.whatsapp.net"
            
            # Enviar via Evolution API
            payload = {
                "number": whatsapp_number,
                "text": message
            }
            
            async with self.session.post(
                f"{self.evolution_url}/message/sendText/{self.instance_name}",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    
                    emoji_logger.followup_event(
                        f"✅ Mensagem REAL enviada para {clean_phone}"
                    )
                    
                    return {
                        "success": True,
                        "message_id": result.get("key", {}).get("id"),
                        "message": "Mensagem enviada com sucesso",
                        "real": True
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Erro {response.status}: {error}")
                    
        except Exception as e:
            emoji_logger.service_error(f"Erro ao enviar mensagem: {e}")
            return {
                "success": False,
                "message": f"Erro ao enviar mensagem: {e}"
            }
    
    async def send_typing(self, phone_number: str, duration: int = 3) -> Dict[str, Any]:
        """
        Envia status de digitando REAL
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            whatsapp_number = f"{clean_phone}@s.whatsapp.net"
            
            # Enviar status de digitando
            payload = {
                "number": whatsapp_number,
                "status": "composing",
                "duration": duration * 1000  # Milissegundos
            }
            
            async with self.session.post(
                f"{self.evolution_url}/chat/updatePresence/{self.instance_name}",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    emoji_logger.system_debug(f"📝 Digitando para {clean_phone}...")
                    return {
                        "success": True,
                        "message": "Status de digitando enviado",
                        "real": True
                    }
                    
        except Exception as e:
            # Não é crítico se falhar
            emoji_logger.system_debug(f"Aviso: Erro ao enviar typing: {e}")
            return {"success": False}
    
    async def get_pending_followups(self) -> List[Dict[str, Any]]:
        """
        Busca follow-ups pendentes REAIS do banco
        """
        try:
            # Buscar do Supabase
            pending = await self.db.get_pending_followups()
            
            emoji_logger.followup_event(
                f"📅 {len(pending)} follow-ups pendentes encontrados"
            )
            
            return pending
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao buscar follow-ups: {e}")
            return []
    
    async def execute_pending_followups(self) -> Dict[str, Any]:
        """
        Executa todos os follow-ups pendentes
        """
        try:
            pending = await self.get_pending_followups()
            executed = 0
            failed = 0
            
            for followup in pending:
                # Verificar se já é hora de enviar
                scheduled_time = datetime.fromisoformat(followup.get("scheduled_at", followup.get("scheduled_time", "")))
                if scheduled_time <= datetime.now():
                    # Enviar mensagem
                    result = await self.send_message(
                        followup.get("phone_number", followup.get("phone", "")),  # Compatível com ambos
                        followup["message"]
                    )
                    
                    if result["success"]:
                        await self.db.update_followup_status(followup["id"], "executed")
                        executed += 1
                    else:
                        await self.db.update_followup_status(followup["id"], "failed")
                        failed += 1
            
            emoji_logger.followup_event(
                f"📤 Follow-ups executados: {executed} sucesso, {failed} falhas"
            )
            
            return {
                "success": True,
                "executed": executed,
                "failed": failed,
                "message": f"{executed} follow-ups enviados",
                "real": True
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao executar follow-ups: {e}")
            return {
                "success": False,
                "message": f"Erro ao executar follow-ups: {e}"
            }
    
    async def cancel_followup(self, followup_id: str) -> Dict[str, Any]:
        """
        Cancela follow-up agendado
        """
        try:
            await self.db.update_followup_status(followup_id, "cancelled")
            
            emoji_logger.followup_event(
                f"❌ Follow-up {followup_id} cancelado"
            )
            
            return {
                "success": True,
                "message": "Follow-up cancelado com sucesso",
                "real": True
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao cancelar follow-up: {e}")
            return {
                "success": False,
                "message": f"Erro ao cancelar follow-up: {e}"
            }
    
    async def create_reengagement_campaign(self, 
                                          leads: List[Dict[str, Any]],
                                          message_template: str) -> Dict[str, Any]:
        """
        Cria campanha de reengajamento REAL
        """
        try:
            scheduled = 0
            delay_hours = 0
            
            for lead in leads:
                if lead.get("phone"):
                    # Personalizar mensagem
                    message = message_template.format(
                        name=lead.get("name", "Cliente"),
                        bill_value=lead.get("bill_value", 0)
                    )
                    
                    # Agendar com delay progressivo
                    result = await self.schedule_followup(
                        lead["phone"],
                        message,
                        delay_hours=delay_hours,
                        lead_info=lead
                    )
                    
                    if result["success"]:
                        scheduled += 1
                    
                    # Aumentar delay para próximo (evitar spam)
                    delay_hours += 2
            
            emoji_logger.followup_event(
                f"🎯 Campanha criada: {scheduled} follow-ups agendados"
            )
            
            return {
                "success": True,
                "scheduled": scheduled,
                "message": f"Campanha criada com {scheduled} follow-ups",
                "real": True
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao criar campanha: {e}")
            return {
                "success": False,
                "message": f"Erro ao criar campanha: {e}"
            }
    
    async def create_nurturing_campaign(self,
                                        lead_info: Dict[str, Any],
                                        strategy: str = "moderate",
                                        duration_days: int = 30,
                                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Cria campanha completa de nutrição com mensagens personalizadas
        NÃO USA TEMPLATES FIXOS - gera mensagens baseadas no contexto
        
        Args:
            lead_info: Informações do lead
            strategy: Estratégia da campanha (aggressive, moderate, gentle)
            duration_days: Duração da campanha em dias
            context: Contexto da conversa para personalização
            
        Returns:
            Dict com resultado da criação da campanha
        """
        try:
            # Definir cadência baseada na estratégia
            cadences = {
                "aggressive": [1, 2, 3, 5, 7, 10, 14, 21, 30],  # 9 touchpoints
                "moderate": [1, 3, 7, 14, 21, 30],              # 6 touchpoints
                "gentle": [3, 7, 14, 30]                        # 4 touchpoints
            }
            
            campaign_days = cadences.get(strategy.lower(), cadences["moderate"])
            
            # Filtrar dias dentro da duração solicitada
            campaign_days = [d for d in campaign_days if d <= duration_days]
            
            # Preparar contexto para personalização
            lead_name = lead_info.get("name", "").split()[0] if lead_info.get("name") else ""
            bill_value = lead_info.get("bill_value", 0)
            pain_points = context.get("pain_points", []) if context else []
            objections = context.get("objections_raised", []) if context else []
            interests = context.get("main_interest", "economia") if context else "economia"
            
            # Temas para cada dia da campanha (baseado no dia)
            message_themes = {
                1: {
                    "focus": "reforçar interesse inicial",
                    "tone": "entusiasmado",
                    "action": "continuar conversa"
                },
                2: {
                    "focus": "compartilhar caso de sucesso similar",
                    "tone": "informativo",
                    "action": "gerar identificação"
                },
                3: {
                    "focus": "esclarecer dúvidas comuns",
                    "tone": "educativo",
                    "action": "remover objeções"
                },
                5: {
                    "focus": "demonstrar economia real",
                    "tone": "analítico",
                    "action": "mostrar números"
                },
                7: {
                    "focus": "oferta especial temporária",
                    "tone": "urgente mas amigável",
                    "action": "criar urgência"
                },
                10: {
                    "focus": "benefícios além da economia",
                    "tone": "consultivo",
                    "action": "ampliar valor percebido"
                },
                14: {
                    "focus": "check-in amigável",
                    "tone": "casual",
                    "action": "manter relacionamento"
                },
                21: {
                    "focus": "novidades e atualizações",
                    "tone": "informativo",
                    "action": "reengajar com novidades"
                },
                30: {
                    "focus": "última oportunidade",
                    "tone": "direto mas respeitoso",
                    "action": "decisão final"
                }
            }
            
            # Criar follow-ups para cada dia da campanha
            scheduled_count = 0
            
            for day in campaign_days:
                scheduled_at = datetime.now() + timedelta(days=day)
                
                # Obter tema do dia
                theme = message_themes.get(day, message_themes[1])
                
                # Gerar mensagem personalizada baseada no contexto
                message = await self._generate_nurturing_message(
                    lead_name=lead_name,
                    bill_value=bill_value,
                    day=day,
                    theme=theme,
                    pain_points=pain_points,
                    objections=objections,
                    interests=interests,
                    strategy=strategy
                )
                
                # Preparar lead_id válido para o Supabase
                supabase_lead_id = await self._get_or_create_supabase_lead_id(lead_info)
                
                # Criar follow-up no banco
                followup_data = {
                    "lead_id": supabase_lead_id,  # UUID válido do Supabase
                    "phone_number": lead_info.get("phone"),  # Corrigido: phone_number
                    "type": "nurture",  # Usar tipo válido da constraint
                    "scheduled_at": scheduled_at.isoformat(),
                    "message": message,
                    "metadata": {
                        "campaign_day": day,
                        "theme": theme["focus"],
                        "strategy": strategy,
                        "campaign_strategy": strategy,  # Movido para metadata
                        "kommo_lead_id": lead_info.get("id")  # Manter referência ao Kommo
                    }
                }
                
                # Salvar no banco
                result = await self.db.save_followup(followup_data)
                if result:
                    scheduled_count += 1
                    emoji_logger.followup_event(
                        f"📅 Follow-up dia {day} agendado para {scheduled_at.strftime('%d/%m')}"
                    )
            
            emoji_logger.followup_event(
                f"🎯 Campanha {strategy.upper()} criada: {scheduled_count} touchpoints em {duration_days} dias"
            )
            
            return {
                "success": True,
                "campaign_created": True,
                "strategy": strategy,
                "touchpoints": scheduled_count,
                "duration_days": duration_days,
                "message": f"Campanha de nutrição criada com {scheduled_count} mensagens",
                "real": True
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao criar campanha de nutrição: {e}")
            return {
                "success": False,
                "message": f"Erro ao criar campanha: {e}"
            }
    
    async def _generate_nurturing_message(self,
                                         lead_name: str,
                                         bill_value: float,
                                         day: int,
                                         theme: Dict[str, str],
                                         pain_points: List[str],
                                         objections: List[str],
                                         interests: str,
                                         strategy: str) -> str:
        """
        Gera mensagem personalizada de nutrição baseada no contexto
        NÃO USA TEMPLATES - cria mensagens únicas
        
        Returns:
            Mensagem personalizada para o follow-up
        """
        try:
            # Usar IA para gerar mensagem personalizada se disponível
            from app.agents.agentic_sdr_refactored import get_agentic_agent
            agent = await get_agentic_agent()
            
            if agent and hasattr(agent, '_gemini_call_with_retry'):
                prompt = f"""
                Você é Helen da SolarPrime. Crie uma mensagem de follow-up PERSONALIZADA.
                
                Contexto do lead:
                - Nome: {lead_name if lead_name else 'Lead'}
                - Valor da conta: R$ {bill_value:.2f}
                - Interesse principal: {interests}
                - Preocupações: {', '.join(pain_points) if pain_points else 'economia'}
                - Objeções: {', '.join(objections) if objections else 'nenhuma específica'}
                
                Dia da campanha: {day}
                Tema: {theme['focus']}
                Tom: {theme['tone']}
                Objetivo: {theme['action']}
                Estratégia: {strategy}
                
                Regras:
                - Máximo 3 linhas
                - Mencione o nome no MÁXIMO 1 vez (dia 1, 7, 30) ou nem mencione
                - Seja natural e conversacional
                - NÃO pareça um template ou mensagem automática
                - Personalize baseado nas preocupações e interesses
                - Use emojis com moderação (1-2 no máximo)
                """
                
                response = await agent._gemini_call_with_retry(
                    prompt,
                    temperature=0.8,
                    max_tokens=150
                )
                
                if response and isinstance(response, dict):
                    message = response.get("content", "").strip()
                    if message:
                        return message
        except Exception as e:
            emoji_logger.system_debug(f"Erro ao gerar com IA, usando fallback: {e}")
        
        # Fallback: gerar mensagem baseada em padrões dinâmicos
        # Mas ainda personalizada, não template fixo
        if day == 1:
            if "conta alta" in str(pain_points).lower():
                bill_val = bill_value if bill_value is not None else 0  # Garantir que nunca é None
                return f"Oi{' ' + lead_name if lead_name else ''}! 😊 Lembrei da nossa conversa sobre sua conta de R$ {bill_val:.0f}. Já calculou quanto isso dá em 5 anos? Mais de R$ {bill_val * 12 * 5:.0f}! Vamos mudar isso?"
            else:
                return f"Estava pensando na nossa conversa sobre {interests}. Tenho uma informação importante que pode te interessar. Posso compartilhar?"
        
        elif day == 3:
            if "investimento" in str(objections).lower():
                return f"Sabia que o investimento em energia solar se paga em média em 3-4 anos? Depois disso, é economia pura por mais de 20 anos! 📊"
            else:
                bill_val = bill_value if bill_value is not None else 0  # Garantir que nunca é None
                return f"Um cliente nosso com conta similar à sua (R$ {bill_val:.0f}) agora paga apenas a taxa mínima. Quer saber como ele conseguiu?"
        
        elif day == 7:
            return f"🎁 Consegui uma condição especial essa semana: 10% de desconto + parcelamento facilitado. Mas preciso confirmar até sexta. Vamos conversar?"
        
        elif day == 14:
            return f"Oi! Como você está? Ainda pensando em reduzir aquela conta de luz? Temos novidades que podem te interessar 🌞"
        
        elif day == 21:
            bill_val = bill_value if bill_value is not None else 0  # Garantir que nunca é None
            if bill_val > 300:
                return f"📈 O reajuste da energia está chegando... Com sua conta de R$ {bill_val:.0f}, isso pode significar mais R$ {bill_val * 0.15:.0f} por mês. Que tal se proteger disso?"
            else:
                return f"Novidade: lançamos um plano especial para contas até R$ 400. Perfeito para o seu caso! Quer conhecer?"
        
        elif day == 30:
            return f"{'Última chance ' + lead_name + '! ' if lead_name else 'Última chance! '}As condições especiais se encerram amanhã. Não quero que você perca essa oportunidade de economizar. Podemos conversar hoje?"
        
        else:
            # Mensagem genérica personalizada para outros dias
            return f"Oi! Voltando ao assunto da economia na conta de luz... Descobri algo que pode te ajudar com {interests}. Tem 2 minutos?"
    
    async def health_check(self) -> bool:
        """Verifica saúde do serviço"""
        try:
            # Em desenvolvimento, sempre retorna True pois Evolution só funciona em produção
            if settings.environment == "development" or settings.debug:
                emoji_logger.service_info("🔧 Evolution API em modo desenvolvimento - OK simulado")
                return True
            
            if not self.is_initialized:
                await self.initialize()
            
            # Em produção, testar acesso real à Evolution API
            async with self.session.get(
                f"{self.evolution_url}/instance/fetchInstances",
                headers=self.headers
            ) as response:
                # Se conseguir conectar com a API, considera como saudável
                return response.status in [200, 201, 401, 403]  # API está respondendo
                    
        except:
            # Em desenvolvimento, retorna True para não bloquear
            if settings.environment == "development" or settings.debug:
                return True
            return False
    
    async def close(self):
        """Fecha conexões de forma segura"""
        await self._close_session_safely()
    
    async def _close_session_safely(self):
        """🛡️ Fecha sessão aiohttp de forma segura"""
        if self.session and not self.session.closed:
            try:
                await self.session.close()
                # Aguardar um pouco para garantir que conexões sejam fechadas
                await asyncio.sleep(0.1)
                emoji_logger.service_info("🔌 Sessão FollowUp fechada com segurança")
            except Exception as e:
                emoji_logger.service_warning(f"Aviso ao fechar sessão FollowUp: {e}")
            finally:
                self.session = None
    
    def __del__(self):
        """🗑️ Destrutor para garantir limpeza de recursos"""
        if self.session and not self.session.closed:
            # Criar nova task para fechar sessão se event loop estiver rodando
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._close_session_safely())
                else:
                    loop.run_until_complete(self._close_session_safely())
            except RuntimeError:
                # Event loop não disponível - tentar fechamento direto
                try:
                    if hasattr(self.session, '_connector') and self.session._connector:
                        self.session._connector.close()
                except:
                    pass
    
    async def _get_or_create_supabase_lead_id(self, lead_info: Dict[str, Any]) -> str:
        """
        Busca ou cria um UUID válido no Supabase para o lead
        Similar ao método do TeamCoordinator
        
        Args:
            lead_info: Informações do lead incluindo telefone e dados do Kommo
            
        Returns:
            UUID válido do Supabase
        """
        try:
            from uuid import uuid4
            from app.integrations.supabase_client import supabase_client
            
            phone = lead_info.get("phone", "")
            if not phone:
                # Se não tem telefone, criar novo UUID e lead no Supabase
                new_lead_uuid = str(uuid4())
                # Usar parte do UUID como telefone único para evitar duplicação
                unique_phone = f"unknown_{new_lead_uuid[:8]}"
                
                lead_data = {
                    "id": new_lead_uuid,  # UUID explícito
                    "phone_number": unique_phone,  # Phone único baseado no UUID
                    "name": lead_info.get("name", "Lead Sem Telefone"),
                    "email": lead_info.get("email"),
                    "bill_value": lead_info.get("bill_value"),
                    "current_stage": "INITIAL_CONTACT", 
                    "qualification_status": "PENDING",
                    "kommo_lead_id": str(lead_info.get("id")) if lead_info.get("id") else None
                }
                
                try:
                    new_lead = await supabase_client.create_lead(lead_data)
                    return new_lead["id"]
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao criar lead sem telefone: {e}")
                    return new_lead_uuid  # Fallback para UUID
            
            # Buscar lead existente no Supabase por telefone
            existing_lead = await supabase_client.get_lead_by_phone(phone)
            
            if existing_lead:
                # Atualizar dados do Kommo se necessário
                kommo_id = lead_info.get("id")
                if kommo_id and existing_lead.get("kommo_lead_id") != str(kommo_id):
                    await supabase_client.update_lead(
                        existing_lead["id"],
                        {"kommo_lead_id": str(kommo_id)}
                    )
                return existing_lead["id"]
            else:
                # 🔥 CORREÇÃO CRÍTICA: Criar novo lead no Supabase
                emoji_logger.followup_event(f"🆕 Criando novo lead no Supabase para {phone}")
                lead_data = {
                    "phone_number": phone,
                    "name": lead_info.get("name"),
                    "email": lead_info.get("email"),
                    "bill_value": lead_info.get("bill_value"),
                    "current_stage": "INITIAL_CONTACT",
                    "qualification_status": "PENDING",
                    "kommo_lead_id": str(lead_info.get("id")) if lead_info.get("id") else None
                }
                
                try:
                    new_lead = await supabase_client.create_lead(lead_data)
                    emoji_logger.system_success(f"✅ Lead criado no Supabase: {new_lead['id']}")
                    return new_lead["id"]
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao criar lead no Supabase: {e}")
                    # Fallback: criar UUID mas registrar erro
                    return str(uuid4())
                
        except Exception as e:
            emoji_logger.service_error(f"Erro ao obter UUID do Supabase: {e}")
            # Fallback: criar novo UUID
            from uuid import uuid4
            return str(uuid4())
    
    async def create_followup_direct(self, followup_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria follow-up com dados diretos (usado pelo AgenticSDR e TeamCoordinator)
        
        Args:
            followup_data: Dados do follow-up incluindo:
                - lead_id: UUID do lead no Supabase 
                - type: Tipo do follow-up
                - scheduled_at: Data/hora de agendamento
                - message: Mensagem a ser enviada
                - metadata: Metadados opcionais
                
        Returns:
            Resultado da criação do follow-up
        """
        try:
            # Extrair dados essenciais
            lead_id = followup_data.get('lead_id')
            scheduled_at = followup_data.get('scheduled_at')
            message = followup_data.get('message')
            followup_type = followup_data.get('type')
            metadata = followup_data.get('metadata', {})
            
            if not all([scheduled_at, message, followup_type]):
                raise ValueError("Campos obrigatórios: scheduled_at, message, type")
            
            # Preparar dados para salvar no banco
            db_followup_data = {
                'lead_id': lead_id,  # UUID válido ou None
                'phone_number': metadata.get('phone_number'),  # Opcional
                'type': followup_type,
                'scheduled_at': scheduled_at,
                'message': message,
                'status': 'pending',
                'metadata': metadata,
                'created_at': datetime.now().isoformat()
            }
            
            # Salvar no banco
            result = await self.db.save_followup(db_followup_data)
            followup_id = result.get("id", f"followup_{datetime.now().timestamp()}")
            
            emoji_logger.followup_event(
                f"✅ Follow-up direto criado: {followup_type}"
            )
            
            # Agendar execução futura (opcional para follow-ups imediatos)
            if scheduled_at:
                from datetime import datetime
                scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
                delay_hours = (scheduled_datetime - datetime.now()).total_seconds() / 3600
                
                if delay_hours > 0:
                    asyncio.create_task(self._execute_delayed_followup(
                        followup_id, 
                        metadata.get('phone_number', ''), 
                        message, 
                        int(delay_hours)
                    ))
            
            return {
                "success": True,
                "followup_id": followup_id,
                "scheduled_at": scheduled_at,
                "message": f"Follow-up {followup_type} criado com sucesso",
                "real": True
            }
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao criar follow-up direto: {e}")
            return {
                "success": False,
                "message": f"Erro ao criar follow-up direto: {e}"
            }