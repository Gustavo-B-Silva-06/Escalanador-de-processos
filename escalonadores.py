from collections import deque
from typing import List, Dict, Any, Optional, Deque
from modelos import Processo, IntervaloLinhaDoTempo


def adicionar_intervalo(
    linha_do_tempo: List[IntervaloLinhaDoTempo],
    processo_id: str,
    inicio: int,
    fim: int
) -> None:
    """
    Adiciona um intervalo [inicio, fim) à linha do tempo, unindo intervalos
    adjacentes do mesmo processo (ou OCIOSO), conforme seção 5.2 do enunciado.
    """
    if fim <= inicio:
        return
    if (
        linha_do_tempo
        and linha_do_tempo[-1].processo == processo_id
        and linha_do_tempo[-1].fim == inicio
    ):
        linha_do_tempo[-1].fim = fim
    else:
        linha_do_tempo.append(
            IntervaloLinhaDoTempo(processo=processo_id, inicio=inicio, fim=fim)
        )


def escalonar_sjf(processos: List[Processo]) -> List[IntervaloLinhaDoTempo]:
    """
    Implementa o algoritmo SJF (Shortest Job First) não-preemptivo.
    Regra de escolha: menor tempo total de CPU entre os processos prontos.
    Desempate geral: menor instante de chegada e, depois, menor ID lexicográfico.
    """
    linha_do_tempo: List[IntervaloLinhaDoTempo] = []
    total = len(processos)
    concluidos = 0
    t = 0

    while concluidos < total:
        prontos = [p for p in processos if p.conclusao is None and p.chegada <= t]

        if not prontos:
            proxima_chegada = min(p.chegada for p in processos if p.conclusao is None)
            adicionar_intervalo(linha_do_tempo, "OCIOSO", t, proxima_chegada)
            t = proxima_chegada
            continue

        # Escolhe pelo menor tempo total de CPU; desempata por chegada e ID
        escolhido = min(prontos, key=lambda p: (p.cpu, p.chegada, p.id))

        if escolhido.primeira_execucao is None:
            escolhido.primeira_execucao = t

        inicio = t
        fim = t + escolhido.cpu
        escolhido.restante = 0
        escolhido.conclusao = fim

        adicionar_intervalo(linha_do_tempo, escolhido.id, inicio, fim)
        t = fim
        concluidos += 1

    return linha_do_tempo


def escalonar_mlfq(
    processos: List[Processo],
    configuracao: Dict[str, Any]
) -> List[IntervaloLinhaDoTempo]:
    """
    Implementa o algoritmo MLFQ (Multilevel Feedback Queue) na versão didática:
    - 3 filas (0, 1, 2) com prioridade decrescente e quanta definidos em 'quantuns'.
    - Novos processos entram no final da fila 0.
    - Dentro de cada fila, utiliza Round Robin.
    - Processo que consome integralmente seu quantum sem concluir desce uma fila (até a 2).
    - Chegada na fila 0 interrompe processo em fila inferior (que permanece na frente
      de sua fila conservando o saldo do quantum).
    - A cada 'boost' unidades (t > 0 e t % boost == 0), move todos os processos prontos
      para a fila 0, reinicia suas cotas e ordena por (chegada, id).
    """
    quantuns: List[int] = configuracao["quantuns"]
    boost: int = configuracao["boost"]

    linha_do_tempo: List[IntervaloLinhaDoTempo] = []
    filas: List[Deque[Processo]] = [deque(), deque(), deque()]

    # Ordena por instante de chegada e ID para admissão determinística
    processos_ordenados = sorted(processos, key=lambda p: (p.chegada, p.id))
    total = len(processos_ordenados)
    idx_chegada = 0
    concluidos = 0
    t = 0
    atual: Optional[Processo] = None

    while concluidos < total:
        # 1. No instante t, registrar a execução que terminou em t e identificar conclusões
        if atual is not None:
            atual.restante -= 1
            atual.quantum_usado += 1
            if atual.restante == 0:
                atual.conclusao = t
                filas[atual.fila].popleft()
                atual = None
                concluidos += 1
                if concluidos == total:
                    break

        # 2. Admitir os processos que chegam em t antes da próxima decisão
        while idx_chegada < total and processos_ordenados[idx_chegada].chegada == t:
            novo = processos_ordenados[idx_chegada]
            novo.fila = 0
            novo.quantum_usado = 0
            filas[0].append(novo)
            idx_chegada += 1

        # 3. Tratar boost ou esgotamento de quantum
        if t > 0 and t % boost == 0:
            # Boost prevalece sobre o rebaixamento e ordena prontos por (chegada, id)
            prontos_no_boost: List[Processo] = []
            for f in range(3):
                prontos_no_boost.extend(filas[f])
                filas[f].clear()

            if prontos_no_boost:
                prontos_no_boost.sort(key=lambda p: (p.chegada, p.id))
                for p in prontos_no_boost:
                    p.fila = 0
                    p.quantum_usado = 0
                    filas[0].append(p)
            atual = None
        else:
            # Fora de um instante de boost, esgotamento do quantum provoca rebaixamento normal
            if atual is not None and atual.quantum_usado == quantuns[atual.fila]:
                filas[atual.fila].popleft()
                nova_fila = min(atual.fila + 1, 2)
                atual.fila = nova_fila
                atual.quantum_usado = 0
                filas[nova_fila].append(atual)
                atual = None

        # 4. Decisão de escalonamento para o intervalo [t, t + 1)
        fila_escolhida: Optional[int] = None
        for f in range(3):
            if len(filas[f]) > 0:
                fila_escolhida = f
                break

        if fila_escolhida is not None:
            escolhido = filas[fila_escolhida][0]
            if escolhido.primeira_execucao is None:
                escolhido.primeira_execucao = t
            adicionar_intervalo(linha_do_tempo, escolhido.id, t, t + 1)
            atual = escolhido
            t += 1
        else:
            # Nenhuma fila possui processo pronto: CPU fica ociosa até a próxima chegada
            proxima_chegada = processos_ordenados[idx_chegada].chegada
            adicionar_intervalo(linha_do_tempo, "OCIOSO", t, proxima_chegada)
            atual = None
            t = proxima_chegada

    return linha_do_tempo
