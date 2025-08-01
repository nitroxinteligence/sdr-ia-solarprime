"""
Test data fixtures for SDR Agent end-to-end tests.

This module contains sample data for testing various scenarios including
WhatsApp messages, media processing, lead qualification stages, and expected responses.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any
from uuid import uuid4


class TestData:
    """Container for test data fixtures"""
    
    # Sample WhatsApp instance
    INSTANCE_NAME = "test-instance"
    
    # Test phone numbers
    TEST_PHONES = {
        "lead_1": "5511999887766",
        "lead_2": "5511888776655", 
        "lead_3": "5521987654321",
        "qualified_lead": "5511999999999",
        "disqualified_lead": "5511888888888"
    }
    
    # Sample WhatsApp webhook payloads
    WEBHOOK_PAYLOADS = {
        "text_message": {
            "event": "messages.upsert",
            "instance": {
                "instanceName": INSTANCE_NAME,
                "status": "active"
            },
            "data": {
                "key": {
                    "remoteJid": f"{TEST_PHONES['lead_1']}@s.whatsapp.net",
                    "fromMe": False,
                    "id": "BAE5F1A2B3C4D5E6"
                },
                "message": {
                    "conversation": "Olá, gostaria de saber mais sobre energia solar",
                    "messageTimestamp": str(int(datetime.now(timezone.utc).timestamp()))
                },
                "messageType": "conversation",
                "pushName": "João Silva",
                "source": "web"
            }
        },
        "image_message": {
            "event": "messages.upsert",
            "instance": {
                "instanceName": INSTANCE_NAME,
                "status": "active"
            },
            "data": {
                "key": {
                    "remoteJid": f"{TEST_PHONES['lead_1']}@s.whatsapp.net",
                    "fromMe": False,
                    "id": "BAE5F1A2B3C4D5E7"
                },
                "message": {
                    "imageMessage": {
                        "url": "https://example.com/test-image.jpg",
                        "mimetype": "image/jpeg",
                        "caption": "Aqui está minha conta de luz",
                        "fileLength": "123456",
                        "height": 1024,
                        "width": 768
                    },
                    "messageTimestamp": str(int(datetime.now(timezone.utc).timestamp()))
                },
                "messageType": "imageMessage",
                "pushName": "João Silva",
                "source": "web"
            }
        },
        "audio_message": {
            "event": "messages.upsert",
            "instance": {
                "instanceName": INSTANCE_NAME,
                "status": "active"
            },
            "data": {
                "key": {
                    "remoteJid": f"{TEST_PHONES['lead_2']}@s.whatsapp.net",
                    "fromMe": False,
                    "id": "BAE5F1A2B3C4D5E8"
                },
                "message": {
                    "audioMessage": {
                        "url": "https://example.com/test-audio.ogg",
                        "mimetype": "audio/ogg; codecs=opus",
                        "seconds": 15,
                        "ptt": True
                    },
                    "messageTimestamp": str(int(datetime.now(timezone.utc).timestamp()))
                },
                "messageType": "audioMessage",
                "pushName": "Maria Santos",
                "source": "mobile"
            }
        },
        "document_message": {
            "event": "messages.upsert",
            "instance": {
                "instanceName": INSTANCE_NAME,
                "status": "active"
            },
            "data": {
                "key": {
                    "remoteJid": f"{TEST_PHONES['lead_3']}@s.whatsapp.net",
                    "fromMe": False,
                    "id": "BAE5F1A2B3C4D5E9"
                },
                "message": {
                    "documentMessage": {
                        "url": "https://example.com/test-document.pdf",
                        "mimetype": "application/pdf",
                        "title": "Conta_Luz_Dezembro.pdf",
                        "fileLength": "543210",
                        "pageCount": 2
                    },
                    "messageTimestamp": str(int(datetime.now(timezone.utc).timestamp()))
                },
                "messageType": "documentMessage",
                "pushName": "Carlos Oliveira",
                "source": "web"
            }
        }
    }
    
    # Sample lead data at different stages
    LEAD_DATA = {
        "new_lead": {
            "phone_number": TEST_PHONES["lead_1"],
            "name": None,
            "current_stage": "INITIAL_CONTACT",
            "qualification_score": 0,
            "interested": True
        },
        "identified_lead": {
            "phone_number": TEST_PHONES["lead_2"],
            "name": "Maria Santos",
            "current_stage": "IDENTIFYING",
            "qualification_score": 10,
            "interested": True
        },
        "qualifying_lead": {
            "phone_number": TEST_PHONES["lead_3"],
            "name": "Carlos Oliveira",
            "bill_value": 450.0,
            "property_type": "casa",
            "current_stage": "QUALIFYING",
            "qualification_score": 40,
            "interested": True
        },
        "qualified_lead": {
            "phone_number": TEST_PHONES["qualified_lead"],
            "name": "Ana Costa",
            "email": "ana.costa@example.com",
            "bill_value": 850.0,
            "property_type": "casa",
            "address": "Rua das Flores, 123",
            "current_stage": "QUALIFIED",
            "qualification_score": 85,
            "interested": True,
            "kommo_lead_id": "12345"
        },
        "disqualified_lead": {
            "phone_number": TEST_PHONES["disqualified_lead"],
            "name": "Pedro Lima",
            "bill_value": 150.0,
            "property_type": "apartamento",
            "current_stage": "NOT_INTERESTED",
            "qualification_score": 0,
            "interested": False
        }
    }
    
    # Sample media processing results
    MEDIA_PROCESSING_RESULTS = {
        "bill_image_success": {
            "success": True,
            "data": {
                "bill_value": 567.89,
                "consumption_kwh": 789,
                "provider": "CEMIG",
                "month": "12/2024",
                "customer_name": "JOAO SILVA"
            },
            "raw_text": "CEMIG CONTA DE LUZ\nVALOR: R$ 567,89\nCONSUMO: 789 kWh",
            "confidence": 0.95
        },
        "bill_pdf_success": {
            "success": True,
            "data": {
                "bill_value": 1234.56,
                "consumption_kwh": 1523,
                "provider": "LIGHT",
                "month": "12/2024",
                "customer_name": "CARLOS OLIVEIRA"
            },
            "raw_text": "LIGHT S.A.\nFATURA DE ENERGIA\nTOTAL A PAGAR: R$ 1.234,56",
            "confidence": 0.92
        },
        "audio_transcription": {
            "success": True,
            "data": {
                "transcription": "Olá, meu nome é Maria Santos. Gostaria de saber mais sobre a economia que vocês prometem. Minha conta vem muito alta, cerca de 600 reais por mês.",
                "duration_seconds": 15,
                "language": "pt-BR"
            },
            "confidence": 0.88
        },
        "processing_error": {
            "success": False,
            "error": "Failed to process media: Invalid file format",
            "data": None
        }
    }
    
    # Expected responses for each qualification stage
    EXPECTED_RESPONSES = {
        "initial_contact": {
            "keywords": ["Olá", "Helen Vieira", "SolarPrime", "energia solar", "economia"],
            "intent": "greeting_and_introduction",
            "emotional_state": "entusiasmada"
        },
        "identification": {
            "keywords": ["prazer", "conhecer", "posso chamá-lo"],
            "intent": "request_name",
            "emotional_state": "neutral"
        },
        "qualification": {
            "keywords": ["conta de luz", "valor médio", "economia"],
            "intent": "gather_bill_info",
            "emotional_state": "empática"
        },
        "discovery": {
            "keywords": ["solução", "benefício", "economia garantida"],
            "intent": "present_solutions",
            "emotional_state": "entusiasmada"
        },
        "objection_handling": {
            "keywords": ["entendo", "preocupação", "garantia", "clientes satisfeitos"],
            "intent": "handle_objection",
            "emotional_state": "empática"
        },
        "scheduling": {
            "keywords": ["agendar", "reunião", "disponibilidade", "horário"],
            "intent": "schedule_meeting",
            "emotional_state": "determinada"
        }
    }
    
    # Objection scenarios
    OBJECTION_SCENARIOS = {
        "price_concern": {
            "message": "Achei muito caro, não tenho condições",
            "expected_keywords": ["substitui", "mesma conta", "garantida", "25 anos"]
        },
        "trust_issue": {
            "message": "Não confio nessas empresas de energia solar",
            "expected_keywords": ["9,64", "Reclame Aqui", "23 mil clientes", "depoimentos"]
        },
        "low_bill": {
            "message": "Minha conta é só 200 reais",
            "expected_keywords": ["abaixo de R$400", "não compensa", "indicação"]
        },
        "rental_property": {
            "message": "Moro de aluguel, não posso instalar nada",
            "expected_keywords": ["assinatura", "sem instalação", "12-20%"]
        }
    }
    
    # Calendar availability mock data
    CALENDAR_SLOTS = [
        {
            "start": "2024-12-20T10:00:00-03:00",
            "end": "2024-12-20T11:00:00-03:00",
            "duration_minutes": 60
        },
        {
            "start": "2024-12-20T14:00:00-03:00",
            "end": "2024-12-20T15:00:00-03:00",
            "duration_minutes": 60
        },
        {
            "start": "2024-12-21T09:00:00-03:00",
            "end": "2024-12-21T10:00:00-03:00",
            "duration_minutes": 60
        }
    ]
    
    # Kommo CRM mock responses
    KOMMO_RESPONSES = {
        "lead_created": {
            "id": 12345,
            "name": "João Silva - WhatsApp",
            "price": 0,
            "status_id": 142,  # Novo Lead
            "pipeline_id": 1,
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "updated_at": int(datetime.now(timezone.utc).timestamp()),
            "custom_fields_values": [
                {"field_id": 123, "values": [{"value": TEST_PHONES["lead_1"]}]}
            ]
        },
        "stage_updated": {
            "id": 12345,
            "status_id": 143,  # Em Negociação
            "updated_at": int(datetime.now(timezone.utc).timestamp())
        }
    }
    
    # Follow-up scenarios
    FOLLOW_UP_SCENARIOS = {
        "first_attempt": {
            "delay_minutes": 30,
            "message": "Oi {name}! 😊 Vi que você demonstrou interesse em economizar na conta de luz. Ainda está por aí?",
            "type": "reminder"
        },
        "second_attempt": {
            "delay_hours": 24,
            "message": "Olá {name}! Helen aqui da SolarPrime 👋 Ontem conversamos sobre economia de energia. Conseguiu ver minha mensagem?",
            "type": "check_in"
        },
        "nurture": {
            "delay_days": 3,
            "message": "Oi {name}! Sabia que nossos clientes economizam em média R$500 por mês? 💰 Que tal conversarmos sobre isso?",
            "type": "nurture"
        }
    }
    
    # Error scenarios
    ERROR_SCENARIOS = {
        "evolution_api_down": {
            "error": "Connection refused: Evolution API unavailable",
            "retry_count": 3
        },
        "kommo_rate_limit": {
            "error": "429 Too Many Requests: Kommo API rate limit exceeded",
            "retry_after": 60
        },
        "google_calendar_auth": {
            "error": "401 Unauthorized: Invalid Google Calendar credentials",
            "requires_reauth": True
        },
        "database_connection": {
            "error": "PostgreSQL connection failed: Connection timeout",
            "retry_count": 5
        }
    }
    
    @classmethod
    def get_sample_message(cls, message_type: str = "text", content: str = None) -> Dict[str, Any]:
        """Get a sample message for testing"""
        if message_type == "text":
            payload = cls.WEBHOOK_PAYLOADS["text_message"].copy()
            if content:
                payload["data"]["message"]["conversation"] = content
            return payload
        return cls.WEBHOOK_PAYLOADS.get(f"{message_type}_message", {})
    
    @classmethod
    def get_lead_at_stage(cls, stage: str) -> Dict[str, Any]:
        """Get lead data at specific qualification stage"""
        stage_map = {
            "new": "new_lead",
            "identified": "identified_lead",
            "qualifying": "qualifying_lead",
            "qualified": "qualified_lead",
            "disqualified": "disqualified_lead"
        }
        return cls.LEAD_DATA.get(stage_map.get(stage, "new_lead"), {})