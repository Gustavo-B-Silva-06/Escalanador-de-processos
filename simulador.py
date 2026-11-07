import sys
import json
from typing import Dict, Any

from validacao import ler_e_validar_entrada, ErroValidacao
from escalonadores import escalonar_sjf, escalonar_mlfq
from metricas import calcular_metricas


def executar_simulacao(conteudo_json: str) -> Dict[str, Any]:
    """
    Executa o fluxo completo: validação, escalonamento e cálculo de métricas.
    Retorna o dicionário pronto para serialização JSON.
    """
    # Remove eventual BOM UTF-8 gerado pelo PowerShell no Windows
    conteudo_limpo = conteudo_json.lstrip("\ufeff")
    algoritmo, configuracao, processos = ler_e_validar_entrada(conteudo_limpo)

    if algoritmo == "SJF":
        linha_do_tempo = escalonar_sjf(processos)
    elif algoritmo == "MLFQ":
        linha_do_tempo = escalonar_mlfq(processos, configuracao)
    else:
        raise ErroValidacao(f"Algoritmo '{algoritmo}' não suportado.")

    metricas_processos, medias = calcular_metricas(processos)

    return {
        "algoritmo": algoritmo,
        "linha_do_tempo": [intervalo.to_dict() for intervalo in linha_do_tempo],
        "processos": [m.to_dict() for m in metricas_processos],
        "medias": medias,
    }


def main() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        entrada_str = sys.stdin.read()
        resultado = executar_simulacao(entrada_str)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        sys.exit(0)
    except ErroValidacao as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"erro": f"Erro interno na simulação: {str(e)}"}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
