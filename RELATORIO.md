# Relatório de Simulação e Análise Comparativa: SJF vs. MLFQ

**Disciplina:** Sistemas Operacionais  
**Dupla 2:** Gustavo e Andressa  
**Algoritmos analisados:** `SJF` (*Shortest Job First*) e `MLFQ` (*Multilevel Feedback Queue* — Filas Multinível com Realimentação)

---

## Fórmulas das Métricas Adotadas (Seção 6)

Para cada processo $i$, considerando ausência de operações de E/S e custo zero de troca de contexto:

$$\text{Turnaround}_i = \text{Conclusão}_i - \text{Chegada}_i$$

$$\text{Espera}_i = \text{Turnaround}_i - \text{CPU}_i$$

$$\text{Resposta}_i = \text{Primeira Execução}_i - \text{Chegada}_i$$

---

## 1. Experimento 1: Conjunto Comum (Seção 7.1)

### Conjunto de Entrada (Seção 5.1)

| Processo | Chegada | Tempo de CPU |
|---|---|---|
| `P01` | 0 | 8 |
| `P02` | 1 | 4 |
| `P03` | 2 | 2 |
| `P04` | 4 | 1 |

- **Configuração SJF:** `{}`
- **Configuração MLFQ:** `{"quantuns": [2, 4, 8], "boost": 20}`

---

### 1.1. Execução no Algoritmo SJF

- **Arquivos:** `experimentos/exp1_comum_sjf_entrada.json` e `experimentos/exp1_comum_sjf_saida.json`

#### Diagrama de Gantt (SJF)

```text
Tempo:  0               8   9    11        15
        +---------------+---+----+---------+
CPU:    |      P01      |P04|P03 |   P02   |
        +---------------+---+----+---------+
        0               8   9    11        15
```

| Intervalo `[inicio, fim)` | Processo | Duração |
|---|---|---|
| `[0, 8)` | `P01` | 8 |
| `[8, 9)` | `P04` | 1 |
| `[9, 11)` | `P03` | 2 |
| `[11, 15)` | `P02` | 4 |

#### Tabela de Métricas — SJF (Experimento 1)

| Processo | Chegada | CPU | Primeira Execução | Conclusão | Turnaround | Espera | Resposta |
|---|---|---|---|---|---|---|---|
| `P01` | 0 | 8 | 0 | 8 | 8 | 0 | 0 |
| `P02` | 1 | 4 | 11 | 15 | 14 | 10 | 10 |
| `P03` | 2 | 2 | 9 | 11 | 9 | 7 | 7 |
| `P04` | 4 | 1 | 8 | 9 | 5 | 4 | 4 |
| **Médias** | — | — | — | — | **9,00** | **5,25** | **5,25** |

#### Explicação das Decisões de Escalonamento (SJF)

1. **`t = 0`:** Apenas `P01` (`cpu = 8`) chegou. Como a CPU não pode ficar ociosa havendo processo pronto, `P01` inicia sua execução. Por ser **não-preemptivo**, o SJF mantém `P01` até sua conclusão em `t = 8`, mesmo com as chegadas de `P02` (`t = 1`), `P03` (`t = 2`) e `P04` (`t = 4`).
2. **`t = 8`:** `P01` conclui. Os processos prontos são `P02` (`cpu = 4`), `P03` (`cpu = 2`) e `P04` (`cpu = 1`). O SJF escolhe o menor tempo total de CPU: `P04` (`cpu = 1`), que executa em `[8, 9)` e conclui.
3. **`t = 9`:** Restam prontos `P02` (`cpu = 4`) e `P03` (`cpu = 2`). O SJF escolhe `P03` (`cpu = 2`), que executa em `[9, 11)` e conclui.
4. **`t = 11`:** Resta apenas `P02` (`cpu = 4`), que executa em `[11, 15)` e conclui a simulação em `t = 15`.

---

### 1.2. Execução no Algoritmo MLFQ

- **Arquivos:** `experimentos/exp1_comum_mlfq_entrada.json` e `experimentos/exp1_comum_mlfq_saida.json`

#### Diagrama de Gantt (MLFQ)

```text
Tempo:  0     2     4     6   7         11    13    15
        +-----+-----+-----+---+---------+-----+-----+
CPU:    | P01 | P02 | P03 |P04|   P01   | P02 | P01 |
        +-----+-----+-----+---+---------+-----+-----+
Fila:     F0    F0    F0   F0     F1      F1    F2
```

| Intervalo `[inicio, fim)` | Processo | Fila em que executou | Duração |
|---|---|---|---|
| `[0, 2)` | `P01` | Fila 0 (quantum = 2) | 2 |
| `[2, 4)` | `P02` | Fila 0 (quantum = 2) | 2 |
| `[4, 6)` | `P03` | Fila 0 (quantum = 2) | 2 |
| `[6, 7)` | `P04` | Fila 0 (quantum = 2) | 1 |
| `[7, 11)` | `P01` | Fila 1 (quantum = 4) | 4 |
| `[11, 13)` | `P02` | Fila 1 (quantum = 4) | 2 |
| `[13, 15)` | `P01` | Fila 2 (quantum = 8) | 2 |

#### Tabela de Métricas — MLFQ (Experimento 1)

| Processo | Chegada | CPU | Primeira Execução | Conclusão | Turnaround | Espera | Resposta |
|---|---|---|---|---|---|---|---|
| `P01` | 0 | 8 | 0 | 15 | 15 | 7 | 0 |
| `P02` | 1 | 4 | 2 | 13 | 12 | 8 | 1 |
| `P03` | 2 | 2 | 4 | 6 | 4 | 2 | 2 |
| `P04` | 4 | 1 | 6 | 7 | 3 | 2 | 2 |
| **Médias** | — | — | — | — | **8,50** | **4,75** | **1,25** |

#### Explicação das Decisões de Escalonamento (MLFQ)

1. **`t = 0`:** `P01` chega e entra na Fila 0 (`F0 = [P01]`). Executa em `[0, 2)`. Em `t = 1`, `P02` chega na Fila 0 (`F0 = [P01, P02]`), mas chegada à mesma fila não interrompe o processo atual.
2. **`t = 2`:** `P03` chega e entra no final da Fila 0. `P01` esgota seu quantum de 2 unidades na Fila 0 (restam 6 unidades de CPU) e sofre **rebaixamento** para a Fila 1 (`F1 = [P01]`). O próximo da Fila 0 é `P02`, que executa em `[2, 4)`.
3. **`t = 4`:** `P04` chega e entra no final da Fila 0 (`F0 = [P03, P04]`). `P02` esgota seu quantum de 2 unidades na Fila 0 (restam 2 unidades) e é rebaixado para a Fila 1 (`F1 = [P01, P02]`). O próximo da Fila 0 é `P03`, que executa em `[4, 6)` e **conclui** em `t = 6` exatamente ao fim de seu quantum.
4. **`t = 6`:** Ainda na Fila 0, `P04` (`cpu = 1`) executa em `[6, 7)` e **conclui** em `t = 7`.
5. **`t = 7`:** A Fila 0 fica vazia! O escalonador passa a atender a Fila 1 (`F1 = [P01, P02]`). `P01` executa por todo o quantum da Fila 1 (`4` unidades) em `[7, 11)`. Em `t = 11`, ainda restam 2 unidades para `P01`, que é rebaixado para a Fila 2 (`F2 = [P01]`).
6. **`t = 11`:** O próximo da Fila 1 é `P02` (restam 2 unidades). Ele executa em `[11, 13)` e **conclui** em `t = 13` (usando apenas 2 das 4 unidades de quantum da Fila 1).
7. **`t = 13`:** Filas 0 e 1 estão vazias. O escalonador atende a Fila 2 (`F2 = [P01]`). `P01` executa suas 2 unidades finais em `[13, 15)` e **conclui** em `t = 15`. (O boost em `t = 20` não chega a ocorrer pois a simulação termina em `t = 15`).

---

### 1.3. Comparação entre SJF e MLFQ no Experimento 1

| Métrica Média | SJF | MLFQ | Diferença (MLFQ vs. SJF) |
|---|---|---|---|
| **Turnaround Médio** | 9,00 | **8,50** | **Melhorou (-0,50 / -5,6%)** |
| **Espera Média** | 5,25 | **4,75** | **Melhorou (-0,50 / -9,5%)** |
| **Resposta Média** | 5,25 | **1,25** | **Melhorou (-4,00 / -76,2%)** |

**Análise crítica:**
- **Por que o MLFQ superou o SJF em todas as três métricas neste conjunto?** No conjunto da Seção 5.1, o processo mais longo (`P01`, `cpu = 8`) chega em `t = 0`, antes dos processos mais curtos (`P02`, `P03`, `P04`). Como o SJF é **não-preemptivo**, ele fica preso executando `P01` durante todo o intervalo `[0, 8)`, causando o **efeito comboio (*convoy effect*)**: `P02`, `P03` e `P04` aguardam até `t = 8` para começar.
- Já o **MLFQ**, ao atribuir um quantum curto (`2` unidades) na Fila 0, rebaixa `P01` em `t = 2`, permitindo que `P02`, `P03` e `P04` recebam a CPU quase imediatamente (reduzindo o tempo de resposta médio de `5,25` para `1,25`) e fazendo com que `P03` e `P04` concluam já em `t = 6` e `t = 7`, o que também reduziu as médias de espera (`4,75` vs `5,25`) e de turnaround (`8,50` vs `9,00`).

---

## 2. Experimento 2: Casos Elaborados pela Dupla (Seção 7.2)

Foram elaborados três casos de teste adicionais para exercitar cenários específicos do modelo de simulação.

---

### 2.1. Caso 1: CPU Ociosa no Início e Entre Chegadas

- **Objetivo:** Verificar o registro correto do estado reservado `"OCIOSO"` tanto no início da simulação (quando a primeira chegada ocorre em `t > 0`, conforme Seção 5.2) quanto em lacunas intermediárias quando todos os processos anteriores já concluíram e o próximo ainda não chegou.
- **Arquivos:** `experimentos/exp2_caso1_ocioso_sjf_{entrada,saida}.json` e `experimentos/exp2_caso1_ocioso_mlfq_{entrada,saida}.json`

#### Processos de Entrada (Caso 1)

| Processo | Chegada | CPU |
|---|---|---|
| `P01` | 2 | 3 |
| `P02` | 3 | 2 |
| `P03` | 9 | 4 |
| `P04` | 10 | 1 |

#### Diagramas de Gantt (Caso 1)

**SJF:**
```text
Tempo:  0       2       5     7       9        13  14
        +-------+-------+-----+-------+---------+---+
CPU:    |OCIOSO |  P01  | P02 |OCIOSO |   P03   |P04|
        +-------+-------+-----+-------+---------+---+
```

**MLFQ (`quantuns = [2, 4, 8]`, `boost = 20`):**
```text
Tempo:  0       2     4     6   7       9     11  12    14
        +-------+-----+-----+---+-------+-----+---+-----+
CPU:    |OCIOSO | P01 | P02 |P01|OCIOSO | P03 |P04| P03 |
        +-------+-----+-----+---+-------+-----+---+-----+
Fila:      --     F0    F0   F1    --     F0   F0   F1
```

#### Tabelas de Métricas (Caso 1)

| Processo | SJF: 1ª Exec | SJF: Concl. | SJF: Turn. | SJF: Esp. | SJF: Resp. | MLFQ: 1ª Exec | MLFQ: Concl. | MLFQ: Turn. | MLFQ: Esp. | MLFQ: Resp. |
|---|---|---|---|---|---|---|---|---|---|---|
| `P01` | 2 | 5 | 3 | 0 | 0 | 2 | 7 | 5 | 2 | 0 |
| `P02` | 5 | 7 | 4 | 2 | 2 | 4 | 6 | 3 | 1 | 1 |
| `P03` | 9 | 13 | 4 | 0 | 0 | 9 | 14 | 5 | 1 | 0 |
| `P04` | 13 | 14 | 4 | 3 | 3 | 11 | 12 | 2 | 1 | 1 |
| **Médias** | — | — | **3,75** | **1,25** | **1,25** | — | — | **3,75** | **1,25** | **0,50** |

**Observação:** Nos dois algoritmos, os intervalos `[0, 2)` e `[7, 9)` são corretamente registrados como `"OCIOSO"`. As médias de turnaround (`3,75`) e espera (`1,25`) empataram, mas o MLFQ reduziu o tempo de resposta médio pela metade (`0,50` contra `1,25`).

---

### 2.2. Caso 2: Processos de Durações Diferentes com Chegadas Durante a Execução

- **Objetivo:** Demonstrar um cenário em que um processo longo (`P01`, `cpu = 10`) inicia em `t = 0` e três processos de durações variadas (`cpu = 6, 2, 4`) chegam durante sua execução. No SJF, a escolha ótima entre os processos prontos após `t = 10` (`P03 -> P04 -> P02`) minimiza o tempo de espera médio em comparação à alternância das filas do MLFQ.
- **Arquivos:** `experimentos/exp2_caso2_duracoes_sjf_{entrada,saida}.json` e `experimentos/exp2_caso2_duracoes_mlfq_{entrada,saida}.json`

#### Processos de Entrada (Caso 2)

| Processo | Chegada | CPU |
|---|---|---|
| `P01` | 0 | 10 |
| `P02` | 1 | 6 |
| `P03` | 2 | 2 |
| `P04` | 3 | 4 |

#### Diagramas de Gantt (Caso 2)

**SJF:**
```text
Tempo:  0          10    12      16        22
        +-----------+-----+-------+---------+
CPU:    |    P01    | P03 |  P04  |   P02   |
        +-----------+-----+-------+---------+
```

**MLFQ (`quantuns = [2, 4, 8]`, `boost = 20`):**
```text
Tempo:  0    2    4    6    8      12      16    18      22
        +----+----+----+----+-------+-------+-----+-------+
CPU:    |P01 |P02 |P03 |P04 |  P01  |  P02  | P04 |  P01  |
        +----+----+----+----+-------+-------+-----+-------+
Fila:    F0   F0   F0   F0     F1      F1     F1   F2/F0*
```
*\*Nota sobre `[18, 22)` no MLFQ:* `P01` executa `[18, 20)` na Fila 2 (consumindo 2 unidades) e, em `t = 20`, ocorre o **boost**, que move `P01` (único processo restante) para a Fila 0, onde executa `[20, 22)` e conclui. Pela regra de normalização da Seção 5.2, os intervalos contíguos `[18, 20)` e `[20, 22)` de `P01` são unidos na linha do tempo em `[18, 22)`.

#### Tabelas de Métricas (Caso 2)

| Processo | SJF: 1ª Exec | SJF: Concl. | SJF: Turn. | SJF: Esp. | SJF: Resp. | MLFQ: 1ª Exec | MLFQ: Concl. | MLFQ: Turn. | MLFQ: Esp. | MLFQ: Resp. |
|---|---|---|---|---|---|---|---|---|---|---|
| `P01` | 0 | 10 | 10 | 0 | 0 | 0 | 22 | 22 | 12 | 0 |
| `P02` | 16 | 22 | 21 | 15 | 15 | 2 | 16 | 15 | 9 | 1 |
| `P03` | 10 | 12 | 10 | 8 | 8 | 4 | 6 | 4 | 2 | 2 |
| `P04` | 12 | 16 | 13 | 9 | 9 | 6 | 18 | 15 | 11 | 3 |
| **Médias** | — | — | **13,50** | **8,00** | **8,00** | — | — | **14,00** | **8,50** | **1,50** |

**Análise:** Aqui observa-se o *trade-off* clássico entre os dois algoritmos: o **SJF** obteve menor **turnaround médio (`13,50` vs `14,00`)** e menor **espera média (`8,00` vs `8,50`)**, pois a partir de `t = 10` executou `P03`, `P04` e `P02` estritamente em ordem crescente de duração sem fatiá-los. Em contrapartida, o **MLFQ** reduziu drasticamente a **resposta média (`1,50` vs `8,00`)**.

---

### 2.3. Caso 3: Empates Exercitando Regras de Desempate (com Conferência Manual)

- **Objetivo:** Exercitar rigorosamente as duas regras de desempate da Seção 3:
  1. Menor instante de chegada (`chegada`);
  2. Menor identificador em ordem lexicográfica (`id`).
  Além disso, os processos foram gravados no arquivo JSON fora de ordem (`P03, P01, P04, P02`) para comprovar que a ordem no arquivo de entrada não interfere nas decisões de escalonamento.
- **Arquivos:** `experimentos/exp2_caso3_empates_sjf_{entrada,saida}.json` e `experimentos/exp2_caso3_empates_mlfq_{entrada,saida}.json`

#### Processos de Entrada (Caso 3 — na ordem exata do arquivo JSON)

| Ordem no JSON | Processo | Chegada | CPU | Motivo no Teste de Desempate |
|---|---|---|---|---|
| 1º | `P03` | 1 | 3 | Empata em `cpu = 3` e `chegada = 1` com `P02` (perde no desempate por ID: `"P02" < "P03"`). |
| 2º | `P01` | 0 | 5 | Único processo pronto em `t = 0`. |
| 3º | `P04` | 2 | 3 | Empata em `cpu = 3` com `P02` e `P03`, mas tem `chegada = 2 > 1` (perde por chegada). |
| 4º | `P02` | 1 | 3 | Empata em `cpu = 3` e `chegada = 1` com `P03` (vence no desempate por ID: `"P02" < "P03"`). |

#### Diagramas de Gantt (Caso 3)

**SJF:**
```text
Tempo:  0         5       8      11      14
        +---------+-------+-------+-------+
CPU:    |   P01   |  P02  |  P03  |  P04  |
        +---------+-------+-------+-------+
```

**MLFQ (`quantuns = [2, 4, 8]`, `boost = 20`):**
```text
Tempo:  0     2     4     6     8       11  12  13  14
        +-----+-----+-----+-----+-------+---+---+---+
CPU:    | P01 | P02 | P03 | P04 |  P01  |P02|P03|P04|
        +-----+-----+-----+-----+-------+---+---+---+
Fila:     F0    F0    F0    F0     F1    F1  F1  F1
```

---

### 2.4. Conferência Manual Passo a Passo do Caso 3 (Seção 7.2)

Abaixo realizamos a conferência manual completa do **Caso 3** nos dois algoritmos para comprovar a exatidão da linha do tempo e das métricas geradas pelo simulador.

#### A) Conferência Manual no SJF

1. **Rastreamento da Linha do Tempo:**
   - **`t = 0`:** Único processo com `chegada <= 0` é `P01` (`chegada = 0, cpu = 5`).
     - `P01` inicia em `t = 0` (`primeira_execucao = 0`) e executa sem preempção até `t = 0 + 5 = 5` (`conclusao = 5`).
     - Intervalo 1: `["P01", 0, 5)`.
   - **`t = 5`:** Processos prontos (`chegada <= 5` e não concluídos):
     - `P03`: `(cpu=3, chegada=1, id="P03")`
     - `P04`: `(cpu=3, chegada=2, id="P04")`
     - `P02`: `(cpu=3, chegada=1, id="P02")`
     - Todos os três empatam no critério principal do SJF (`cpu = 3`).
     - **1º Desempate (menor chegada):** `P02` e `P03` têm `chegada = 1`, vencendo `P04` (`chegada = 2`).
     - **2º Desempate (ordem lexicográfica de ID):** entre `P02` e `P03`, `"P02" < "P03"`. Logo, `P02` é escolhido!
     - `P02` executa de `t = 5` (`primeira_execucao = 5`) até `t = 5 + 3 = 8` (`conclusao = 8`).
     - Intervalo 2: `["P02", 5, 8)`.
   - **`t = 8`:** Processos prontos: `P03` (`cpu=3, chegada=1`) e `P04` (`cpu=3, chegada=2`).
     - Empate em `cpu = 3`. Desempate pelo menor instante de chegada (`1 < 2`): `P03` é escolhido!
     - `P03` executa de `t = 8` (`primeira_execucao = 8`) até `t = 8 + 3 = 11` (`conclusao = 11`).
     - Intervalo 3: `["P03", 8, 11)`.
   - **`t = 11`:** Único processo restante é `P04` (`cpu = 3`).
     - `P04` executa de `t = 11` (`primeira_execucao = 11`) até `t = 11 + 3 = 14` (`conclusao = 14`).
     - Intervalo 4: `["P04", 11, 14)`.

2. **Cálculo Manual das Métricas Individuais (SJF — Caso 3):**
   - **`P01` (`chegada = 0, cpu = 5, primeira_execucao = 0, conclusao = 5`):**
     - $\text{Turnaround} = 5 - 0 = 5$
     - $\text{Espera} = 5 - 5 = 0$
     - $\text{Resposta} = 0 - 0 = 0$
   - **`P02` (`chegada = 1, cpu = 3, primeira_execucao = 5, conclusao = 8`):**
     - $\text{Turnaround} = 8 - 1 = 7$
     - $\text{Espera} = 7 - 3 = 4$
     - $\text{Resposta} = 5 - 1 = 4$
   - **`P03` (`chegada = 1, cpu = 3, primeira_execucao = 8, conclusao = 11`):**
     - $\text{Turnaround} = 11 - 1 = 10$
     - $\text{Espera} = 10 - 3 = 7$
     - $\text{Resposta} = 8 - 1 = 7$
   - **`P04` (`chegada = 2, cpu = 3, primeira_execucao = 11, conclusao = 14`):**
     - $\text{Turnaround} = 14 - 2 = 12$
     - $\text{Espera} = 12 - 3 = 9$
     - $\text{Resposta} = 11 - 2 = 9$
   - **Médias Manuais (SJF):**
     - $\text{Média Turnaround} = \frac{5 + 7 + 10 + 12}{4} = \frac{34}{4} = 8,5$
     - $\text{Média Espera} = \frac{0 + 4 + 7 + 9}{4} = \frac{20}{4} = 5,0$
     - $\text{Média Resposta} = \frac{0 + 4 + 7 + 9}{4} = \frac{20}{4} = 5,0$
   - *Resultado idêntico ao arquivo `experimentos/exp2_caso3_empates_sjf_saida.json`.*

#### B) Conferência Manual no MLFQ (`quantuns = [2, 4, 8]`, `boost = 20`)

1. **Rastreamento da Linha do Tempo:**
   - **`t = 0`:** `P01` chega e entra em `F0 = [P01]`. Inicia em `t = 0` (`primeira_execucao = 0`).
   - **`t = 1`:** `P02` e `P03` chegam simultaneamente em `t = 1`. Pela regra de desempate (`menor chegada`, depois `ID lexicográfico`), entram na Fila 0 na ordem `P02`, depois `P03` (`F0 = [P01, P02, P03]`). `P01` continua executando sua 2ª unidade na Fila 0.
   - **`t = 2`:**
     - `P01` completa 2 unidades (`[0, 2)`), restam `5 - 2 = 3`.
     - `P04` chega em `t = 2` e entra no final da Fila 0 (`F0 = [P01, P02, P03, P04]`).
     - `P01` esgotou o quantum `2` da Fila 0 e desce para a Fila 1 (`F1 = [P01]`, `F0 = [P02, P03, P04]`).
     - `P02` assume a CPU (`primeira_execucao = 2`) e executa `[2, 4)` na Fila 0.
   - **`t = 4`:** `P02` esgota o quantum `2` da Fila 0 (resta `3 - 2 = 1`) e desce para a Fila 1 (`F1 = [P01, P02]`). `P03` assume a CPU (`primeira_execucao = 4`) e executa `[4, 6)` na Fila 0.
   - **`t = 6`:** `P03` esgota o quantum `2` da Fila 0 (resta `3 - 2 = 1`) e desce para a Fila 1 (`F1 = [P01, P02, P03]`). `P04` assume a CPU (`primeira_execucao = 6`) e executa `[6, 8)` na Fila 0.
   - **`t = 8`:** `P04` esgota o quantum `2` da Fila 0 (resta `3 - 2 = 1`) e desce para a Fila 1 (`F1 = [P01, P02, P03, P04]`). Fila 0 agora está vazia!
   - **`[8, 11)`:** Na Fila 1 (`quantum = 4`), `P01` precisa de apenas `3` unidades restantes; executa `[8, 11)` e conclui em `t = 11` (`conclusao = 11`).
   - **`[11, 12)`:** `P02` (resta `1`) executa na Fila 1 e conclui em `t = 12` (`conclusao = 12`).
   - **`[12, 13)`:** `P03` (resta `1`) executa na Fila 1 e conclui em `t = 13` (`conclusao = 13`).
   - **`[13, 14)`:** `P04` (resta `1`) executa na Fila 1 e conclui em `t = 14` (`conclusao = 14`).

2. **Cálculo Manual das Métricas Individuais (MLFQ — Caso 3):**
   - **`P01` (`chegada = 0, cpu = 5, 1ª exec = 0, conclusao = 11`):** $\text{Turnaround} = 11 - 0 = 11$, $\text{Espera} = 11 - 5 = 6$, $\text{Resposta} = 0 - 0 = 0$.
   - **`P02` (`chegada = 1, cpu = 3, 1ª exec = 2, conclusao = 12`):** $\text{Turnaround} = 12 - 1 = 11$, $\text{Espera} = 11 - 3 = 8$, $\text{Resposta} = 2 - 1 = 1$.
   - **`P03` (`chegada = 1, cpu = 3, 1ª exec = 4, conclusao = 13`):** $\text{Turnaround} = 13 - 1 = 12$, $\text{Espera} = 12 - 3 = 9$, $\text{Resposta} = 4 - 1 = 3$.
   - **`P04` (`chegada = 2, cpu = 3, 1ª exec = 6, conclusao = 14`):** $\text{Turnaround} = 14 - 2 = 12$, $\text{Espera} = 12 - 3 = 9$, $\text{Resposta} = 6 - 2 = 4$.
   - **Médias Manuais (MLFQ):**
     - $\text{Média Turnaround} = \frac{11 + 11 + 12 + 12}{4} = \frac{46}{4} = 11,5$
     - $\text{Média Espera} = \frac{6 + 8 + 9 + 9}{4} = \frac{32}{4} = 8,0$
     - $\text{Média Resposta} = \frac{0 + 1 + 3 + 4}{4} = \frac{8}{4} = 2,0$
   - *Resultado idêntico ao arquivo `experimentos/exp2_caso3_empates_mlfq_saida.json`.*

---

## 3. Experimento 3: Características dos Algoritmos Atribuídos (Seção 7.3)

---

### 3.1. Análise Específica do SJF: Postergação de Processo Longo e *Starvation*

> **Solicitação (Seção 7.3 — SJF):** *"Mostrar como um processo longo pode esperar enquanto processos curtos são escolhidos. Explicar quando chegadas contínuas podem causar starvation."*

- **Arquivos:** `experimentos/exp3_sjf_starvation_sjf_{entrada,saida}.json` (e comparativo `experimentos/exp3_sjf_starvation_mlfq_{entrada,saida}.json`)

#### Processos de Entrada

| Processo | Chegada | CPU | Perfil |
|---|---|---|---|
| `P01` | 0 | 3 | Curto inicial (ocupa a CPU em `[0, 3)`) |
| `P02` | 1 | **12** | **Processo longo** (chega em `t = 1`, logo após o início de `P01`) |
| `P03` | 2 | 2 | Curto (chega antes de `P01` terminar) |
| `P04` | 4 | 1 | Muito curto (chega enquanto `P03` executa) |
| `P05` | 5 | 2 | Curto (chega quando `P03` termina) |
| `P06` | 7 | 2 | Curto (chega enquanto `P05` executa) |

#### Diagrama de Gantt no SJF

```text
Tempo:  0       3     5   6     8    10                      22
        +-------+-----+---+-----+-----+-----------------------+
CPU:    |  P01  | P03 |P04| P05 | P06 |          P02          |
        +-------+-----+---+-----+-----+-----------------------+
                  ^
          P02 (cpu=12) já estava pronto desde t=1, mas foi
          ultrapassado por P03, P04, P05 e P06!
```

#### Tabela de Métricas — Experimento 3 (SJF vs. MLFQ na mesma carga)

| Processo | Chegada | CPU | SJF: 1ª Exec | SJF: Concl. | SJF: Espera | SJF: Resp. | MLFQ: 1ª Exec | MLFQ: Concl. | MLFQ: Espera | MLFQ: Resp. |
|---|---|---|---|---|---|---|---|---|---|---|
| `P01` | 0 | 3 | 0 | 3 | 0 | 0 | 0 | 12 | 9 | 0 |
| **`P02` (Longo)** | **1** | **12** | **10** | **22** | **9** | **9** | **2** | **22** | **9** | **1** |
| `P03` | 2 | 2 | 3 | 5 | 1 | 1 | 4 | 6 | 2 | 2 |
| `P04` | 4 | 1 | 5 | 6 | 1 | 1 | 6 | 7 | 2 | 2 |
| `P05` | 5 | 2 | 6 | 8 | 1 | 1 | 7 | 9 | 2 | 2 |
| `P06` | 7 | 2 | 8 | 10 | 1 | 1 | 9 | 11 | 2 | 2 |
| **Médias** | — | — | — | — | **2,17** | **2,17** | — | — | **4,33** | **1,50** |

#### Explicação Técnica: Por que `P02` espera e quando ocorre *Starvation*?

1. **Como o processo longo espera neste experimento:**
   - `P02` (`cpu = 12`) chega em `t = 1`, enquanto `P01` (`[0, 3)`) está na CPU.
   - Em `t = 3`, quando a CPU fica livre, `P03` (`cpu = 2`, chegou em `t = 2`) já está pronto e é escolhido no lugar de `P02` (`2 < 12`).
   - Durante a execução de `P03` (`[3, 5)`), chegam `P04` (`t = 4, cpu = 1`) e `P05` (`t = 5, cpu = 2`). Assim, em `t = 5` `P04` é escolhido (`[5, 6)`) e em `t = 6` `P05` é escolhido (`[6, 8)`).
   - Durante a execução de `P05`, chega `P06` (`t = 7, cpu = 2`), que é escolhido em `t = 8` (`[8, 10)`).
   - Embora `P02` tenha sido o **segundo processo a chegar no sistema (`t = 1`)**, ele é o **último a iniciar (`t = 10`)**, sofrendo tempo de resposta igual a `9` unidades. No MLFQ, por outro lado, `P02` entra na Fila 0 em `t = 1` e recebe sua primeira fatia de CPU já em `t = 2` (`resposta = 1`).
2. **Quando chegadas contínuas causam *Starvation* (Inanição):**
   - No SJF, um processo longo $P_L$ com tempo de CPU $C_L$ permanece indefinidamente na fila de prontos (sofrendo **starvation / inanição**) sempre que, antes do término do processo curto atualmente em execução, chegar ao menos um novo processo com tempo de CPU $C_i < C_L$.
   - Formalmente, se em todo instante de conclusão $t_k$ o conjunto de processos prontos $\{P_i \mid \text{chegada}_i \le t_k \text{ e } C_i < C_L\}$ for não vazio, a função de seleção do SJF jamais escolherá $P_L$. Em um sistema real com fluxo contínuo de tarefas curtas (como requisições interativas ou *jobs* rápidos), o tempo de espera de $P_L$ tende ao infinito ($\text{Espera}(P_L) \to \infty$), impedindo sua execução.

---

### 3.2. Análise Específica do MLFQ: Rebaixamento, Interrupção por Prioridade e Boost

> **Solicitação (Seção 7.3 — MLFQ):** *"Mostrar um rebaixamento, uma interrupção por prioridade e um boost. Usar processos longos o suficiente para que os três eventos ocorram."*

- **Arquivos:** `experimentos/exp3_mlfq_eventos_mlfq_{entrada,saida}.json` (e comparativo `experimentos/exp3_mlfq_eventos_sjf_{entrada,saida}.json`)
- **Configuração MLFQ:** `{"quantuns": [2, 4, 8], "boost": 20}`

#### Processos de Entrada

| Processo | Chegada | CPU | Objetivo no Experimento |
|---|---|---|---|
| `P01` | 0 | 18 | Processo longo que sofre rebaixamento em `t = 2`, é interrompido na Fila 1 em `t = 3` (conservando saldo de quantum), desce à Fila 2 em `t = 8` e recebe boost em `t = 20`. |
| `P02` | 3 | 12 | Chega na Fila 0 em `t = 3` provocando **interrupção por prioridade** sobre `P01` (que executava na Fila 1), sofre rebaixamentos em `t = 5` e `t = 12`, e recebe boost em `t = 20`. |

#### Diagrama de Gantt Detalhado (Interno vs. Linha do Tempo Normalizada)

```text
Eventos:  t=0     t=2    t=3     t=5       t=8         t=12                t=20    t=22    t=24    t=26        t=30
           |       |      |       |         |           |                   |       |       |       |           |
Interno:   |  P01  | P01  |  P02  |   P01   |    P02    |        P01        |  P01  |  P02  |  P01  |    P02    |
Fila:      | F0(2) |F1(1/4| F0(2) | F1(3/4) |   F1(4)   |       F2(8)       | F0(2) | F0(2) | F1(2) |   F1(4)   |
           +-------+------+-------+---------+-----------+-------------------+-------+-------+-------+-----------+
Saída JSON:|     P01      |  P02  |   P01   |    P02    |            P01            |  P02  |  P01  |    P02    |
Intervalo: [0, 3)          [3, 5)  [5, 8)    [8, 12)     [12, 22)                    [22,24) [24,26) [26, 30)
```

> **Nota sobre a união de intervalos adjacentes (Seção 5.2):** Nos instantes `t = 2` (`[0, 2)` na Fila 0 + `[2, 3)` na Fila 1 -> `[0, 3)`) e `t = 20` (`[12, 20)` na Fila 2 + `[20, 22)` na Fila 0 após o boost -> `[12, 22)`), o mesmo processo (`P01`) continuou na CPU em fatias consecutivas sem outro processo executar entre elas. Conforme exigido pela Seção 5.2 (*"Unir intervalos adjacentes do mesmo processo"*), a saída JSON apresenta `[0, 3)` e `[12, 22)`.

#### Rastreamento dos Três Eventos Obrigatórios do MLFQ

1. **Evento 1 — Rebaixamento de Fila (`t = 2`, `t = 5`, `t = 8`, `t = 12`, `t = 22`, `t = 24`):**
   - Em `t = 0`, `P01` entra na Fila 0 (`quantum = 2`).
   - Em **`t = 2`**, após executar `[0, 2)`, `P01` consumiu integralmente as `2` unidades de quantum da Fila 0 sem concluir (`restante = 16`). Ele sofre **rebaixamento** da Fila 0 para a Fila 1 (`quantum = 4`). Como a Fila 0 está vazia em `t = 2`, `P01` inicia imediatamente sua execução na Fila 1 durante `[2, 3)`.

2. **Evento 2 — Interrupção por Prioridade e Conservação do Saldo de Quantum (`t = 3` e retomada em `t = 5`):**
   - Em **`t = 3`**, `P01` está executando na **Fila 1** e consumiu apenas `1` das `4` unidades de sua cota na Fila 1 (`saldo restante = 3`, `CPU restante = 15`).
   - Nesse exato instante `t = 3`, `P02` chega no sistema e entra na **Fila 0** (maior prioridade).
   - Ocorre a **interrupção por prioridade (preempção)**: `P01` é interrompido imediatamente em `t = 3`, **permanece na frente da Fila 1** e **conserva seu saldo de quantum de 3 unidades** (sua cota não é reiniciada).
   - `P02` executa na Fila 0 durante `[3, 5)`. Em `t = 5`, `P02` esgota seu quantum de 2 unidades na Fila 0 e é rebaixado para o **final da Fila 1** (`F1 = [P01, P02]`).
   - Em **`t = 5`**, com a Fila 0 vazia, `P01` (que permaneceu na frente da Fila 1!) retoma a CPU e executa apenas as **3 unidades restantes** de sua cota da Fila 1 no intervalo `[5, 8)`. Em `t = 8`, tendo completado `1 + 3 = 4` unidades na Fila 1, `P01` é rebaixado para a Fila 2 (`restante = 12`), e `P02` executa suas 4 unidades na Fila 1 em `[8, 12)` antes de também descer para a Fila 2 (`restante = 6`).

3. **Evento 3 — Priority Boost (`t = 20`):**
   - No intervalo `[12, 20)`, as Filas 0 e 1 estão vazias e `P01` executa na Fila 2 por 8 unidades (`restante = 4`).
   - Em **`t = 20`** (`t > 0` e múltiplo de `boost = 20`), ocorre o **Priority Boost**!
   - Pela regra da Seção 4.5 (*"Se boost, chegada e fim de quantum coincidirem, processar eventual conclusão, admitir as chegadas e aplicar o boost. O boost prevalece sobre o rebaixamento. No boost, ordenar os processos pelo instante de chegada e pelo ID"*):
     - Sem o boost, `P01` iria para o final da Fila 2 e `P02` assumiria a CPU em `t = 20`.
     - Com o boost em `t = 20`, tanto `P01` (`restante = 4`) quanto `P02` (`restante = 6`) são movidos para a **Fila 0**, têm suas cotas reiniciadas (`quantum = 2`) e são ordenados por `(chegada, id)` -> `F0 = [P01, P02]`.
   - Assim, `P01` executa `[20, 22)` na Fila 0 (rebaixado para Fila 1 em `t = 22` com `restante = 2`), `P02` executa `[22, 24)` na Fila 0 (rebaixado para Fila 1 em `t = 24` com `restante = 4`), `P01` executa `[24, 26)` na Fila 1 e **conclui em `t = 26`**, e `P02` executa `[26, 30)` na Fila 1 e **conclui em `t = 30`**.

#### Tabela de Métricas — Experimento 3 (MLFQ Eventos vs. SJF)

| Processo | Chegada | CPU | MLFQ: 1ª Exec | MLFQ: Concl. | MLFQ: Turn. | MLFQ: Esp. | MLFQ: Resp. | SJF: 1ª Exec | SJF: Concl. | SJF: Turn. | SJF: Esp. | SJF: Resp. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `P01` | 0 | 18 | 0 | 26 | 26 | 8 | 0 | 0 | 18 | 18 | 0 | 0 |
| `P02` | 3 | 12 | 3 | 30 | 27 | 15 | 0 | 18 | 30 | 27 | 15 | 15 |
| **Médias** | — | — | — | — | **26,50** | **11,50** | **0,00** | — | — | **22,50** | **7,50** | **7,50** |

**Conclusão Geral dos Experimentos:**
Os resultados demonstram que nenhum algoritmo é universalmente superior em todas as métricas para qualquer carga de trabalho:
- O **SJF** minimiza o tempo médio de espera e de turnaround entre processos já disponíveis na fila de prontos, mas sofre com o efeito comboio quando um processo longo chega primeiro (Experimento 1) e pode causar *starvation* de processos longos diante da chegada contínua de processos curtos (Experimento 3 — SJF).
- O **MLFQ** proporciona excelente **tempo de resposta** em todos os cenários avaliados (sem precisar conhecer a duração de CPU a priori na vida real), priorizando processos recém-chegados ou interativos na Fila 0, adaptando a prioridade por meio do rebaixamento daqueles que consomem todo o quantum e prevenindo *starvation* por meio do mecanismo periódico de *boost*.
