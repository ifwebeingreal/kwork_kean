from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def setup_scheduler(start_reminders, process_reminders, bot):
    scheduler.add_job(
        start_reminders,
        trigger="cron",
        hour=9,  # 9
        minute=8,
        args=[bot]
    )

    scheduler.add_job(
        process_reminders,
        trigger="interval",
        seconds=30,
        args=[bot]
    )

    scheduler.start()
