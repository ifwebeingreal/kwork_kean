from app.database.models import async_session
from app.database.models import Admin


async def set_admin(tg_id):
    async with async_session() as session:
        session.add(Admin(tg_id=tg_id))
        await session.commit()