#!/usr/bin/env python3
"""Genera una selección editorial semanal. No afirma medir búsquedas reales."""
from __future__ import annotations
import argparse
import json
import random
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS_FILE = ROOT / "data" / "topics.json"
OUT_DIR = ROOT / "output"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Número de temas a proponer")
    parser.add_argument("--date", default=date.today().isoformat(), help="Fecha YYYY-MM-DD")
    args = parser.parse_args()

    if args.count < 1:
        raise SystemExit("--count debe ser al menos 1")

    topics = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    # Rotación reproducible: cambia por semana, sin fingir que es una métrica de tendencias.
    week_seed = args.date[:7] + "-historia-ai"
    rng = random.Random(week_seed)

    ranked = []
    for item in topics:
        relevance = int(item.get("curriculum_relevance", 1))
        editorial_signal = int(item.get("trend_score", 1))
        # Puntuación editorial interna, NO volumen de búsquedas.
        score = relevance * 0.65 + editorial_signal * 0.25 + rng.random() * 0.10
        ranked.append((score, item))

    ranked.sort(key=lambda pair: pair[0], reverse=True)
    selected = ranked[:args.count]
    OUT_DIR.mkdir(exist_ok=True)

    report = [
        f"# Historia AI — propuestas editoriales ({args.date})",
        "",
        "> Selección inicial basada en relevancia curricular y prioridad editorial manual. "
        "No representa datos reales de búsquedas ni garantiza viralidad.",
        "",
    ]
    for index, (score, item) in enumerate(selected, start=1):
        report += [
            f"## {index}. {item['title']}",
            f"- Área: {item['area']}",
            f"- Periodo: {item['period']}",
            f"- Formato sugerido: {item['format']}",
            f"- Prioridad editorial interna: {score:.2f}/5",
            f"- ID: `{item['id']}`",
            "",
        ]

    report += [
        "## Siguiente paso de producción",
        "Investigar cada tema con al menos dos fuentes fiables, contrastar fechas y conceptos, "
        "y redactar un guion antes de generar cualquier vídeo.",
        "",
    ]
    (OUT_DIR / "weekly_plan.md").write_text("\n".join(report), encoding="utf-8")
    payload = {
        "generated_on": args.date,
        "note": "Puntuación editorial interna; no son datos de búsquedas reales.",
        "items": [{"score": round(score, 3), **item} for score, item in selected],
    }
    (OUT_DIR / "weekly_plan.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Plan generado: {OUT_DIR / 'weekly_plan.md'} ({len(selected)} temas)")

if __name__ == "__main__":
    main()
