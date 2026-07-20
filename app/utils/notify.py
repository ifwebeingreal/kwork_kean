from datetime import datetime, date, timedelta
from aiogram import Bot

from app.database.requests.notify.delete import delete_notify
from app.database.requests.team.select import get_team
from app.database.requests.user.select import get_users_for_start
from app.database.requests.user.update import update_user, update_user_is_over
from app.database.requests.admin.select import get_admins
from app.database.requests.notify.select import get_expired_notify

import app.keyboards.builder as bkb
from loguru import logger

from app.database.requests.user_team_member.select import get_users_team_members


async def fast_notify(bot: Bot):
    expired_notify = await get_expired_notify()
    admins = await get_admins()
    team_members = await get_users_team_members()

    admin_ids = {admin.tg_id for admin in admins}

    for find_notify in expired_notify:
        sent_ids = set()

        try:
            team = await get_team(find_notify.team_id)

            pool_name = team.name if team else "Без пула"

            # Сообщение для админов
            admin_text = (
                f"⏰ Триальный период окончен\n\n"
                f"👤 Пользователь: @{find_notify.username}\n"
                f"📌 Пулл: {pool_name}"
            )

            # Сообщение для участников
            member_text = (
                f"⏰ Триальный период окончен\n\n"
                f"👤 Пользователь: @{find_notify.username}"
            )


            # ----------------------
            # Отправляем администраторам
            # ----------------------
            for admin in admins:
                try:
                    await bot.send_message(
                        chat_id=admin.tg_id,
                        text=admin_text
                    )

                    sent_ids.add(admin.tg_id)

                except Exception as e:
                    logger.error(
                        f"Failed send expired notify "
                        f"to admin {admin.tg_id}: {e}"
                    )


            # ----------------------
            # Отправляем участникам своего пула
            # ----------------------
            for member in team_members:

                if member.team_id != find_notify.team_id:
                    continue

                # чтобы не было дублей
                if member.tg_id in sent_ids:
                    continue

                try:
                    await bot.send_message(
                        chat_id=member.tg_id,
                        text=member_text
                    )

                    sent_ids.add(member.tg_id)

                except Exception as e:
                    logger.error(
                        f"Failed send expired notify "
                        f"to member {member.tg_id}: {e}"
                    )


        except Exception as e:
            logger.error(
                f"Error processing notify {find_notify.id}: {e}"
            )
            continue


        await delete_notify(find_notify.id)


async def start_reminders(bot: Bot):
    admins = await get_admins()
    team_members = await get_users_team_members()
    users = await get_users_for_start(date.today())

    now = datetime.now()

    logger.info(f"Found {len(users)} users for reminder start")

    # Чтобы не было дублей
    admin_ids = {admin.tg_id for admin in admins}

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

            # Общее сообщение для обычных участников
            member_text = (
                f"💰 @{user.username} сегодня оплата!\n\n"
                f"📅 Период: "
                f"{user.created_at:%d.%m.%Y} - "
                f"{period_end:%d.%m.%Y}"
            )

            # Сообщение для админов
            team = await get_team(user.team_id)

            pool_name = team.name if team else "Без пула"

            admin_text = (
                f"💰 @{user.username} сегодня оплата!\n\n"
                f"📅 Период: "
                f"{user.created_at:%d.%m.%Y} - "
                f"{period_end:%d.%m.%Y}\n\n"
                f"📌 Пулл: {pool_name}"
            )

            keyboard = await bkb.done(user.id)

            sent_ids = set()

            # -------------------------
            # Отправка администраторам
            # -------------------------
            for admin in admins:
                try:
                    await bot.send_message(
                        chat_id=admin.tg_id,
                        text=admin_text,
                        reply_markup=keyboard
                    )

                    sent_ids.add(admin.tg_id)

                except Exception as e:
                    logger.error(
                        f"Failed send reminder to admin "
                        f"{admin.tg_id}: {e}"
                    )


            # ---------------------------------
            # Отправка участникам своего пула
            # ---------------------------------
            for member in team_members:

                # Только свой пул
                if member.team_id != user.team_id:
                    continue

                # Если уже получил как админ
                if member.tg_id in sent_ids:
                    continue

                try:
                    await bot.send_message(
                        chat_id=member.tg_id,
                        text=member_text,
                        reply_markup=keyboard
                    )

                    sent_ids.add(member.tg_id)

                except Exception as e:
                    logger.error(
                        f"Failed send reminder to member "
                        f"{member.tg_id}: {e}"
                    )


            await update_user(
                user_id=user.id,
                reminder_started_at=now,
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