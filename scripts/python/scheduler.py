# scripts/python/scheduler.py

import logging
import time
from threading import Thread

import schedule

from backup_runner import run_all_backups
from health_checks import main as health_main
from perf_metrics_collector import main as perf_main
from security_audit import main as audit_main
from db_utils import load_config_global

logger = logging.getLogger("db_admin.scheduler")


def schedule_jobs() -> None:
    cfg = load_config_global()
    sched_cfg = cfg["scheduler"]

    schedule.every(sched_cfg["health_check_interval_minutes"]).minutes.do(health_main)
    schedule.every(sched_cfg["perf_collect_interval_minutes"]).minutes.do(perf_main)
    schedule.every(sched_cfg["backup_check_interval_minutes"]).minutes.do(run_all_backups)
    schedule.every(sched_cfg["security_audit_interval_hours"]).hours.do(audit_main)


def run_scheduler_loop() -> None:
    logger.info("Démarrage du scheduler")
    schedule_jobs()
    while True:
        schedule.run_pending()
        time.sleep(5)


def main() -> None:
    t = Thread(target=run_scheduler_loop, daemon=False)
    t.start()
    t.join()


if __name__ == "__main__":
    main()
