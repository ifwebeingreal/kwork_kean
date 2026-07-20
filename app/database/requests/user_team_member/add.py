from app.database.models import async_session
from app.database.models import UserTeamMember


async def set_user_team_member(
        tg_id: int,
        team_id: int,
):
    async with async_session() as session:
        session.add(UserTeamMember(tg_id=tg_id,
                                   team_id=team_id))
        await session.commit()