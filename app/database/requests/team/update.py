from app.database.models import async_session
from app.database.models import Team
from sqlalchemy import update


async def update_team_name(team_id: int, name: str):
    async with async_session() as session:
        await session.execute(
            update(Team).where(Team.id == team_id).values(name=name)
        )
        await session.commit()