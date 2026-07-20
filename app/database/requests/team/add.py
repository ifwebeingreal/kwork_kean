from app.database.models import async_session
from app.database.models import Team


async def set_team(name: str):
    async with async_session() as session:
        team = Team(name=name)
        session.add(team)
        await session.commit()
        await session.refresh(team)
        return team