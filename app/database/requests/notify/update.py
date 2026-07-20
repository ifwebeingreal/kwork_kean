from datetime import datetime

from app.database.models import async_session
from app.database.models import Notify
from sqlalchemy import update


async def update_notify_username(user_id: int, username: str):
    async with async_session() as session:
        await session.execute(
            update(Notify).where(Notify.id == user_id).values(username=username)
        )
        await session.commit()


async def update_notify_date(user_id: int, notify_date: datetime):
    async with async_session() as session:
        await session.execute(
            update(Notify).where(Notify.id == user_id).values(notify_date=notify_date)
        )
        await session.commit()


async def update_notify_team_id(user_id: int, team_id: int):
    async with async_session() as session:
        await session.execute(
            update(Notify).where(Notify.id == user_id).values(team_id=team_id)
        )
        await session.commit()