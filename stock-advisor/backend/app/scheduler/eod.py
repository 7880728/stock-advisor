"""EOD scan scheduler — runs daily after market close."""

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings

scheduler = BackgroundScheduler()


def eod_scan_job():
    """Daily end-of-day scan: update data → screen → analyze → generate signals → push."""
    # TODO: implement full pipeline
    pass


def setup_eod_scheduler():
    hour, minute = map(int, settings.eod_scan_time.split(":"))
    scheduler.add_job(
        eod_scan_job,
        "cron",
        hour=hour,
        minute=minute,
        day_of_week="mon-fri",
        id="eod_scan",
    )
    scheduler.start()
