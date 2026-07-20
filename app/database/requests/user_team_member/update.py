from app.database.models import async_session
from app.database.models import UserTeamMember
from sqlalchemy import update


async def update_user_tg_id(user_id: int, tg_id: int):
    async with async_session() as session:
        await session.execute(
            update(UserTeamMember)
            .where(UserTeamMember.id == user_id)
            .values(tg_id=tg_id)
        )
        await session.commit()


async def update_user_team_id(user_id: int, team_id: int):
    async with async_session() as session:
        await session.execute(
            update(UserTeamMember)
            .where(UserTeamMember.id == user_id)
            .values(team_id=team_id)
        )
        await session.commit()