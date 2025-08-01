"""Agente SDR IA SolarPrime - Modular Architecture"""

try:
    from .core.agent import SDRAgent
except ImportError:
    SDRAgent = None

# AgentConfig não existe no config.py atual, removendo import
# from .core.config import AgentConfig

__version__ = "2.0.0"
__all__ = ["SDRAgent"] if SDRAgent else []