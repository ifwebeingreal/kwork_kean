from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database.requests.team.add import set_team
from app.database.requests.team.select import get_team
from app.database.requests.team.update import update_team_name
from app.database.requests.team.delete import delete_team

import app.keyboards.builder as bkb
import app.keyboards.inline as ikb

from app.states import AddTeam, EditTeam


team = Router()


@team.callback_query(F.data == "pulls")
async def all_pulls(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Добавленные группы пользователей:</b>",
        reply_markup=await bkb.pulls_cb()
    )


@team.callback_query(F.data == "add_pull")
async def add_pull(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Введите название для пула:</b>",
        reply_markup=ikb.admin_cancel
    )

    await state.set_state(AddTeam.name)


@team.message(AddTeam.name)
async def check_team_name(message: Message, state: FSMContext):
    if message.text and len(message.text) <= 100:
        new_pull = await set_team(message.text)

        await message.answer(
            "<b>Команда была успешно добавлена!</b>",
            reply_markup=await bkb.pull_setter(new_pull.id)
        )

        await state.clear()

    else:
        await message.answer(
            "<b>Название пула должно быть до 100 символов!</b>",
            reply_markup=ikb.admin_cancel
        )


@team.callback_query(F.data.startswith("pull_"))
async def pull_info(callback: CallbackQuery):
    pull_id = int(callback.data.split("_")[1])
    pull = await get_team(pull_id)

    await callback.message.edit_text(
        f"<b>Панель управления пуллом</b>\n\n"
        f"<b>Название:</b> {pull.name}\n\n"
        f"<i>Выберите действие:</i>",
        reply_markup=await bkb.edit_pull(pull_id)
    )


@team.callback_query(F.data.startswith("edit_pull_"))
async def edit_pull_name(callback: CallbackQuery, state: FSMContext):
    pull_id = int(callback.data.split("_")[2])

    await callback.message.edit_text(
        "<b>Введите новое название для пула:</b>",
        reply_markup=ikb.admin_cancel
    )

    await state.set_state(EditTeam.new_name)
    await state.update_data(pull_id=pull_id)


@team.message(EditTeam.new_name)
async def check_new_name(message: Message, state: FSMContext):
    if message.text and len(message.text) <= 100:
        await state.update_data(name=message.text)

        data = await state.get_data()

        pull_id = data.get("pull_id")
        name = data.get("name")

        await update_team_name(pull_id, name)
        pull = await get_team(pull_id)

        await message.answer(
            f"<b>Панель управления пуллом</b>\n\n"
            f"<b>Название:</b> {pull.name}\n\n"
            f"<i>Выберите действие:</i>",
            reply_markup=await bkb.edit_pull(pull_id)
        )

        await state.clear()

    else:
        await message.answer(
            "<b>Название пула должно быть до 100 символов!</b>",
            reply_markup=ikb.admin_cancel
        )


@team.callback_query(F.data.startswith("delete_pull_"))
async def remove_pull(callback: CallbackQuery):
    pull_id = int(callback.data.split("_")[2])
    await delete_team(pull_id)

    await callback.message.edit_text(
        "<b>Пулл был успешно удален!</b>",
        reply_markup=await bkb.pulls_cb()
    )