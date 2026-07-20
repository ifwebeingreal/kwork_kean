from datetime import datetime

from app.database.models import async_session
from app.database.models import Notify


async def set_notify(
        username: str,
        notify_date: datetime,
):
    async with async_session() as session:
        session.add(Notify(username=username, notify_date=notify_date))
        await session.commit()