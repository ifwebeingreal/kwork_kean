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
        print("=" * 50)
        print(f"Событие: {type(event).__name__}")

        user = getattr(event, "from_user", None)
        if not user:
            print("❌ У события нет from_user")
            return await handler(event, data)

        print(f"👤 Пользователь: {user.full_name}")
        print(f"🆔 TG ID: {user.id}")
        print(f"📛 Username: @{user.username}")

        admins = await get_admins()
        users = await get_users_team_members()

        admin_ids = {a.tg_id for a in admins}
        user_ids = {u.tg_id for u in users}

        print(f"\n👮 Админов найдено: {len(admin_ids)}")
        print(admin_ids)

        print(f"\n👥 Пользователей команды найдено: {len(user_ids)}")
        print(user_ids)

        tg_id = user.id

        if tg_id in admin_ids:
            print("✅ Пользователь является администратором")
            return await handler(event, data)

        if tg_id in user_ids:
            print("✅ Пользователь найден в UserTeamMember")
            return await handler(event, data)

        print("⛔ Доступ запрещен")

        if hasattr(event, "answer"):
            await event.answer("У вас недостаточно прав!")

        return None