from datetime import datetime, timedelta

from aiogram import Bot
from loguru import logger

import app.keyboards.builder as bkb

from app.database.requests.admin.select import get_admins
from app.database.requests.team.select import get_team
from app.database.requests.user.select import get_active_reminders
from app.database.requests.user.update import update_user
from app.database.requests.user_team_member.select import get_users_team_members

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
    team_members = await get_users_team_members()
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

            if user.reminder_count >= len(DELAYS):
                logger.info(
                    f"User {user.id} reminder flow finished"
                )

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


            if now < next_time:
                logger.info(
                    f"Skip user {user.id}"
                )
                continue


            team = await get_team(user.team_id)

            pool_name = team.name if team else "Без пула"


            period_end = (
                user.created_at + timedelta(days=7)
            )


            # Для админов
            admin_text = (
                f"⚠️ Напоминание #{user.reminder_count + 1}\n\n"
                f"💰 {user.username} сегодня оплата!\n"
                f"📅 Период: "
                f"{user.created_at:%d.%m.%Y} - "
                f"{period_end:%d.%m.%Y}\n\n"
                f"📌 Пулл: {pool_name}\n\n"
                f"⏳ Нужно оплатить"
            )


            # Для обычных участников
            member_text = (
                f"⚠️ Напоминание #{user.reminder_count + 1}\n\n"
                f"💰 {user.username} сегодня оплата!\n"
                f"📅 Период: "
                f"{user.created_at:%d.%m.%Y} - "
                f"{period_end:%d.%m.%Y}\n\n"
                f"⏳ Нужно оплатить"
            )


            keyboard = await bkb.done(user.id)

            sent_ids = set()


            # ----------------------
            # Админы получают всё
            # ----------------------
            for admin in admins:
                try:
                    logger.info(
                        f"Send reminder to admin {admin.tg_id}"
                    )

                    await bot.send_message(
                        chat_id=admin.tg_id,
                        text=admin_text,
                        reply_markup=keyboard
                    )

                    sent_ids.add(admin.tg_id)

                except Exception as e:
                    logger.error(
                        f"Failed send to admin "
                        f"{admin.tg_id}: {e}"
                    )


            # ----------------------
            # Участники своего пула
            # ----------------------
            for member in team_members:

                if member.team_id != user.team_id:
                    continue

                if member.tg_id in sent_ids:
                    continue

                try:
                    logger.info(
                        f"Send reminder to member {member.tg_id}"
                    )

                    await bot.send_message(
                        chat_id=member.tg_id,
                        text=member_text,
                        reply_markup=keyboard
                    )

                    sent_ids.add(member.tg_id)

                except Exception as e:
                    logger.error(
                        f"Failed send to member "
                        f"{member.tg_id}: {e}"
                    )


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