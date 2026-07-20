from app.database.models import async_session
from app.database.models import UserTeamMember
from sqlalchemy import select


async def get_users_team_members():
    async with async_session() as session:
        users = await session.scalars(
            select(UserTeamMember)
        )
        return users.all()


async def get_users_by_team(team_id: int):
    async with async_session() as session:
        users = await session.scalars(
            select(UserTeamMember)
            .where(UserTeamMember.team_id == team_id)
        )
        return users


async def get_user_by_id(user_id: int):
    async with async_session() as session:
        user = await session.scalar(
            select(UserTeamMember)
            .where(UserTeamMember.id == user_id)
        )
        return user


async def get_user_by_tg_id(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(
            select(UserTeamMember)
            .where(UserTeamMember.tg_id == tg_id)
        )
        return user
