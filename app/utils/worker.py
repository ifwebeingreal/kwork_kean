from datetime import datetime, timedelta

from aiogram import Bot
from loguru import logger

import app.keyboards.builder as bkb

from app.database.requests.admin.select import get_admins
from app.database.requests.user.select import get_active_reminders
from app.database.requests.user.update import update_user


DELAYS = [
    timedelta(hours=1),
    timedelta(hours=3),
    timedelta(hours=6),
]

# DELAYS = [
#     timedelta(minutes=1),
#     timedelta(minutes=3),
#     timedelta(minutes=6),
# ]


async def process_reminders(bot: Bot):
    admins = await get_admins()
    users = await get_active_reminders()

    now = datetime.now()

    logger.info(f"Found {len(users)} active reminders")

    for user in users:
        try:
            logger.info(
                f"Processing user: "
                f"id={user.id}, "
                f"username={user.username}, "
                f"count={user.reminder_count}"
            )

            # завершили цикл напоминаний
            if user.reminder_count >= len(DELAYS):
                logger.info(f"User {user.id} reminder flow finished")

                await update_user(
                    user_id=user.id,
                    is_over=True
                )

                continue

            delay = DELAYS[user.reminder_count]

            next_time = user.reminder_started_at + delay

            logger.info(
                f"User {user.id}: "
                f"next_time={next_time}, "
                f"now={now}"
            )

            # ещё не время
            if now < next_time:
                logger.info(f"Skip user {user.id}")
                continue

            logger.info(f"Send reminder to user {user.id}")

            text = (
                f"⚠️ Напоминание #{user.reminder_count + 1}\n\n"
                f"💰 {user.username} сегодня оплата!\n"
                f"📅 Период: "
                f"{user.created_at:%d.%m.%Y} - "
                f"{(user.created_at + timedelta(days=7)):%d.%m.%Y}\n\n"
                f"⏳ Нужно оплатить"
            )

            keyboard = await bkb.done(user.id)

            for admin in admins:
                try:
                    logger.info(
                        f"Send message to admin {admin.tg_id}"
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

            # увеличиваем счётчик
            await update_user(
                user_id=user.id,
                reminder_count=user.reminder_count + 1
            )

            logger.success(
                f"Reminder sent successfully "
                f"for user {user.id}"
            )

        except Exception as e:
            logger.exception(
                f"Error while processing user {user.id}: {e}"
            )