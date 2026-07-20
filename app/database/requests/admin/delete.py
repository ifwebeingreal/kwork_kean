from app.database.models import async_session
from app.database.models import Admin
from sqlalchemy import delete


async def delete_admin(id):
    async with async_session() as session:
        await session.execute(delete(Admin).where(Admin.id == id))
        await session.commit()