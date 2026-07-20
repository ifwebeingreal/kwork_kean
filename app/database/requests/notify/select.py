from datetime import datetime

import pytz

from app.database.models import async_session
from app.database.models import Notify
from sqlalchemy import select


async def get_all_notify():
    async with async_session() as session:
        notify = await session.scalars(select(Notify))
        return notify


async def get_notify(id: int):
    async with async_session() as session:
        notify = await session.scalar(
            select(Notify).where(Notify.id == id)
        )
        return notify


async def get_notify_by_team_id(team_id: int):
    async with async_session() as session:
        notify = await session.scalars(
            select(Notify).where(Notify.team_id == team_id)
        )
        return notify


async def get_expired_notify():
    # 1. Получаем время строго по Москве
    tz = pytz.timezone('Europe/Moscow')
    # 2. .replace(tzinfo=None) делает время "наивным",
    # чтобы база сравнивала просто цифры без учета часовых поясов
    now_msk = datetime.now(tz).replace(tzinfo=None)

    async with async_session() as session:
        result = await session.scalars(
            select(Notify).where(Notify.notify_date <= now_msk)
        )
        return result.all()