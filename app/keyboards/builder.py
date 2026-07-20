from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests.admin.select import get_admins, get_admin_by_tg_id
from app.database.requests.user.select import get_users
from app.database.requests.notify.select import get_all_notify
from app.database.requests.team.select import get_teams
from app.database.requests.user_team_member.select import get_users_by_team


async def admin_panel(tg_id: int):
    kb = InlineKeyboardBuilder()

    admin = await get_admin_by_tg_id(tg_id)

    kb.row(InlineKeyboardButton(text="Пользователи", callback_data="users"))
    kb.row(InlineKeyboardButton(text="Напоминания", callback_data="all_notify"))

    if admin:
        kb.row(InlineKeyboardButton(text="Администраторы", callback_data="admins"))
        kb.row(InlineKeyboardButton(text="Группы", callback_data="pulls"))

    return kb.as_markup()



async def admins_cb():
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="➕ Добавить администратора", callback_data="add_admin"))

    admins = await get_admins()
    for admin in admins:
        kb.row(InlineKeyboardButton(text=f"{admin.tg_id}", callback_data=f"admin_{admin.id}"))

    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))

    return kb.as_markup()


async def edit_admin(id: int):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="❌ Удалить", callback_data=f"deleteadmin_{id}"))
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data=f"admins"))

    return kb.as_markup()


async def users_cb(users):
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(
            text="➕ Добавить пользователя",
            callback_data="add_user"
        )
    )

    for user in users:
        kb.row(
            InlineKeyboardButton(
                text=f"{user.username}",
                callback_data=f"user_{user.id}"
            )
        )

    kb.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back"
        )
    )

    return kb.as_markup()

async def edit_user(id: int, is_admin: bool = False):
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(
            text="✏️ Изменить ник",
            callback_data=f"edit_username_{id}"
        )
    )

    kb.row(
        InlineKeyboardButton(
            text="✏️ Изменить дату",
            callback_data=f"edit_start_date_{id}"
        )
    )

    if is_admin:
        kb.row(
            InlineKeyboardButton(
                text="✏️ Изменить пулл",
                callback_data=f"edit_user_team_{id}"
            )
        )

    kb.row(
        InlineKeyboardButton(
            text="❌ Удалить",
            callback_data=f"delete_user_{id}"
        )
    )

    kb.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="users"
        )
    )

    return kb.as_markup()


async def done(id: int, style: str = "danger"):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="Готово", callback_data=f"done_{id}", style=style))

    return kb.as_markup()


async def notify_cb(notifies):
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(
            text="➕ Добавить напоминание",
            callback_data="add_notify"
        )
    )

    for notify in notifies:
        kb.row(
            InlineKeyboardButton(
                text=notify.username,
                callback_data=f"notify_{notify.id}"
            )
        )

    kb.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back"
        )
    )

    return kb.as_markup()


async def edit_notify(id: int, is_admin: bool = False):
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(
            text="✏️ Изменить ник",
            callback_data=f"edit_notify_username_{id}"
        )
    )

    kb.row(
        InlineKeyboardButton(
            text="✏️ Изменить дату",
            callback_data=f"edit_notify_date_{id}"
        )
    )

    if is_admin:
        kb.row(
            InlineKeyboardButton(
                text="✏️ Изменить пул",
                callback_data=f"edit_notify_pull_{id}"
            )
        )

    kb.row(
        InlineKeyboardButton(
            text="❌ Удалить",
            callback_data=f"delete_notify_{id}"
        )
    )

    kb.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="all_notify"
        )
    )

    return kb.as_markup()


async def pulls_cb():
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="➕ Добавить пул", callback_data="add_pull"))

    pulls = await get_teams()
    for pull in pulls:
        kb.row(InlineKeyboardButton(text=f"{pull.name}", callback_data=f"pull_{pull.id}"))

    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))

    return kb.as_markup()


async def pull_setter(pull_id: int):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="👤 Пользователи", callback_data=f"check_pull_users_{pull_id}"))
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))

    return kb.as_markup()


async def edit_pull(pull_id: int):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="👤 Пользователи", callback_data=f"check_pull_users_{pull_id}"))
    kb.row(InlineKeyboardButton(text="🧑‍💻 Клиенты", callback_data=f"get_pull_users_{pull_id}"))
    kb.row(InlineKeyboardButton(text="✉️ Уведомления", callback_data=f"get_pull_notify_{pull_id}"))
    kb.row(InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"edit_pull_{pull_id}"))
    kb.row(InlineKeyboardButton(text="❌ Удалить пулл", callback_data=f"delete_pull_{pull_id}"))
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))

    return kb.as_markup()


async def pull_users(pull_id: int):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="➕ Добавить пользователя", callback_data=f"add_pull_user_{pull_id}"))

    users = await get_users_by_team(pull_id)
    for user in users:
        kb.row(InlineKeyboardButton(text=f"{user.tg_id}", callback_data=f"pulluser_{user.id}"))

    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data=f"pull_{pull_id}"))

    return kb.as_markup()


async def team_user_panel(user_id: int, pull_id: int):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="❌ Удалить", callback_data=f"deletepulluser_{user_id}"))
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data=f"check_pull_users_{pull_id}"))

    return kb.as_markup()


async def users_pulls_cb():
    kb = InlineKeyboardBuilder()

    pulls = await get_teams()
    for pull in pulls:
        kb.row(InlineKeyboardButton(text=f"{pull.name}", callback_data=f"userspull_{pull.id}"))

    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))

    return kb.as_markup()


async def edit_users_pulls_cb():
    kb = InlineKeyboardBuilder()

    pulls = await get_teams()
    for pull in pulls:
        kb.row(InlineKeyboardButton(text=f"{pull.name}", callback_data=f"edituserspull_{pull.id}"))

    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))

    return kb.as_markup()


async def notify_pulls_cb():
    kb = InlineKeyboardBuilder()

    pulls = await get_teams()
    for pull in pulls:
        kb.row(InlineKeyboardButton(text=f"{pull.name}", callback_data=f"notifypull_{pull.id}"))

    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))

    return kb.as_markup()


async def edit_notify_pulls_cb():
    kb = InlineKeyboardBuilder()

    pulls = await get_teams()
    for pull in pulls:
        kb.row(InlineKeyboardButton(text=f"{pull.name}", callback_data=f"editnotifypull_{pull.id}"))

    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))

    return kb.as_markup()
