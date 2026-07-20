from app.database.models import async_session
from app.database.models import Admin
from sqlalchemy import select


async def get_admins():
    async with async_session() as session:
        admins = await session.scalars(select(Admin))
        return admins.all()


async def get_admin(id):
    async with async_session() as session:
        admin = await session.scalar(select(Admin).where(Admin.id == id))
        return admin


async def get_admin_by_tg_id(tg_id: int):
    async with async_session() as session:
        admin = await session.scalar(select(Admin).where(Admin.tg_id == tg_id))
        return admin