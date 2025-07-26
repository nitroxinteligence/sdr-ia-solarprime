"""
Métricas e Análise de Reasoning
================================
Utilitários para monitorar e analisar o processo de reasoning do agente
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger
import json


class ReasoningMetrics:
    """Classe para coletar e analisar métricas do processo de reasoning"""
    
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        
    def log_reasoning_session(
        self, 
        session_id: str, 
        reasoning_steps: Any,
        response_time: float,
        stage: str,
        sentiment: str
    ):
        """Registra uma sessão de reasoning"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "response_time": response_time,
            "stage": stage,
            "sentiment": sentiment,
            "steps_count": self._count_steps(reasoning_steps),
            "reasoning_data": self._extract_reasoning_data(reasoning_steps)
        }
        
        self.sessions[session_id].append(session_data)
        logger.debug(f"Reasoning metrics logged for session {session_id}")
        
    def _count_steps(self, reasoning_steps: Any) -> int:
        """Conta o número de passos de reasoning"""
        if isinstance(reasoning_steps, list):
            return len(reasoning_steps)
        elif reasoning_steps:
            return 1
        return 0
        
    def _extract_reasoning_data(self, reasoning_steps: Any) -> Dict[str, Any]:
        """Extrai dados relevantes do reasoning"""
        if not reasoning_steps:
            return {}
            
        data = {
            "has_reasoning": True,
            "type": type(reasoning_steps).__name__
        }
        
        if isinstance(reasoning_steps, list):
            data["steps"] = [str(step)[:100] for step in reasoning_steps]  # Primeiros 100 chars
        else:
            data["content"] = str(reasoning_steps)[:200]  # Primeiros 200 chars
            
        return data
        
    def get_session_metrics(self, session_id: str) -> Dict[str, Any]:
        """Obtém métricas de uma sessão específica"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
            
        sessions = self.sessions[session_id]
        
        return {
            "total_interactions": len(sessions),
            "average_response_time": sum(s["response_time"] for s in sessions) / len(sessions),
            "average_reasoning_steps": sum(s["steps_count"] for s in sessions) / len(sessions),
            "stages_visited": list(set(s["stage"] for s in sessions)),
            "sentiment_distribution": self._calculate_sentiment_distribution(sessions)
        }
        
    def _calculate_sentiment_distribution(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calcula distribuição de sentimentos"""
        distribution = {"positivo": 0, "neutro": 0, "negativo": 0}
        
        for session in sessions:
            sentiment = session.get("sentiment", "neutro")
            if sentiment in distribution:
                distribution[sentiment] += 1
                
        return distribution
        
    def export_metrics(self, session_id: Optional[str] = None) -> str:
        """Exporta métricas em formato JSON"""
        if session_id:
            data = {
                session_id: self.get_session_metrics(session_id)
            }
        else:
            data = {
                sid: self.get_session_metrics(sid) 
                for sid in self.sessions.keys()
            }
            
        return json.dumps(data, indent=2, ensure_ascii=False)
        
    def analyze_reasoning_quality(self, session_id: str) -> Dict[str, Any]:
        """Analisa a qualidade do reasoning em uma sessão"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
            
        sessions = self.sessions[session_id]
        
        # Análise de qualidade
        quality_metrics = {
            "consistency": self._check_consistency(sessions),
            "progression": self._check_progression(sessions),
            "effectiveness": self._check_effectiveness(sessions),
            "recommendations": self._generate_recommendations(sessions)
        }
        
        return quality_metrics
        
    def _check_consistency(self, sessions: List[Dict[str, Any]]) -> float:
        """Verifica consistência do reasoning (0-1)"""
        if len(sessions) < 2:
            return 1.0
            
        # Verifica se o número de steps é consistente
        steps_counts = [s["steps_count"] for s in sessions]
        avg_steps = sum(steps_counts) / len(steps_counts)
        variance = sum((x - avg_steps) ** 2 for x in steps_counts) / len(steps_counts)
        
        # Menor variância = maior consistência
        consistency = 1.0 / (1.0 + variance)
        return round(consistency, 2)
        
    def _check_progression(self, sessions: List[Dict[str, Any]]) -> str:
        """Verifica progressão pelos estágios"""
        stages = [s["stage"] for s in sessions]
        
        expected_progression = [
            "INITIAL_CONTACT",
            "IDENTIFICATION", 
            "DISCOVERY",
            "QUALIFICATION",
            "OBJECTION_HANDLING",
            "SCHEDULING"
        ]
        
        # Verifica se segue a progressão esperada
        current_idx = 0
        for stage in stages:
            if stage in expected_progression:
                stage_idx = expected_progression.index(stage)
                if stage_idx >= current_idx:
                    current_idx = stage_idx
                else:
                    return "irregular"
                    
        return "normal" if current_idx > 0 else "stuck"
        
    def _check_effectiveness(self, sessions: List[Dict[str, Any]]) -> float:
        """Verifica efetividade do reasoning (0-1)"""
        if not sessions:
            return 0.0
            
        # Métricas de efetividade
        positive_sentiments = sum(1 for s in sessions if s["sentiment"] == "positivo")
        reached_scheduling = any(s["stage"] == "SCHEDULING" for s in sessions)
        avg_response_time = sum(s["response_time"] for s in sessions) / len(sessions)
        
        # Pontuação
        score = 0.0
        score += (positive_sentiments / len(sessions)) * 0.4  # 40% peso sentimento
        score += 0.3 if reached_scheduling else 0.0  # 30% peso agendamento
        score += max(0, (5.0 - avg_response_time) / 5.0) * 0.3  # 30% peso velocidade
        
        return round(score, 2)
        
    def _generate_recommendations(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Analisa métricas
        avg_steps = sum(s["steps_count"] for s in sessions) / len(sessions) if sessions else 0
        avg_time = sum(s["response_time"] for s in sessions) / len(sessions) if sessions else 0
        
        if avg_steps < 2:
            recommendations.append("Considere aumentar reasoning_min_steps para análises mais profundas")
        elif avg_steps > 4:
            recommendations.append("Reasoning com muitos passos pode deixar respostas lentas")
            
        if avg_time > 10:
            recommendations.append("Tempo de resposta alto - considere otimizar prompts")
            
        negative_count = sum(1 for s in sessions if s["sentiment"] == "negativo")
        if negative_count > len(sessions) * 0.3:
            recommendations.append("Alto índice de sentimento negativo - revisar abordagem")
            
        return recommendations


# Instância global para uso no sistema
reasoning_metrics = ReasoningMetrics()


# Funções helper
def log_reasoning(session_id: str, reasoning_data: Any, metadata: Dict[str, Any]):
    """Helper para logar reasoning facilmente"""
    reasoning_metrics.log_reasoning_session(
        session_id=session_id,
        reasoning_steps=reasoning_data,
        response_time=metadata.get("response_time", 0.0),
        stage=metadata.get("stage", "UNKNOWN"),
        sentiment=metadata.get("sentiment", "neutro")
    )


def get_reasoning_report(session_id: str) -> Dict[str, Any]:
    """Helper para obter relatório de reasoning"""
    return {
        "metrics": reasoning_metrics.get_session_metrics(session_id),
        "quality": reasoning_metrics.analyze_reasoning_quality(session_id)
    }