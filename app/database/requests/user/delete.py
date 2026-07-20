from app.database.models import async_session
from app.database.models import User
from sqlalchemy import delete


async def delete_user(id: int):
    async with async_session() as session:
        await session.execute(delete(User).where(User.id == id))
        await session.commit()