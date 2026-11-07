from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class Processo:
    """Representa um processo na simulação de escalonamento."""
    id: str
    chegada: int
    cpu: int
    restante: int = 0
    primeira_execucao: Optional[int] = None
    conclusao: Optional[int] = None
    # Atributos auxiliares para o MLFQ
    fila: int = 0
    quantum_usado: int = 0

    def __post_init__(self) -> None:
        self.restante = self.cpu


@dataclass
class IntervaloLinhaDoTempo:
    """Representa um intervalo [inicio, fim) de uso da CPU ou ociosidade."""
    processo: str
    inicio: int
    fim: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "processo": self.processo,
            "inicio": self.inicio,
            "fim": self.fim,
        }


@dataclass
class MetricaProcesso:
    """Armazena as métricas calculadas para um processo concluído."""
    id: str
    primeira_execucao: int
    conclusao: int
    turnaround: int
    espera: int
    resposta: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "primeira_execucao": self.primeira_execucao,
            "conclusao": self.conclusao,
            "turnaround": self.turnaround,
            "espera": self.espera,
            "resposta": self.resposta,
        }
