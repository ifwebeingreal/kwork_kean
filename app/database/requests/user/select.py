from datetime import date, timedelta

from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select, func


async def get_user(id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == id))
        return user


async def get_users():
    async with async_session() as session:
        users = await session.scalars(
            select(User)
            .order_by(
                User.team_id.asc().nulls_last()
            )
        )

        return users.all()


async def get_users_count():
    async with async_session() as session:
        count = await session.scalar(select(func.count()).select_from(User))
        return count


async def get_users_for_start(today: date):
    async with async_session() as session:
        result = await session.scalars(
            select(User).where(
                User.created_at <= today - timedelta(days=7),
                User.reminder_started_at.is_(None),
            )
        )
        return result.all()


async def get_active_reminders():
    async with async_session() as session:
        result = await session.scalars(
            select(User).where(
                User.reminder_started_at.is_not(None),
                User.is_over.is_(False)
            )
        )
        return result.all()


async def get_users_by_team(team_id: int):
    async with async_session() as session:
        users = await session.scalars(
            select(User)
            .where(User.team_id == team_id)
        )
        return users.all()