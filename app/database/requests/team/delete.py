from app.database.models import async_session
from app.database.models import Team
from sqlalchemy import delete


async def delete_team(team_id: int):
    async with async_session() as session:
        await session.execute(
            delete(Team).where(Team.id == team_id)
        )
        await session.commit()