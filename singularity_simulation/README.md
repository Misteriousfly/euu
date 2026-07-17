# Simulação probabilística da singularidade tecnológica

Modelo Monte Carlo auditável para explorar **quando** uma singularidade tecnológica operacional poderia ocorrer e **como** a transição pode pressionar a sociedade.

## O que significa “singularidade” neste projeto

Não significa consciência artificial nem um ponto mágico inevitável. O evento exige quatro condições:

1. IA geral avançada capaz de superar humanos em grande parte do trabalho cognitivo.
2. Aceleração recursiva relevante de pesquisa e desenvolvimento por IA.
3. Computação, energia e infraestrutura suficientes.
4. Difusão ampla na economia e nas instituições.

O modelo inclui ainda a possibilidade de o evento **não ocorrer até 2100** por limites técnicos, guerras, regulação, acidentes, gargalos físicos ou desaceleração econômica.

## Calibração conceitual

- A pesquisa com 2.778 autores de IA estimou 10% de chance de máquinas superarem humanos em todas as tarefas até 2027 e 50% até 2047.
- O AI Index 2026 registra adoção muito rápida da IA generativa, mas adoção não equivale a capacidade geral.
- A Epoch AI registra forte crescimento de compute e eficiência algorítmica, além de possíveis gargalos energéticos e financeiros.
- Ray Kurzweil mantém 2045 como sua previsão de singularidade; o modelo trata isso como um cenário influente, não como fato científico.

Fontes:

- https://arxiv.org/abs/2401.02843
- https://hai.stanford.edu/ai-index/2026-ai-index-report
- https://epoch.ai/trends
- https://epoch.ai/publications/what-will-ai-look-like-in-2030

## Executar

Requer apenas Python 3.10+ e a biblioteca padrão:

```bash
python3 singularity_simulation/simulate.py --runs 100000 --seed 2045 --output singularity_simulation/results
```

Arquivos produzidos:

- `summary.json`: resultados estruturados.
- `timeline_distribution.csv`: probabilidade acumulada anual.
- `REPORT.md`: relatório legível.

## Limites

As distribuições e os pesos são premissas subjetivas documentadas. O resultado serve para análise de cenários e testes de sensibilidade, não para afirmar uma data real ou transformar incerteza radical em precisão falsa.
