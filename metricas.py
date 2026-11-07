from typing import List, Dict, Any, Tuple
from modelos import Processo, MetricaProcesso


def calcular_metricas(
    processos: List[Processo]
) -> Tuple[List[MetricaProcesso], Dict[str, float]]:
    """
    Calcula as métricas individuais (ordenadas pelo ID do processo) e as médias
    de turnaround, espera e resposta, conforme seções 5.2 e 6 do enunciado.
    """
    processos_ordenados = sorted(processos, key=lambda p: p.id)
    metricas_individuais: List[MetricaProcesso] = []

    soma_turnaround = 0
    soma_espera = 0
    soma_resposta = 0
    n = len(processos_ordenados)

    for p in processos_ordenados:
        if p.primeira_execucao is None or p.conclusao is None:
            raise RuntimeError(f"Processo '{p.id}' não possui métricas completas após a simulação.")

        turnaround = p.conclusao - p.chegada
        espera = turnaround - p.cpu
        resposta = p.primeira_execucao - p.chegada

        soma_turnaround += turnaround
        soma_espera += espera
        soma_resposta += resposta

        metricas_individuais.append(
            MetricaProcesso(
                id=p.id,
                primeira_execucao=p.primeira_execucao,
                conclusao=p.conclusao,
                turnaround=turnaround,
                espera=espera,
                resposta=resposta,
            )
        )

    medias = {
        "turnaround": soma_turnaround / n,
        "espera": soma_espera / n,
        "resposta": soma_resposta / n,
    }

    return metricas_individuais, medias
