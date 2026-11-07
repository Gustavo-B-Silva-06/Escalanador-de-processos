import json
from typing import Tuple, List, Dict, Any
from modelos import Processo


ALGORITMOS_IMPLEMENTADOS = {"SJF", "MLFQ"}
TODOS_ALGORITMOS = {"FCFS", "SJF", "SRTF", "RR", "MLFQ", "CFS"}


class ErroValidacao(Exception):
    """Exceção lançada quando a entrada JSON é inválida."""
    pass


def _eh_inteiro(valor: Any) -> bool:
    """Verifica se o valor é um inteiro estrito (excluindo booleanos)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def ler_e_validar_entrada( conteudo_json: str) -> Tuple[str, Dict[str, Any], List[Processo]]:
    """
    Lê e valida a string JSON de entrada de acordo com a especificação do trabalho.
    Retorna (algoritmo, configuracao, lista_de_processos).
    Lança ErroValidacao em caso de qualquer inconsistência.
    """
    if not conteudo_json or not conteudo_json.strip():
        raise ErroValidacao("A entrada padrão está vazia. Forneça um objeto JSON válido.")

    try:
        dados = json.loads(conteudo_json)
    except json.JSONDecodeError as e:
        raise ErroValidacao(f"JSON inválido na entrada: {str(e)}")

    if not isinstance(dados, dict):
        raise ErroValidacao("O elemento raiz do JSON deve ser um objeto.")

    # 1. Validação do campo 'algoritmo'
    if "algoritmo" not in dados:
        raise ErroValidacao("O campo obrigatório 'algoritmo' está ausente.")

    algoritmo = dados["algoritmo"]
    if not isinstance(algoritmo, str) or not algoritmo.strip():
        raise ErroValidacao("O campo 'algoritmo' deve ser uma string não vazia.")

    if algoritmo not in ALGORITMOS_IMPLEMENTADOS:
        if algoritmo in TODOS_ALGORITMOS:
            raise ErroValidacao(
                f"O algoritmo '{algoritmo}' não foi atribuído a esta dupla. "
                f"Algoritmos implementados: SJF e MLFQ."
            )
        raise ErroValidacao(
            f"Algoritmo '{algoritmo}' desconhecido. Valores suportados pela dupla: SJF, MLFQ."
        )

    # 2. Validação do campo 'configuracao'
    if "configuracao" not in dados:
        raise ErroValidacao("O campo obrigatório 'configuracao' está ausente.")

    configuracao = dados["configuracao"]
    if not isinstance(configuracao, dict):
        raise ErroValidacao("O campo 'configuracao' deve ser um objeto JSON.")

    config_validada: Dict[str, Any] = {}
    if algoritmo == "MLFQ":
        if "quantuns" not in configuracao:
            raise ErroValidacao("O algoritmo MLFQ exige o parâmetro 'quantuns' em 'configuracao'.")
        if "boost" not in configuracao:
            raise ErroValidacao("O algoritmo MLFQ exige o parâmetro 'boost' em 'configuracao'.")

        quantuns = configuracao["quantuns"]
        if not isinstance(quantuns, list) or len(quantuns) != 3:
            raise ErroValidacao("O parâmetro 'quantuns' do MLFQ deve ser uma lista com exatamente 3 valores.")

        for i, q in enumerate(quantuns):
            if not _eh_inteiro(q) or q <= 0:
                raise ErroValidacao(
                    f"Todos os valores em 'quantuns' devem ser inteiros positivos (erro na posição {i})."
                )

        if not (quantuns[0] <= quantuns[1] <= quantuns[2]):
            raise ErroValidacao(
                "Os três valores de 'quantuns' do MLFQ devem estar em ordem não decrescente."
            )

        boost = configuracao["boost"]
        if not _eh_inteiro(boost) or boost <= 0:
            raise ErroValidacao("O parâmetro 'boost' do MLFQ deve ser um inteiro positivo.")

        config_validada["quantuns"] = list(quantuns)
        config_validada["boost"] = boost

    # 3. Validação do campo 'processos'
    if "processos" not in dados:
        raise ErroValidacao("O campo obrigatório 'processos' está ausente.")

    processos_raw = dados["processos"]
    if not isinstance(processos_raw, list) or len(processos_raw) == 0:
        raise ErroValidacao("O campo 'processos' deve ser uma lista não vazia.")

    ids_vistos = set()
    processos: List[Processo] = []

    for idx, item in enumerate(processos_raw):
        if not isinstance(item, dict):
            raise ErroValidacao(f"O elemento na posição {idx} de 'processos' deve ser um objeto JSON.")

        if "id" not in item:
            raise ErroValidacao(f"O processo na posição {idx} não possui o campo 'id'.")
        proc_id = item["id"]
        if not isinstance(proc_id, str) or not proc_id.strip():
            raise ErroValidacao("O campo 'id' do processo deve ser uma string não vazia.")
        if proc_id == "OCIOSO":
            raise ErroValidacao("O identificador 'OCIOSO' é reservado e não pode ser usado por um processo.")
        if proc_id in ids_vistos:
            raise ErroValidacao(f"Identificador de processo duplicado: '{proc_id}'.")
        ids_vistos.add(proc_id)

        if "chegada" not in item:
            raise ErroValidacao(f"O processo '{proc_id}' não possui o campo 'chegada'.")
        chegada = item["chegada"]
        if not _eh_inteiro(chegada) or chegada < 0:
            raise ErroValidacao("O instante de chegada deve ser um inteiro maior ou igual a zero.")

        if "cpu" not in item:
            raise ErroValidacao(f"O processo '{proc_id}' não possui o campo 'cpu'.")
        cpu = item["cpu"]
        if not _eh_inteiro(cpu) or cpu <= 0:
            raise ErroValidacao("O tempo de CPU deve ser um inteiro positivo.")

        processos.append(Processo(id=proc_id, chegada=chegada, cpu=cpu))

    return algoritmo, config_validada, processos
