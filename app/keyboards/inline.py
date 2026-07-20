from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import config

# admin_panel = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text="Пользователи", callback_data="users")],
#         [InlineKeyboardButton(text="Напоминания", callback_data="all_notify")],
#         [InlineKeyboardButton(text="Администраторы", callback_data="admins")],
#     ]
# )

admin_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ]
)

date_panel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Текущая дата", callback_data="today")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ]
)

check_sub = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться", url=config.bot.channel_link)],
        [InlineKeyboardButton(text="Проверить подписку", callback_data="check_sub")]
    ]
)


done_panel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Готово", callback_data="done_ok", style="success")],
    ]
)