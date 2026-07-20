from datetime import date, datetime

from app.database.models import async_session
from app.database.models import User
from sqlalchemy import update


async def update_user(user_id: int, **kwargs):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
        )
        await session.commit()


async def update_user_is_over(
        user_id: int,
        is_over: bool,
):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_over=is_over)
        )
        await session.commit()