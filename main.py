import sys
import asyncio
import logging

import pytz
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.notify import start_reminders, fast_notify
from app.utils.scheduler import setup_scheduler
from app.utils.worker import process_reminders

from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis

from app.filters.admin_filter import AdminProtect

from config import config

from app.handlers.user_message import user
from app.handlers.admin_message import admin
from app.handlers.notify_message import notify

from app.database.models import create_db

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))


async def main():
    print("Bot is starting...")

    redis = await aioredis.from_url(config.redis.redis_url)
    await create_db()

    bot = Bot(token=config.bot.bot_token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=RedisStorage(redis))

    admin.message.middleware(AdminProtect())
    admin.callback_query.middleware(AdminProtect())
    user.message.middleware(AdminProtect())
    user.callback_query.middleware(AdminProtect())
    notify.message.middleware(AdminProtect())
    notify.callback_query.middleware(AdminProtect())

    dp.include_router(user)
    dp.include_router(admin)
    dp.include_router(notify)

    setup_scheduler(
        start_reminders=start_reminders,
        process_reminders=process_reminders,
        bot=bot
    )

    # scheduler.add_job(fast_notify, 'interval', seconds=5, kwargs={'bot': bot})

    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
