# scripts/python/generate_reports.py

import csv
import datetime as dt
from pathlib import Path

from db_utils import BASE_DIR


def _find_latest(dir_path: Path, pattern: str):
    candidates = sorted(dir_path.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _load_csv(path: Path):
    rows = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def build_perf_report_md() -> str:
    metrics_dir = BASE_DIR / "monitoring" / "metrics"
    latest = _find_latest(metrics_dir, "table_sizes_*.csv")
    if not latest:
        return "# Rapport performance\n\nAucune donnée disponible."

    rows = _load_csv(latest)
    report_lines = [
        "# Rapport de performance des bases",
        "",
        f"Fichier source: `{latest.name}`",
        f"Date de génération: {dt.datetime.now().isoformat()}",
        "",
        "## Top 10 tables par taille",
        "",
        "| Schéma | Table | Taille totale (octets) | Lignes estimées |",
        "|--------|-------|------------------------|-----------------|",
    ]

    sorted_rows = sorted(rows, key=lambda r: int(r["total_bytes"]), reverse=True)[:10]
    for r in sorted_rows:
        report_lines.append(
            f"| {r['schema_name']} | {r['table_name']} | {r['total_bytes']} | {r.get('live_rows', '')} |"
        )

    return "\n".join(report_lines)


def build_security_report_md() -> str:
    audit_dir = BASE_DIR / "security" / "audit_results"
    if not audit_dir.exists():
        return "# Rapport de sécurité\n\nAucun audit disponible."

    parts = ["# Rapport de sécurité", "", f"Date de génération: {dt.datetime.now().isoformat()}", ""]

    for csv_file in sorted(audit_dir.glob("*.csv")):
        rows = _load_csv(csv_file)
        title = csv_file.stem
        parts.append(f"## {title}")
        parts.append("")
        if not rows:
            parts.append("Aucune anomalie détectée.")
            parts.append("")
            continue

        fieldnames = list(rows[0].keys())
        header = "|" + "|".join(fieldnames) + "|"
        sep = "|" + "|".join("---" for _ in fieldnames) + "|"
        parts.append(header)
        parts.append(sep)
        for r in rows[:50]:
            parts.append("|" + "|".join(str(r.get(k, "")) for k in fieldnames) + "|")
        if len(rows) > 50:
            parts.append("")
            parts.append(f"_Affichage limité à 50 lignes sur {len(rows)}._")
        parts.append("")

    return "\n".join(parts)


def main() -> None:
    reports_dir = BASE_DIR / "monitoring" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    perf_md = build_perf_report_md()
    security_md = build_security_report_md()

    perf_path = reports_dir / "rapport_performance.md"
    sec_path = reports_dir / "rapport_securite.md"

    perf_path.write_text(perf_md, encoding="utf-8")
    sec_path.write_text(security_md, encoding="utf-8")


if __name__ == "__main__":
    main()
