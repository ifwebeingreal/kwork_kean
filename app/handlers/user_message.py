from datetime import date, timedelta

from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards.reply as rkb
import app.keyboards.inline as ikb
import app.keyboards.builder as bkb
from app.database.requests.team.select import get_team

from app.database.requests.user.add import set_user
from app.database.requests.user.select import get_user, get_users, get_users_by_team
from app.database.requests.user.delete import delete_user
from app.database.requests.user.update import update_user
from app.database.requests.admin.select import get_admin_by_tg_id
from app.database.requests.user_team_member.select import get_user_by_tg_id

from app.states import AddUser, EditUser

user = Router()


@user.callback_query(F.data == "users")
async def all_users(callback: CallbackQuery):
    tg_id = callback.from_user.id

    admin = await get_admin_by_tg_id(tg_id)
    team_member = await get_user_by_tg_id(tg_id)

    if admin:
        users = await get_users()

    elif team_member:
        users = await get_users_by_team(team_member.team_id)

    else:
        await callback.answer(
            "У вас нет доступа!",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "<b>Добавленные пользователи:</b>",
        reply_markup=await bkb.users_cb(users)
    )


@user.callback_query(F.data == "add_user")
async def add_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Введите username пользователя:</b>",
        reply_markup=ikb.admin_cancel
    )

    await state.set_state(AddUser.username)


@user.message(AddUser.username)
async def check_username(message: Message, state: FSMContext):
    if message.text and len(message.text) <= 200:
        await state.update_data(username=message.text)

        await message.answer(
            f"<b>Укажите дату начала работ в формате ГГГГ-ММ-ДД:</b>\n\n"
            f"Пример: <code>{date.today()}</code>",
            reply_markup=ikb.date_panel
        )

        await state.set_state(AddUser.created_at)

    else:
        await message.answer(
            "<b>Username должен быть текстом до 200 символов!</b>",
            reply_markup=ikb.admin_cancel
        )


@user.callback_query(F.data == "today", AddUser.created_at)
async def today_create_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    username = data.get("username")
    tg_id = callback.from_user.id
    today = date.today()
    today_str = today.isoformat()
    await state.update_data(created_at=today_str)

    team_member = await get_user_by_tg_id(tg_id)
    admin = await get_admin_by_tg_id(tg_id)

    if admin:
        await callback.message.edit_text(
            "<b>Выберите пул для рассылки:</b>",
            reply_markup=await bkb.users_pulls_cb()
        )

        await state.set_state(AddUser.select_team)

    elif team_member:
        await set_user(username, today, team_id=team_member.team_id)

        tg_id = callback.from_user.id

        admin = await get_admin_by_tg_id(tg_id)
        team_member = await get_user_by_tg_id(tg_id)

        if admin:
            users = await get_users()

        elif team_member:
            users = await get_users_by_team(team_member.team_id)

        else:
            await callback.answer(
                "У вас нет доступа!",
                show_alert=True
            )
            return

        await callback.message.edit_text(
            "<b>Пользователь был успешно добавлен!</b>",
            reply_markup=await bkb.users_cb(users)
        )

        await state.clear()


@user.message(AddUser.created_at)
async def check_created_at(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            f"<b>Укажите дату начала работ в формате ГГГГ-ММ-ДД:</b>\n\n"
            f"Пример: <code>{date.today()}</code>",
            reply_markup=ikb.date_panel
        )
        return

    try:
        created_at = date.fromisoformat(message.text)

        # В FSM сохраняем строку, так как Redis хранит JSON
        await state.update_data(
            created_at=created_at.isoformat()
        )

        data = await state.get_data()

        username = data.get("username")
        tg_id = message.from_user.id

        team_member = await get_user_by_tg_id(tg_id)
        admin = await get_admin_by_tg_id(tg_id)

        if admin:
            await message.answer(
                "<b>Выберите пул для рассылки:</b>",
                reply_markup=await bkb.users_pulls_cb()
            )

            await state.set_state(AddUser.select_team)

        elif team_member:
            await set_user(
                username,
                created_at,
                team_id=team_member.team_id
            )

            tg_id = message.from_user.id

            admin = await get_admin_by_tg_id(tg_id)
            team_member = await get_user_by_tg_id(tg_id)

            if admin:
                users = await get_users()

            elif team_member:
                users = await get_users_by_team(team_member.team_id)

            else:
                await message.answer(
                    "У вас нет доступа!",
                    show_alert=True
                )
                return

            await message.answer(
                "<b>Пользователь был успешно добавлен!</b>",
                reply_markup=await bkb.users_cb(users)
            )

            await state.clear()

        else:
            await message.answer(
                "<b>У вас нет прав для добавления пользователя.</b>"
            )
            await state.clear()

    except ValueError:
        await message.answer(
            f"<b>Укажите дату начала работ в формате ГГГГ-ММ-ДД:</b>\n\n"
            f"Пример: <code>{date.today()}</code>",
            reply_markup=ikb.date_panel
        )


@user.callback_query(F.data.startswith("userspull_"))
async def select_team(callback: CallbackQuery, state: FSMContext):
    team_id = int(callback.data.split("_")[1])

    data = await state.get_data()

    username = data.get("username")
    created_at = date.fromisoformat(data.get("created_at"))

    await set_user(
        username,
        created_at,
        team_id=team_id
    )

    tg_id = callback.from_user.id

    admin = await get_admin_by_tg_id(tg_id)
    team_member = await get_user_by_tg_id(tg_id)

    if admin:
        users = await get_users()

    elif team_member:
        users = await get_users_by_team(team_member.team_id)

    else:
        await callback.answer(
            "У вас нет доступа!",
            show_alert=True
        )
        return


    await callback.message.edit_text(
        "<b>Пользователь был успешно добавлен!</b>",
        reply_markup=await bkb.users_cb(users)
    )

    await state.clear()


@user.callback_query(F.data.startswith("user_"))
async def check_user_info(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    user_info = await get_user(user_id)
    team = await get_team(user_info.team_id)

    admin = await get_admin_by_tg_id(callback.from_user.id)

    text = (
        f"<b>Панель управления пользователем №{user_info.id}</b>\n\n"
        f"<b>Username:</b> {user_info.username}\n"
        f"<b>Дата начала:</b> {user_info.created_at}\n"
        f"<b>Дата напоминания:</b> {user_info.created_at + timedelta(days=7)}\n"
    )

    if admin:
        text += f"<b>Пулл:</b> {team.name if team else '-'}\n"

    text += "\n<i>Выберите действие:</i>"

    await callback.message.edit_text(
        text,
        reply_markup=await bkb.edit_user(user_info.id,
                                         is_admin=bool(admin))
    )


@user.callback_query(F.data.startswith("edit_username_"))
async def edit_username(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[2])

    await callback.message.edit_text(
        "<b>Введите новый username:</b>",
        reply_markup=ikb.admin_cancel
    )

    await state.set_state(EditUser.new_username)
    await state.update_data(user_id=user_id)


@user.message(EditUser.new_username)
async def check_new_username(message: Message, state: FSMContext):
    if message.text and len(message.text) <= 200:
        await state.update_data(username=message.text)

        data = await state.get_data()

        user_id = data.get("user_id")
        username = data.get("username")

        await update_user(user_id, username=username)
        user_info = await get_user(user_id)
        team = await get_team(user_info.team_id)

        admin = await get_admin_by_tg_id(message.from_user.id)

        text = (
            f"<b>Панель управления пользователем №{user_info.id}</b>\n\n"
            f"<b>Username:</b> {user_info.username}\n"
            f"<b>Дата начала:</b> {user_info.created_at}\n"
            f"<b>Дата напоминания:</b> {user_info.created_at + timedelta(days=7)}\n"
        )

        if admin:
            text += f"<b>Пулл:</b> {team.name if team else '-'}\n"

        text += "\n<i>Выберите действие:</i>"

        await message.answer(
            text,
            reply_markup=await bkb.edit_user(user_info.id,
                                             is_admin=bool(admin))
        )

        await state.clear()

    else:
        await message.answer(
            "<b>Username должен быть текстом до 200 символов!</b>",
            reply_markup=ikb.admin_cancel
        )


@user.callback_query(F.data.startswith("edit_start_date_"))
async def edit_start_date(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[3])

    await callback.message.edit_text(
        f"<b>Укажите новую дату начала работ в формате ГГГГ-ММ-ДД:</b>\n\n"
        f"Пример: <code>{date.today()}</code>",
        reply_markup=ikb.date_panel
    )

    await state.set_state(EditUser.new_created_at)
    await state.update_data(user_id=user_id)


@user.message(EditUser.new_created_at)
async def check_new_created_at(message: Message, state: FSMContext):
    if message.text:
        try:
            created_at = date.fromisoformat(message.text)
            data = await state.get_data()

            user_id = data.get("user_id")

            await update_user(user_id, created_at=created_at)
            user_info = await get_user(user_id)
            team = await get_team(user_info.team_id)

            admin = await get_admin_by_tg_id(message.from_user.id)

            text = (
                f"<b>Панель управления пользователем №{user_info.id}</b>\n\n"
                f"<b>Username:</b> {user_info.username}\n"
                f"<b>Дата начала:</b> {user_info.created_at}\n"
                f"<b>Дата напоминания:</b> {user_info.created_at + timedelta(days=7)}\n"
            )

            if admin:
                text += f"<b>Пулл:</b> {team.name if team else '-'}\n"

            text += "\n<i>Выберите действие:</i>"

            await message.answer(
                text,
                reply_markup=await bkb.edit_user(user_info.id,
                                                 is_admin=bool(admin))
            )

            await state.clear()
        except ValueError:
            await message.answer(
                f"<b>Укажите дату начала работ в формате ГГГГ-ММ-ДД:</b>\n\n"
                f"Пример: <code>{date.today()}</code>",
                reply_markup=ikb.admin_cancel
            )

    else:
        await message.answer(
            f"<b>Укажите дату начала работ в формате ГГГГ-ММ-ДД:</b>\n\n"
            f"Пример: <code>{date.today()}</code>",
            reply_markup=ikb.admin_cancel
        )


@user.callback_query(F.data.startswith("edit_user_team_"))
async def edit_user_team(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[3])

    await callback.message.edit_text(
        "<b>Выберите новый пулл для пользователя:</b>",
        reply_markup=await bkb.edit_users_pulls_cb()
    )

    await state.set_state(EditUser.new_select_team)
    await state.update_data(user_id=user_id)


@user.callback_query(F.data.startswith("edituserspull_"), EditUser.new_select_team)
async def check_select_team(callback: CallbackQuery, state: FSMContext):
    team_id = int(callback.data.split("_")[1])

    data = await state.get_data()

    user_id = data.get("user_id")

    await update_user(user_id, team_id=team_id)
    user_info = await get_user(user_id)
    team = await get_team(user_info.team_id)

    admin = await get_admin_by_tg_id(callback.from_user.id)

    text = (
        f"<b>Панель управления пользователем №{user_info.id}</b>\n\n"
        f"<b>Username:</b> {user_info.username}\n"
        f"<b>Дата начала:</b> {user_info.created_at}\n"
        f"<b>Дата напоминания:</b> {user_info.created_at + timedelta(days=7)}\n"
    )

    if admin:
        text += f"<b>Пулл:</b> {team.name if team else '-'}\n"

    text += "\n<i>Выберите действие:</i>"

    await callback.message.edit_text(
        text,
        reply_markup=await bkb.edit_user(user_info.id,
                                         is_admin=bool(admin))
    )

    await state.clear()


@user.callback_query(F.data.startswith("delete_user_"))
async def remove_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    await delete_user(user_id)

    tg_id = callback.from_user.id

    admin = await get_admin_by_tg_id(tg_id)
    team_member = await get_user_by_tg_id(tg_id)

    if admin:
        users = await get_users()

    elif team_member:
        users = await get_users_by_team(team_member.team_id)

    else:
        await callback.answer(
            "У вас нет доступа!",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "<b>Пользователь был успешно удален!</b>",
        reply_markup=await bkb.users_cb(users)
    )