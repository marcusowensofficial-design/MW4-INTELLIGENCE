"""
MW4 Weapon Intelligence Lab - APScheduler Background Jobs
Manages automated Parquet snapshot backups and scheduled patch note feed polling.
"""

import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from ..database.connection import db_manager, DatabaseManager


class LabScheduler:
    """Manages periodic snapshot backups and feed checks using APScheduler."""

    def __init__(self, manager: DatabaseManager = db_manager):
        self.manager = manager
        self.scheduler = BackgroundScheduler()
        self.is_running = False

    def trigger_parquet_backup_job(self) -> dict[str, str]:
        """Exports all tables to Parquet snapshot folder."""
        export_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data",
            "snapshots"
        )
        return self.manager.export_all_to_parquet(export_dir)

    def start(self) -> None:
        """Starts background scheduled tasks."""
        if not self.is_running:
            # Run snapshot backup every 60 minutes
            self.scheduler.add_job(
                self.trigger_parquet_backup_job,
                "interval",
                minutes=60,
                id="auto_parquet_backup",
                replace_existing=True
            )
            self.scheduler.start()
            self.is_running = True

    def shutdown(self) -> None:
        """Stops scheduler."""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False


# Singleton scheduler instance
lab_scheduler = LabScheduler()
