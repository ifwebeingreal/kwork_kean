from app.database.models import async_session
from app.database.models import UserTeamMember
from sqlalchemy import delete


async def delete_user_team_member(user_id: int):
    async with async_session() as session:
        await session.execute(
            delete(UserTeamMember)
            .where(UserTeamMember.tg_id == user_id)
        )
        await session.commit()