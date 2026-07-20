from app.database.models import async_session
from app.database.models import Team
from sqlalchemy import select


async def get_teams():
    async with async_session() as session:
        teams = await session.scalars(select(Team))
        return teams


async def get_team(team_id: int):
    async with async_session() as session:
        team = await session.scalar(select(Team).where(Team.id == team_id))
        return team