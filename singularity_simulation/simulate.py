#!/usr/bin/env python3
"""Monte Carlo scenario model for technological singularity timelines.

This is a transparent scenario simulator, not an empirical prediction engine.
It separates advanced-AI arrival, recursive R&D acceleration, infrastructure,
governance and social diffusion instead of pretending that one trend line is
enough to determine a singularity date.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path


START_YEAR = 2026
HORIZON = 2100

SCENARIOS = {
    "accelerated": {
        "weight": 0.25,
        "agi": (2027, 2030, 2038),
        "recursive_delay": (0.8, 2.5, 6.0),
        "infra_delay": (0.0, 1.0, 4.0),
        "diffusion_delay": (1.0, 3.0, 7.0),
        "blocked_to_2100": 0.10,
        "governance_readiness": (38, 58),
    },
    "central": {
        "weight": 0.50,
        "agi": (2029, 2042, 2060),
        "recursive_delay": (2.0, 6.0, 14.0),
        "infra_delay": (1.0, 4.0, 10.0),
        "diffusion_delay": (2.0, 7.0, 15.0),
        "blocked_to_2100": 0.22,
        "governance_readiness": (48, 72),
    },
    "constrained": {
        "weight": 0.25,
        "agi": (2038, 2058, 2088),
        "recursive_delay": (6.0, 14.0, 30.0),
        "infra_delay": (4.0, 10.0, 24.0),
        "diffusion_delay": (6.0, 15.0, 32.0),
        "blocked_to_2100": 0.38,
        "governance_readiness": (58, 82),
    },
}


def triangular(rng: random.Random, bounds: tuple[float, float, float]) -> float:
    low, mode, high = bounds
    return rng.triangular(low, high, mode)


def choose_scenario(rng: random.Random) -> str:
    roll = rng.random()
    total = 0.0
    for name, cfg in SCENARIOS.items():
        total += cfg["weight"]
        if roll <= total:
            return name
    return "constrained"


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def run_once(rng: random.Random) -> dict:
    scenario = choose_scenario(rng)
    cfg = SCENARIOS[scenario]
    agi_year = triangular(rng, cfg["agi"])

    # A single random systemic shock represents war, hardware bottlenecks,
    # regulatory pauses, energy scarcity or a severe AI incident.
    systemic_shock = rng.random() < cfg["blocked_to_2100"]
    if systemic_shock:
        return {
            "scenario": scenario,
            "agi_year": round(agi_year, 2),
            "singularity_year": None,
            "blocked": True,
        }

    recursive = triangular(rng, cfg["recursive_delay"])
    infrastructure = triangular(rng, cfg["infra_delay"])
    diffusion = triangular(rng, cfg["diffusion_delay"])

    # Gates partly overlap. Recursive R&D is the main clock; infrastructure
    # and diffusion add their non-overlapping residual delays.
    singularity_year = agi_year + recursive + 0.55 * infrastructure + 0.35 * diffusion
    if singularity_year > HORIZON:
        singularity_year = None

    if singularity_year is None:
        return {
            "scenario": scenario,
            "agi_year": round(agi_year, 2),
            "singularity_year": None,
            "blocked": True,
        }

    governance = rng.uniform(*cfg["governance_readiness"])
    transition_speed = clamp(100 - 2.0 * (singularity_year - agi_year))
    concentration = clamp(rng.gauss(64 if scenario != "constrained" else 55, 13))

    impacts = {
        "scientific_acceleration": clamp(rng.gauss(82, 10) + 0.08 * transition_speed),
        "productivity_gain": clamp(rng.gauss(76, 12) + 0.10 * transition_speed),
        "labor_disruption": clamp(rng.gauss(66, 15) + 0.16 * transition_speed - 0.18 * governance),
        "inequality_pressure": clamp(rng.gauss(52, 16) + 0.30 * concentration - 0.25 * governance),
        "information_disorder": clamp(rng.gauss(55, 15) + 0.12 * transition_speed - 0.22 * governance),
        "authoritarian_surveillance_risk": clamp(rng.gauss(43, 17) + 0.24 * concentration - 0.18 * governance),
        "institutional_stress": clamp(rng.gauss(50, 14) + 0.18 * transition_speed - 0.28 * governance),
        "human_agency_erosion": clamp(rng.gauss(46, 17) + 0.15 * transition_speed - 0.15 * governance),
    }

    return {
        "scenario": scenario,
        "agi_year": round(agi_year, 2),
        "singularity_year": round(singularity_year, 2),
        "blocked": False,
        "governance_readiness": round(governance, 2),
        "transition_speed": round(transition_speed, 2),
        "impacts": {k: round(v, 2) for k, v in impacts.items()},
    }


def summarize(samples: list[dict]) -> dict:
    reached = [s for s in samples if s["singularity_year"] is not None]
    years = [s["singularity_year"] for s in reached]
    agi_years = [s["agi_year"] for s in samples]
    impact_names = next((list(s["impacts"]) for s in reached), [])

    cumulative = {
        str(year): round(100 * sum(y <= year for y in years) / len(samples), 2)
        for year in (2030, 2035, 2040, 2045, 2050, 2060, 2075, 2100)
    }
    conditional_impacts = {
        name: {
            "median": round(statistics.median(s["impacts"][name] for s in reached), 1),
            "p10": round(percentile([s["impacts"][name] for s in reached], 0.10), 1),
            "p90": round(percentile([s["impacts"][name] for s in reached], 0.90), 1),
        }
        for name in impact_names
    }

    return {
        "definition": (
            "Operational singularity: advanced general AI plus recursive AI-R&D acceleration, "
            "sufficient compute/energy, and broad societal diffusion; not consciousness or a "
            "literal mathematical discontinuity."
        ),
        "simulation": {
            "runs": len(samples),
            "start_year": START_YEAR,
            "horizon": HORIZON,
            "scenario_counts": dict(Counter(s["scenario"] for s in samples)),
        },
        "agi_year_unconditional": {
            "p10": round(percentile(agi_years, 0.10), 1),
            "median": round(statistics.median(agi_years), 1),
            "p90": round(percentile(agi_years, 0.90), 1),
        },
        "singularity": {
            "probability_by_2100_percent": round(100 * len(reached) / len(samples), 2),
            "probability_not_reached_by_2100_percent": round(100 * (len(samples) - len(reached)) / len(samples), 2),
            "conditional_year_p10": round(percentile(years, 0.10), 1),
            "conditional_year_median": round(statistics.median(years), 1),
            "conditional_year_p90": round(percentile(years, 0.90), 1),
            "unconditional_probability_by_year_percent": cumulative,
        },
        "conditional_societal_impact_indices_0_to_100": conditional_impacts,
        "interpretation_warning": (
            "Outputs are conditional on transparent subjective assumptions. Impact scores are "
            "stress-test indices, not measured probabilities or guaranteed outcomes."
        ),
    }


def write_outputs(output_dir: Path, samples: list[dict], summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    with (output_dir / "timeline_distribution.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["year", "unconditional_probability_percent"])
        for year in range(START_YEAR, HORIZON + 1):
            probability = 100 * sum(
                s["singularity_year"] is not None and s["singularity_year"] <= year for s in samples
            ) / len(samples)
            writer.writerow([year, f"{probability:.3f}"])

    sing = summary["singularity"]
    impacts = summary["conditional_societal_impact_indices_0_to_100"]
    lines = [
        "# Resultado da simulação da singularidade",
        "",
        f"- Execuções Monte Carlo: **{summary['simulation']['runs']:,}**",
        f"- Probabilidade modelada de ocorrer até 2100: **{sing['probability_by_2100_percent']}%**",
        f"- Janela condicional P10–P90: **{sing['conditional_year_p10']}–{sing['conditional_year_p90']}**",
        f"- Mediana condicional: **{sing['conditional_year_median']}**",
        "",
        "## Probabilidade acumulada (inclui cenários sem singularidade até 2100)",
        "",
        "| Ano | Probabilidade |",
        "|---:|---:|",
    ]
    lines.extend(
        f"| {year} | {prob}% |" for year, prob in sing["unconditional_probability_by_year_percent"].items()
    )
    lines.extend(["", "## Impactos sociais condicionais (índice 0–100)", "", "| Domínio | P10 | Mediana | P90 |", "|---|---:|---:|---:|"])
    for name, stats in impacts.items():
        lines.append(f"| {name.replace('_', ' ').title()} | {stats['p10']} | {stats['median']} | {stats['p90']} |")
    lines.extend([
        "",
        "## Leitura correta",
        "",
        "Este modelo não descobre uma data objetiva. Ele transforma premissas explícitas em uma distribuição "
        "reprodutível e permite alterar pesos, atrasos, bloqueios e governança para testar outras visões.",
        "",
    ])
    (output_dir / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=2045)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    if args.runs < 1_000:
        parser.error("--runs must be at least 1000")

    rng = random.Random(args.seed)
    samples = [run_once(rng) for _ in range(args.runs)]
    summary = summarize(samples)
    write_outputs(args.output, samples, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
