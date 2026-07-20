from app.database.models import async_session
from app.database.models import Notify
from sqlalchemy import delete


async def delete_notify(id: int):
    async with async_session() as session:
        await session.execute(delete(Notify).where(Notify.id == id))
        await session.commit()