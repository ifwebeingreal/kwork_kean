from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database.requests.admin.select import get_admins
from app.database.requests.user_team_member.select import get_users_team_members


class AdminProtect(BaseMiddleware):
    async def __call__(
            self,
            handler,
            event: TelegramObject,
            data: dict
    ):
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        admins = await get_admins()
        users = await get_users_team_members()
        tg_id = event.from_user.id

        if tg_id in {a.tg_id for a in admins}:
            return await handler(event, data)

        if tg_id in {u.tg_id for u in users}:
            return await handler(event, data)

        if hasattr(event, "answer"):
            await event.answer("У вас недостаточно прав!")
            return None
        return None
