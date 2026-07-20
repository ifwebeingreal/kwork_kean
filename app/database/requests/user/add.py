from app.database.models import async_session
from app.database.models import User
from datetime import date


async def set_user(username: str,
                   created_at: date,
                   team_id: int):
    async with async_session() as session:
        session.add(User(username=username,
                         created_at=created_at,
                         team_id=team_id))
        await session.commit()