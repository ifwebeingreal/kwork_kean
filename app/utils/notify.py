from datetime import datetime, date, timedelta
from aiogram import Bot

from app.database.requests.notify.delete import delete_notify
from app.database.requests.user.select import get_users_for_start
from app.database.requests.user.update import update_user, update_user_is_over
from app.database.requests.admin.select import get_admins
from app.database.requests.notify.select import get_expired_notify

import app.keyboards.builder as bkb
from loguru import logger


async def fast_notify(bot: Bot):
    expired_notify = await get_expired_notify()
    admins = await get_admins()

    for find_notify in expired_notify:
        try:
            for admin in admins:
                await bot.send_message(
                    chat_id=admin.tg_id,
                    text=f"триальный период окончен {find_notify.username}"
                )
        except Exception as e:
            print(e)
            continue

        await delete_notify(find_notify.id)


async def start_reminders(bot: Bot):
    admins = await get_admins()
    users = await get_users_for_start(date.today())
    now = datetime.now()

    logger.info(f"Found {len(users)} users for reminder start")

    for user in users:
        try:
            logger.info(
                f"Start reminder flow for user: "
                f"id={user.id}, "
                f"username={user.username}"
            )

            if user.reminder_started_at is not None:
                logger.info(
                    f"User {user.id} already has active reminders"
                )

                continue

            await update_user_is_over(
                user_id=user.id,
                is_over=False
            )

            period_end = user.created_at + timedelta(days=7)

            text = (
                f"💰 @{user.username} сегодня оплата!\n\n"
                f"📅 Период: "
                f"{user.created_at:%d.%m.%Y} - "
                f"{period_end:%d.%m.%Y}"
            )

            keyboard = await bkb.done(user.id)

            for admin in admins:

                try:
                    logger.info(
                        f"Send start reminder "
                        f"to admin {admin.tg_id}"
                    )

                    await bot.send_message(
                        chat_id=admin.tg_id,
                        text=text,
                        reply_markup=keyboard
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to send message "
                        f"to admin {admin.tg_id}: {e}"
                    )

            await update_user(
                user_id=user.id,
                reminder_started_at=now,
                # created_at=period_end,
                reminder_count=0
            )

            logger.success(
                f"Reminder flow started successfully "
                f"for user {user.id}"
            )
        except Exception as e:
            logger.exception(
                f"Error while starting reminders "
                f"for user {user.id}: {e}"

            )