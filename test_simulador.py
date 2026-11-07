import json
import subprocess
import sys
import unittest
from simulador import executar_simulacao
from validacao import ErroValidacao


class TestSimuladorEscalonamento(unittest.TestCase):
    def test_sjf_experimento_1(self) -> None:
        entrada = {
            "algoritmo": "SJF",
            "configuracao": {},
            "processos": [
                {"id": "P01", "chegada": 0, "cpu": 8},
                {"id": "P02", "chegada": 1, "cpu": 4},
                {"id": "P03", "chegada": 2, "cpu": 2},
                {"id": "P04", "chegada": 4, "cpu": 1},
            ],
        }
        res = executar_simulacao(json.dumps(entrada))
        self.assertEqual(res["algoritmo"], "SJF")
        self.assertEqual(
            res["linha_do_tempo"],
            [
                {"processo": "P01", "inicio": 0, "fim": 8},
                {"processo": "P04", "inicio": 8, "fim": 9},
                {"processo": "P03", "inicio": 9, "fim": 11},
                {"processo": "P02", "inicio": 11, "fim": 15},
            ],
        )
        self.assertAlmostEqual(res["medias"]["turnaround"], 9.0)
        self.assertAlmostEqual(res["medias"]["espera"], 5.25)
        self.assertAlmostEqual(res["medias"]["resposta"], 5.25)

    def test_mlfq_experimento_1(self) -> None:
        entrada = {
            "algoritmo": "MLFQ",
            "configuracao": {"quantuns": [2, 4, 8], "boost": 20},
            "processos": [
                {"id": "P01", "chegada": 0, "cpu": 8},
                {"id": "P02", "chegada": 1, "cpu": 4},
                {"id": "P03", "chegada": 2, "cpu": 2},
                {"id": "P04", "chegada": 4, "cpu": 1},
            ],
        }
        res = executar_simulacao(json.dumps(entrada))
        self.assertEqual(res["algoritmo"], "MLFQ")
        self.assertEqual(
            res["linha_do_tempo"],
            [
                {"processo": "P01", "inicio": 0, "fim": 2},
                {"processo": "P02", "inicio": 2, "fim": 4},
                {"processo": "P03", "inicio": 4, "fim": 6},
                {"processo": "P04", "inicio": 6, "fim": 7},
                {"processo": "P01", "inicio": 7, "fim": 11},
                {"processo": "P02", "inicio": 11, "fim": 13},
                {"processo": "P01", "inicio": 13, "fim": 15},
            ],
        )
        self.assertAlmostEqual(res["medias"]["turnaround"], 8.5)
        self.assertAlmostEqual(res["medias"]["espera"], 4.75)
        self.assertAlmostEqual(res["medias"]["resposta"], 1.25)

    def test_mlfq_preempcao_conserva_saldo_quantum(self) -> None:
        # P01 chega em 0 com CPU 10.
        # [0, 2): Fila 0 (esgota quantum 2 -> desce p/ Fila 1)
        # [2, 3): Fila 1 (usa 1 de 4 do quantum da Fila 1; saldo restante = 3)
        # Em t=3, P02 chega com CPU 1 -> entra na Fila 0 e interrompe P01.
        # [3, 4): P02 executa na Fila 0 e conclui em t=4.
        # [4, 7): P01 retoma na frente da Fila 1 e usa apenas o saldo de 3 unidades!
        # Em t=7, P01 desce para a Fila 2 (restam 4 unidades) e executa [7, 11).
        entrada = {
            "algoritmo": "MLFQ",
            "configuracao": {"quantuns": [2, 4, 8], "boost": 50},
            "processos": [
                {"id": "P01", "chegada": 0, "cpu": 10},
                {"id": "P02", "chegada": 3, "cpu": 1},
            ],
        }
        res = executar_simulacao(json.dumps(entrada))
        # Note que [4, 7) e [7, 11) são do mesmo processo P01 e são unidos na saída em [4, 11)
        self.assertEqual(
            res["linha_do_tempo"],
            [
                {"processo": "P01", "inicio": 0, "fim": 3},
                {"processo": "P02", "inicio": 3, "fim": 4},
                {"processo": "P01", "inicio": 4, "fim": 11},
            ],
        )

    def test_mlfq_coincidencia_boost_fim_quantum_e_chegada(self) -> None:
        # Verifica que o boost prevalece sobre o rebaixamento quando coincidem
        entrada = {
            "algoritmo": "MLFQ",
            "configuracao": {"quantuns": [2, 4, 8], "boost": 6},
            "processos": [
                {"id": "P02", "chegada": 0, "cpu": 10},
                {"id": "P01", "chegada": 6, "cpu": 2},
            ],
        }
        # P02 executa [0, 2) na fila 0 -> desce p/ fila 1 em t=2.
        # P02 executa [2, 6) na fila 1 -> em t=6 esgotaria o quantum 4 da fila 1,
        # MAS t=6 é instante de boost e P01 chega em t=6.
        # Ambos vão para a fila 0 ordenados por (chegada, id): P02 (chegada 0) antes de P01 (chegada 6)!
        # Portanto P02 recebe [6, 8) na fila 0 (unido com [0, 6) -> [0, 8)), depois P01 [8, 10), depois P02 [10, 12).
        res = executar_simulacao(json.dumps(entrada))
        self.assertEqual(
            res["linha_do_tempo"],
            [
                {"processo": "P02", "inicio": 0, "fim": 8},
                {"processo": "P01", "inicio": 8, "fim": 10},
                {"processo": "P02", "inicio": 10, "fim": 12},
            ],
        )

    def test_validacao_entradas_invalidas(self) -> None:
        casos_invalidos = [
            "",
            "{invalido",
            json.dumps([]),
            json.dumps({"algoritmo": "FCFS", "configuracao": {}, "processos": [{"id": "P01", "chegada": 0, "cpu": 1}]}),
            json.dumps({"algoritmo": "SJF", "configuracao": {}, "processos": []}),
            json.dumps({"algoritmo": "SJF", "configuracao": {}, "processos": [{"id": "OCIOSO", "chegada": 0, "cpu": 1}]}),
            json.dumps({"algoritmo": "SJF", "configuracao": {}, "processos": [{"id": "P01", "chegada": -1, "cpu": 1}]}),
            json.dumps({"algoritmo": "SJF", "configuracao": {}, "processos": [{"id": "P01", "chegada": 0, "cpu": 0}]}),
            json.dumps({"algoritmo": "SJF", "configuracao": {}, "processos": [{"id": "P01", "chegada": True, "cpu": 2}]}),
            json.dumps({"algoritmo": "MLFQ", "configuracao": {"quantuns": [4, 2, 8], "boost": 20}, "processos": [{"id": "P01", "chegada": 0, "cpu": 2}]}),
            json.dumps({"algoritmo": "MLFQ", "configuracao": {"quantuns": [2, 4], "boost": 20}, "processos": [{"id": "P01", "chegada": 0, "cpu": 2}]}),
            json.dumps({"algoritmo": "MLFQ", "configuracao": {"quantuns": [2, 4, 8], "boost": 0}, "processos": [{"id": "P01", "chegada": 0, "cpu": 2}]}),
        ]
        for caso in casos_invalidos:
            with self.assertRaises(ErroValidacao):
                executar_simulacao(caso)

    def test_cli_erro_retorna_codigo_nao_zero(self) -> None:
        proc = subprocess.run(
            [sys.executable, "simulador.py"],
            input='{"algoritmo": "SJF", "configuracao": {}, "processos": [{"id": "P01", "chegada": 0, "cpu": -5}]}',
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertNotEqual(proc.returncode, 0)
        saida = json.loads(proc.stdout)
        self.assertIn("erro", saida)


if __name__ == "__main__":
    unittest.main()
