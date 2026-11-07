# Simulador de Escalonamento de Processos — SJF e MLFQ

**Disciplina:** Sistemas Operacionais  
**Dupla 2:** Gustavo e Andressa  
**Algoritmos atribuídos e implementados:**
- `SJF` (*Shortest Job First* — não-preemptivo)
- `MLFQ` (*Multilevel Feedback Queue* — Filas Multinível com Realimentação, versão didática)

---

## 1. Requisitos

- **Python 3.8+** (utiliza apenas a biblioteca padrão do Python: `sys`, `json`, `collections`, `dataclasses`, `typing` e `unittest`).
- Nenhuma dependência externa precisa ser instalada.

---

## 2. Organização do Código e Estruturas de Dados

O projeto foi organizado de forma modular, separando leitura/validação, estruturas de dados, políticas de escalonamento e cálculo de métricas:

| Arquivo | Responsabilidade |
|---|---|
| `simulador.py` | Ponto de entrada da aplicação CLI (`stdin` -> `stdout`), orquestrando validação, simulação e formatação JSON. |
| `validacao.py` | Leitura e validação estrita do JSON de entrada, verificação de tipos, valores, unicidade de IDs e parâmetros obrigatórios (`quantuns` e `boost` no MLFQ). |
| `modelos.py` | Dataclasses que representam `Processo`, `IntervaloLinhaDoTempo` e `MetricaProcesso`. |
| `escalonadores.py` | Implementação dos algoritmos `escalonar_sjf` e `escalonar_mlfq`, além da normalização/união de intervalos adjacentes da linha do tempo. |
| `metricas.py` | Cálculo das métricas individuais (`turnaround`, `espera`, `resposta`) ordenadas por `id` e cálculo das médias aritméticas. |
| `gerar_experimentos.py` | Script utilitário que gera todos os arquivos JSON de entrada e saída dos Experimentos 1, 2 e 3 na pasta `experimentos/`. |
| `test_simulador.py` | Suíte de testes automatizados (`unittest`) validando casos de borda, regras de desempate, boost, preempção e tratamento de entradas inválidas. |
| `RELATORIO.md` | Relatório completo com diagramas de Gantt, tabelas de métricas, conferência manual passo a passo e análises da Seção 7. |

### Estruturas de Dados Utilizadas

1. **Representação de Processos (`Processo` em `modelos.py`):**
   - Cada processo é representado por uma `@dataclass` contendo os atributos fixos de entrada (`id`, `chegada`, `cpu`) e variáveis de estado da simulação (`restante`, `primeira_execucao`, `conclusao`, `fila` e `quantum_usado`).
2. **Escalonador SJF (`escalonar_sjf` em `escalonadores.py`):**
   - Mantém a lista de processos e, a cada instante `t` em que a CPU fica livre, filtra os processos prontos (`conclusao is None` e `chegada <= t`).
   - A seleção utiliza a função `min(prontos, key=lambda p: (p.cpu, p.chegada, p.id))`, garantindo em uma única tupla a escolha pelo menor tempo total de CPU e os critérios gerais de desempate (menor instante de chegada e menor ID em ordem lexicográfica).
3. **Escalonador MLFQ (`escalonar_mlfq` em `escalonadores.py`):**
   - Utiliza três filas `deque` (`collections.deque`), indexadas de `0` a `2` (`filas = [deque(), deque(), deque()]`), permitindo inserções no final (`append`) e remoções no início (`popleft`) em tempo $O(1)$.
   - **Invariante de fila ativa:** o processo em execução na fila `f` permanece na cabeça de sua fila (`filas[f][0]`) enquanto consome sua cota de quantum. Assim:
     - Se um novo processo chegar na fila `0` enquanto um processo da fila `1` ou `2` estiver executando, a fila `0` passa a não vazia e assume a CPU imediatamente (preempção por prioridade), enquanto o processo interrompido permanece exatamente na frente de sua fila (`filas[f][0]`) conservando seu saldo de quantum (`quantum_usado`).
     - Se um novo processo chegar na fila `0` enquanto outro processo já estiver executando na fila `0`, o novo processo entra no final (`filas[0].append(novo)`) e não interrompe o processo atual (`filas[0][0]`).
     - Nos instantes positivos múltiplos de `boost` (`t > 0 and t % boost == 0`), após registrar eventual conclusão e admitir novas chegadas em `t`, todos os processos presentes nas três filas são reunidos, ordenados por `(p.chegada, p.id)` e reinseridos na fila `0` com `quantum_usado = 0`.
4. **Linha do Tempo (` List[IntervaloLinhaDoTempo]`):**
   - Lista sequencial de intervalos `[inicio, fim)`. A função `adicionar_intervalo` verifica se o último intervalo pertence ao mesmo processo e é contíguo (`fim == inicio`), fundindo automaticamente intervalos adjacentes para apresentação sem alterar a contagem interna de quantum ou eventos de boost.

---

## 3. Instruções de Execução

O simulador lê um objeto JSON da **entrada padrão (`stdin`)** e escreve o resultado JSON na **saída padrão (`stdout`)**.

### Linux / macOS / Git Bash / CMD (Windows)

```bash
python simulador.py < experimentos/exp1_comum_sjf_entrada.json > resultado.json
```

```bash
python simulador.py < experimentos/exp1_comum_mlfq_entrada.json > resultado.json
```

### Windows PowerShell

No PowerShell, como o operador `<` é reservado, utilize `Get-Content` com pipe (`|`):

```powershell
Get-Content experimentos/exp1_comum_sjf_entrada.json | python simulador.py > resultado.json
```

### Executar Testes Automatizados e Regerar Experimentos

```bash
python -m unittest discover -v
python gerar_experimentos.py
```

---

## 4. Índice dos Arquivos de Experimentos (`experimentos/`)

| Experimento | Algoritmo | Arquivo de Entrada | Arquivo de Saída |
|---|---|---|---|
| **Exp. 1:** Conjunto Comum (Seção 5.1) | `SJF` | `experimentos/exp1_comum_sjf_entrada.json` | `experimentos/exp1_comum_sjf_saida.json` |
| **Exp. 1:** Conjunto Comum (Seção 5.1) | `MLFQ` | `experimentos/exp1_comum_mlfq_entrada.json` | `experimentos/exp1_comum_mlfq_saida.json` |
| **Exp. 2 (Caso 1):** CPU Ociosa | `SJF` | `experimentos/exp2_caso1_ocioso_sjf_entrada.json` | `experimentos/exp2_caso1_ocioso_sjf_saida.json` |
| **Exp. 2 (Caso 1):** CPU Ociosa | `MLFQ` | `experimentos/exp2_caso1_ocioso_mlfq_entrada.json` | `experimentos/exp2_caso1_ocioso_mlfq_saida.json` |
| **Exp. 2 (Caso 2):** Durações Diferentes | `SJF` | `experimentos/exp2_caso2_duracoes_sjf_entrada.json` | `experimentos/exp2_caso2_duracoes_sjf_saida.json` |
| **Exp. 2 (Caso 2):** Durações Diferentes | `MLFQ` | `experimentos/exp2_caso2_duracoes_mlfq_entrada.json` | `experimentos/exp2_caso2_duracoes_mlfq_saida.json` |
| **Exp. 2 (Caso 3):** Regras de Desempate | `SJF` | `experimentos/exp2_caso3_empates_sjf_entrada.json` | `experimentos/exp2_caso3_empates_sjf_saida.json` |
| **Exp. 2 (Caso 3):** Regras de Desempate | `MLFQ` | `experimentos/exp2_caso3_empates_mlfq_entrada.json` | `experimentos/exp2_caso3_empates_mlfq_saida.json` |
| **Exp. 3 (SJF):** Espera de Longo / Starvation | `SJF` | `experimentos/exp3_sjf_starvation_sjf_entrada.json` | `experimentos/exp3_sjf_starvation_sjf_saida.json` |
| **Exp. 3 (SJF):** Comparativo no MLFQ | `MLFQ` | `experimentos/exp3_sjf_starvation_mlfq_entrada.json` | `experimentos/exp3_sjf_starvation_mlfq_saida.json` |
| **Exp. 3 (MLFQ):** Rebaixamento, Preempção e Boost | `MLFQ` | `experimentos/exp3_mlfq_eventos_mlfq_entrada.json` | `experimentos/exp3_mlfq_eventos_mlfq_saida.json` |
| **Exp. 3 (MLFQ):** Comparativo no SJF | `SJF` | `experimentos/exp3_mlfq_eventos_sjf_entrada.json` | `experimentos/exp3_mlfq_eventos_sjf_saida.json` |
