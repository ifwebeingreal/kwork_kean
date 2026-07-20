from datetime import timedelta

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

import app.keyboards.builder as bkb
import app.keyboards.inline as ikb

from app.database.requests.admin.select import get_admins, get_admin
from app.database.requests.admin.delete import delete_admin
from app.database.requests.admin.add import set_admin
from app.database.requests.user.select import get_user
from app.database.requests.user.update import update_user_is_over, update_user

from app.states import AddAdmin

admin = Router()


@admin.message(CommandStart())
@admin.message(Command("admin"))
@admin.message(F.text == "Админ-панель")
async def admin_panel(message: Message):
    admins = await get_admins()

    for admin in admins:
        if admin.tg_id == message.from_user.id:
            await message.answer(text=f"<b>Добро пожаловать!</b>\n"
                                      f"Вы успешно авторизовались как администратор!",
                                 reply_markup=await bkb.admin_panel(message.from_user.id))
            return


@admin.callback_query(F.data == "admins")
async def all_admins(callback: CallbackQuery):
    await callback.message.edit_text("<b>Текущие администраторы бота:</b>",
                                     reply_markup=await bkb.admins_cb())


@admin.callback_query(F.data == "add_admin")
async def add_admin(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("<b>Введите Telegram ID администратора:</b>",
                                     reply_markup=ikb.admin_cancel)

    await state.set_state(AddAdmin.tg_id)


@admin.message(AddAdmin.tg_id)
async def add_admin(message: Message, state: FSMContext):
    if message.text and message.text.isdigit():
        await set_admin(int(message.text))

        await message.answer("<b>Администратор успешно добавлен!</b>",
                             reply_markup=await bkb.admins_cb())

        await state.clear()

    else:
        await message.answer("<b>Введите корректный Telegram ID!</b>",
                             reply_markup=ikb.admin_cancel)


@admin.callback_query(F.data.startswith("admin_"))
async def admin_info_panel(callback: CallbackQuery):
    admin_id = int(callback.data.split("_")[1])
    admin_info = await get_admin(admin_id)

    await callback.message.edit_text(f"<b>Панель управления администратором №{admin_info.id}:</b>\n\n"
                                     f"<b>Telegram ID:</b> {admin_info.tg_id}\n\n"
                                     f"<b><i>Выберите действие:</i></b>",
                                     reply_markup=await bkb.edit_admin(admin_id))


@admin.callback_query(F.data.startswith("deleteadmin_"))
async def remove_admin(callback: CallbackQuery):
    admin_id = int(callback.data.split("_")[1])
    await delete_admin(admin_id)

    await callback.message.edit_text("<b>Администратор успешно удален!</b>",
                                     reply_markup=await bkb.admins_cb())


@admin.callback_query(F.data.startswith("done_"))
async def done_admin(callback: CallbackQuery):
    await callback.answer()

    user_id = int(callback.data.split("_")[1])
    user = await get_user(user_id)

    if not user.is_over:
        await update_user(
            user_id=user.id,
            created_at=user.created_at + timedelta(days=7),
            reminder_started_at=None,
            reminder_count=0,
            is_over=True
        )

        await callback.message.edit_reply_markup(
            reply_markup=await bkb.done(user.id, "success")
        )


@admin.callback_query(F.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    admins = await get_admins()

    for admin in admins:
        if admin.tg_id == callback.from_user.id:
            await callback.message.edit_text(text=f"<b>Добро пожаловать!</b>\n"
                                      f"Вы успешно авторизовались как администратор!",
                                 reply_markup=await bkb.admin_panel(callback.from_user.id))
            await state.clear()

            return
