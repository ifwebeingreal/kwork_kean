from typing import Annotated
from datetime import date, datetime

from sqlalchemy import ForeignKey, String, BigInteger, Date, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from config import config

engine = create_async_engine(url=config.database.sqlalchemy_url(),
                             echo=True)

async_session = async_sessionmaker(engine)

intpk = Annotated[int, mapped_column(primary_key=True)]


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(String)
    created_at: Mapped[date] = mapped_column(Date)
    reminder_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reminder_count: Mapped[int] = mapped_column(Integer, default=0)
    is_over: Mapped[bool] = mapped_column(Boolean, default=False)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )


class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[intpk]
    tg_id: Mapped[int] = mapped_column(BigInteger)


class Notify(Base):
    __tablename__ = 'notify'

    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(String)
    notify_date: Mapped[datetime] = mapped_column(DateTime)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String)


class UserTeamMember(Base):
    __tablename__ = "user_team_members"

    id: Mapped[intpk]
    tg_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
