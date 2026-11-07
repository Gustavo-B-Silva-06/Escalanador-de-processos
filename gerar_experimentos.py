import json
import os
import subprocess
import sys

EXPERIMENTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experimentos")
os.makedirs(EXPERIMENTOS_DIR, exist_ok=True)

CONFIG_MLFQ = {"quantuns": [2, 4, 8], "boost": 20}

# 1. Experimento 1: Conjunto comum (Seção 5.1 / 7.1)
PROCESSOS_EXP1 = [
    {"id": "P01", "chegada": 0, "cpu": 8},
    {"id": "P02", "chegada": 1, "cpu": 4},
    {"id": "P03", "chegada": 2, "cpu": 2},
    {"id": "P04", "chegada": 4, "cpu": 1},
]

# 2. Experimento 2 - Caso 1: CPU ociosa no início e entre chegadas
PROCESSOS_EXP2_CASO1 = [
    {"id": "P01", "chegada": 2, "cpu": 3},
    {"id": "P02", "chegada": 3, "cpu": 2},
    {"id": "P03", "chegada": 9, "cpu": 4},
    {"id": "P04", "chegada": 10, "cpu": 1},
]

# 3. Experimento 2 - Caso 2: Processos de durações diferentes e chegadas durante uma execução
PROCESSOS_EXP2_CASO2 = [
    {"id": "P01", "chegada": 0, "cpu": 10},
    {"id": "P02", "chegada": 1, "cpu": 6},
    {"id": "P03", "chegada": 2, "cpu": 2},
    {"id": "P04", "chegada": 3, "cpu": 4},
]

# 4. Experimento 2 - Caso 3: Empates exercitando regras de desempate (chegada e ID lexicográfico)
# Ordem no arquivo propositalmente embaralhada para comprovar independência da ordem do JSON
PROCESSOS_EXP2_CASO3 = [
    {"id": "P03", "chegada": 1, "cpu": 3},
    {"id": "P01", "chegada": 0, "cpu": 5},
    {"id": "P04", "chegada": 2, "cpu": 3},
    {"id": "P02", "chegada": 1, "cpu": 3},
]

# 5. Experimento 3 - SJF: Processo longo preterido por chegadas sucessivas de processos curtos (Starvation)
PROCESSOS_EXP3_SJF = [
    {"id": "P01", "chegada": 0, "cpu": 3},
    {"id": "P02", "chegada": 1, "cpu": 12},
    {"id": "P03", "chegada": 2, "cpu": 2},
    {"id": "P04", "chegada": 4, "cpu": 1},
    {"id": "P05", "chegada": 5, "cpu": 2},
    {"id": "P06", "chegada": 7, "cpu": 2},
]

# 6. Experimento 3 - MLFQ: Rebaixamento, Interrupção por prioridade (com preservação de saldo) e Boost
PROCESSOS_EXP3_MLFQ = [
    {"id": "P01", "chegada": 0, "cpu": 18},
    {"id": "P02", "chegada": 3, "cpu": 12},
]

CASOS = [
    ("exp1_comum_sjf", "SJF", {}, PROCESSOS_EXP1),
    ("exp1_comum_mlfq", "MLFQ", CONFIG_MLFQ, PROCESSOS_EXP1),
    ("exp2_caso1_ocioso_sjf", "SJF", {}, PROCESSOS_EXP2_CASO1),
    ("exp2_caso1_ocioso_mlfq", "MLFQ", CONFIG_MLFQ, PROCESSOS_EXP2_CASO1),
    ("exp2_caso2_duracoes_sjf", "SJF", {}, PROCESSOS_EXP2_CASO2),
    ("exp2_caso2_duracoes_mlfq", "MLFQ", CONFIG_MLFQ, PROCESSOS_EXP2_CASO2),
    ("exp2_caso3_empates_sjf", "SJF", {}, PROCESSOS_EXP2_CASO3),
    ("exp2_caso3_empates_mlfq", "MLFQ", CONFIG_MLFQ, PROCESSOS_EXP2_CASO3),
    ("exp3_sjf_starvation_sjf", "SJF", {}, PROCESSOS_EXP3_SJF),
    ("exp3_sjf_starvation_mlfq", "MLFQ", CONFIG_MLFQ, PROCESSOS_EXP3_SJF),
    ("exp3_mlfq_eventos_sjf", "SJF", {}, PROCESSOS_EXP3_MLFQ),
    ("exp3_mlfq_eventos_mlfq", "MLFQ", CONFIG_MLFQ, PROCESSOS_EXP3_MLFQ),
]


def main() -> None:
    simulador_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulador.py")
    for nome, alg, conf, procs in CASOS:
        entrada_path = os.path.join(EXPERIMENTOS_DIR, f"{nome}_entrada.json")
        saida_path = os.path.join(EXPERIMENTOS_DIR, f"{nome}_saida.json")

        payload = {
            "algoritmo": alg,
            "configuracao": conf,
            "processos": procs,
        }
        with open(entrada_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")

        with open(entrada_path, "r", encoding="utf-8") as fin:
            proc = subprocess.run(
                [sys.executable, simulador_path],
                stdin=fin,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            )

        with open(saida_path, "w", encoding="utf-8") as fout:
            fout.write(proc.stdout)

        print(f"[OK] {nome}: entrada e saída geradas com sucesso.")


if __name__ == "__main__":
    main()
