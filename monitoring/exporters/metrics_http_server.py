# monitoring/exporters/metrics_http_server.py

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
STATUS_DIR = BASE_DIR / "monitoring" / "status"
METRICS_DIR = BASE_DIR / "monitoring" / "metrics"


def load_health_status() -> Dict[str, Any]:
    path = STATUS_DIR / "health_status.json"
    if not path.exists():
        return {
            "status": {
                "engine": "postgres",
                "ok": False,
                "error": "health_status.json not found",
            },
            "metrics": {},
            "timestamp": time.time(),
        }
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def latest_table_sizes_file() -> Optional[Path]:
    if not METRICS_DIR.exists():
        return None
    candidates = sorted(
        METRICS_DIR.glob("table_sizes_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def summarize_table_sizes(path: Path) -> Dict[str, Any]:
    import csv

    summary: Dict[str, Any] = {
        "tables_count": 0,
        "total_bytes": 0,
        "top_tables": [],
    }
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return summary

    summary["tables_count"] = len(rows)
    total_bytes = 0
    for r in rows:
        try:
            total_bytes += int(r.get("total_bytes", 0))
        except ValueError:
            continue
    summary["total_bytes"] = total_bytes

    sorted_rows = sorted(rows, key=lambda r: int(r.get("total_bytes", 0)), reverse=True)[:5]
    summary["top_tables"] = [
        {
            "schema": r.get("schema_name", ""),
            "table": r.get("table_name", ""),
            "total_bytes": int(r.get("total_bytes", 0)),
            "live_rows": int(r.get("live_rows", 0)) if r.get("live_rows") else 0,
        }
        for r in sorted_rows
    ]
    return summary


class MetricsHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: Dict[str, Any], status_code: int = 200) -> None:
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path not in ("/", "/metrics", "/health"):
            self._send_json({"error": "not_found", "path": self.path}, status_code=404)
            return

        health = load_health_status()
        table_summary: Dict[str, Any] = {}
        latest = latest_table_sizes_file()
        if latest:
            table_summary = summarize_table_sizes(latest)

        payload = {
            "timestamp": time.time(),
            "health": health.get("status", {}),
            "db_metrics": health.get("metrics", {}),
            "tables": table_summary,
        }
        self._send_json(payload)


def run_server(host: str = "0.0.0.0", port: int = 9100) -> None:
    server_address = (host, port)
    httpd = HTTPServer(server_address, MetricsHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
