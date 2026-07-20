from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database.requests.user_team_member.add import set_user_team_member
from app.database.requests.user_team_member.select import get_user_by_id
from app.database.requests.user_team_member.delete import delete_user_team_member

import app.keyboards.builder as bkb
import app.keyboards.inline as ikb

from app.states import AddTeamUser


user_team = Router()


@user_team.callback_query(F.data.startswith("check_pull_users_"))
async def check_pull_users_(callback: CallbackQuery):
    pull_id = int(callback.data.split("_")[3])

    await callback.message.edit_text(
        "<b>Добавленные пользователи в пулл:</b>",
        reply_markup=await bkb.pull_users(pull_id),
    )


@user_team.callback_query(F.data.startswith("add_pull_user_"))
async def add_pull_user(callback: CallbackQuery, state: FSMContext):
    pull_id = int(callback.data.split("_")[3])

    await callback.message.edit_text(
        "<b>Введите TG ID пользователя:</b>\n\n"
        "<i>Получить его можно тут: @username_to_id_bot</i>\n",
        reply_markup=ikb.admin_cancel
    )

    await state.set_state(AddTeamUser.tg_id)
    await state.update_data(pull_id=pull_id)


@user_team.message(AddTeamUser.tg_id)
async def check_tg_id(message: Message, state: FSMContext):
    if message.text and message.text.isdigit():
        await state.update_data(tg_id=int(message.text))

        data = await state.get_data()

        pull_id = data.get("pull_id")
        tg_id = data.get("tg_id")

        await set_user_team_member(tg_id, pull_id)

        await message.answer(
            "<b>Пользователь был успешно добавлен!</b>",
            reply_markup=await bkb.pull_users(pull_id),
        )

        await state.clear()

    else:
        await message.answer(
            "<b>TG ID должен быть числом!</b>",
            reply_markup=ikb.admin_cancel
        )


@user_team.callback_query(F.data.startswith("pulluser_"))
async def check_team_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    user = await get_user_by_id(user_id)

    await callback.message.edit_text(
        f"<b>Панель управления пользователем</b>\n\n"
        f"<b>TG ID:</b> <code>{user.tg_id}</code>",
        reply_markup=await bkb.team_user_panel(user.id, user.team_id),
    )


@user_team.callback_query(F.data.startswith("delete_pull_user_"))
async def remove_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])
    user = await get_user_by_id(user_id)
    pull_id = user.team_id
    await delete_user_team_member(user_id)
    await callback.message.edit_text(
        "<b>Пользователь был успешно удален!</b>",
        reply_markup=await bkb.pull_users(pull_id),
    )