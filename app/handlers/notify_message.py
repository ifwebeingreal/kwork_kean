from datetime import datetime

import pytz
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards.builder as bkb
import app.keyboards.inline as ikb
from app.database.requests.admin.select import get_admin_by_tg_id

from app.database.requests.notify.add import set_notify
from app.database.requests.notify.select import get_notify, get_notify_by_team_id, get_all_notify
from app.database.requests.notify.delete import delete_notify
from app.database.requests.notify.update import update_notify_date, update_notify_username, update_notify_team_id
from app.database.requests.team.select import get_team
from app.database.requests.user_team_member.select import get_user_by_tg_id

from app.states import AddNotify, EditNotify


notify = Router()


async def get_notify_text(notify_info, tg_id: int):
    admin = await get_admin_by_tg_id(tg_id)

    text = (
        f"<b>Панель управления напоминанием</b>\n\n"
        f"<b>Username:</b> {notify_info.username}\n"
        f"<b>Дата напоминания:</b> {notify_info.notify_date}\n"
    )

    if admin:
        team = await get_team(notify_info.team_id)
        text += f"<b>Пулл:</b> {team.name if team else '-'}\n"

    text += "\n<i>Выберите действие:</i>"

    return text


@notify.callback_query(F.data == "all_notify")
async def all_notify(callback: CallbackQuery):
    tg_id = callback.from_user.id

    admin = await get_admin_by_tg_id(tg_id)
    team_member = await get_user_by_tg_id(tg_id)

    if admin:
        notifies = await get_all_notify()

    elif team_member:
        notifies = await get_notify_by_team_id(team_id=team_member.team_id)

    else:
        await callback.answer(
            "У вас нет доступа!",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "<b>Добавленные напоминания:</b>",
        reply_markup=await bkb.notify_cb(notifies)
    )


@notify.callback_query(F.data == "add_notify")
async def add_notify(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Введите username:</b>",
        reply_markup=ikb.admin_cancel
    )

    await state.set_state(AddNotify.username)


@notify.message(AddNotify.username)
async def check_username(message: Message, state: FSMContext):
    if message.text and len(message.text) <= 200:
        await state.update_data(username=message.text)

        msk_tz = pytz.timezone('Europe/Moscow')
        now_msk = datetime.now(msk_tz).replace(tzinfo=None)  # Чистое время МСК

        await message.answer(
            "<b>Введите дату и время для напоминания:</b>\n\n"
            "Формат: <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n"
            f"Пример (МСК): <code>{now_msk.strftime('%d.%m.%Y %H:%M')}</code>",  # Здесь теперь МСК
            reply_markup=ikb.admin_cancel
        )

        await state.set_state(AddNotify.notify_date)
    else:
        await message.answer("Username должен быть текстом до 200 символов!",
                             reply_markup=ikb.admin_cancel)


@notify.message(AddNotify.notify_date)
async def process_notify_date(message: Message, state: FSMContext):
    try:
        date_obj = datetime.strptime(
            message.text,
            "%d.%m.%Y %H:%M"
        )

        msk_tz = pytz.timezone('Europe/Moscow')
        now_msk = datetime.now(msk_tz).replace(tzinfo=None)

        if date_obj < now_msk:
            await message.answer(
                "❌ Дата и время не могут быть в прошлом (по МСК)!",
                reply_markup=ikb.admin_cancel
            )
            return

        data = await state.get_data()

        username = data.get("username")
        tg_id = message.from_user.id

        admin = await get_admin_by_tg_id(tg_id)
        team_member = await get_user_by_tg_id(tg_id)

        if admin:
            await state.update_data(
                notify_date=date_obj
            )

            await message.answer(
                "<b>Выберите пул для напоминания:</b>",
                reply_markup=await bkb.users_pulls_cb()
            )

            await state.set_state(AddNotify.select_team)

        elif team_member:
            await set_notify(
                username,
                date_obj,
                team_id=team_member.team_id
            )

            await message.answer(
                f"✅ Создано на {message.text} (МСК)",
                reply_markup=await bkb.notify_cb(
                    await get_notify_by_team_id(team_id=team_member.team_id)
                )
            )

            await state.clear()

    except ValueError:
        await message.answer(
            "⚠️ Неверный формат!",
            reply_markup=ikb.admin_cancel
        )


@notify.callback_query(F.data.startswith("notifypull_"))
async def select_notify_team(
        callback: CallbackQuery,
        state: FSMContext
):
    team_id = int(callback.data.split("_")[1])

    data = await state.get_data()

    username = data.get("username")
    notify_date = data.get("notify_date")

    await set_notify(
        username,
        notify_date,
        team_id=team_id
    )

    await callback.message.edit_text(
        "<b>Напоминание успешно создано!</b>",
        reply_markup=await bkb.notify_cb(
            await get_notify_by_team_id(team_id=team_id)
        )
    )

    await state.clear()


@notify.callback_query(F.data.startswith("notify_"))
async def check_notify(callback: CallbackQuery):
    notify_id = int(callback.data.split("notify_")[1])

    notify_info = await get_notify(notify_id)

    admin = await get_admin_by_tg_id(callback.from_user.id)

    text = (
        f"<b>Панель управления напоминанием</b>\n\n"
        f"<b>Username:</b> {notify_info.username}\n"
        f"<b>Дата напоминания:</b> {notify_info.notify_date}\n"
    )

    if admin:
        team = await get_team(notify_info.team_id)

        text += (
            f"<b>Пулл:</b> {team.name if team else '-'}\n"
        )

    text += "\n<i>Выберите действие:</i>\n"

    await callback.message.edit_text(
        text,
        reply_markup=await bkb.edit_notify(notify_id)
    )


@notify.callback_query(F.data.startswith("edit_notify_username_"))
async def edit_notify_username(callback: CallbackQuery, state: FSMContext):
    notify_id = int(callback.data.split("_")[3])

    await callback.message.edit_text(
        "<b>Введите новый username для уведомлений:</b>",
        reply_markup=ikb.admin_cancel
    )

    await state.set_state(EditNotify.new_username)
    await state.update_data(notify_id=notify_id)


@notify.message(EditNotify.new_username)
async def check_new_username(message: Message, state: FSMContext):
    if message.text and len(message.text) <= 200:
        await state.update_data(username=message.text)

        data = await state.get_data()

        notify_id = data.get("notify_id")
        username = data.get("username")

        await update_notify_username(
            notify_id,
            username
        )

        notify_info = await get_notify(notify_id)

        await message.answer(
            await get_notify_text(
                notify_info,
                message.from_user.id
            ),
            reply_markup=await bkb.edit_notify(notify_id)
        )

        await state.clear()

    else:
        await message.answer(
            "Username должен быть текстом до 200 символов!",
            reply_markup=ikb.admin_cancel
        )


@notify.callback_query(F.data.startswith("edit_notify_date_"))
async def edit_notify_date(callback: CallbackQuery, state: FSMContext):
    notify_id = int(callback.data.split("_")[3])

    msk_tz = pytz.timezone('Europe/Moscow')
    now_msk = datetime.now(msk_tz).replace(tzinfo=None)  # Чистое время МСК

    await callback.message.edit_text(
        "<b>Введите дату и время для напоминания:</b>\n\n"
        "Формат: <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n"
        f"Пример (МСК): <code>{now_msk.strftime('%d.%m.%Y %H:%M')}</code>",  # Здесь теперь МСК
        reply_markup=ikb.admin_cancel
    )

    await state.set_state(EditNotify.new_notify_date)
    await state.update_data(notify_id=notify_id)


@notify.message(EditNotify.new_notify_date)
async def check_new_notify_date(message: Message, state: FSMContext):
    try:
        date_obj = datetime.strptime(
            message.text,
            "%d.%m.%Y %H:%M"
        )

        msk_tz = pytz.timezone('Europe/Moscow')
        now_msk = datetime.now(msk_tz).replace(tzinfo=None)

        if date_obj < now_msk:
            await message.answer(
                "❌ Дата и время не могут быть в прошлом (по МСК)!",
                reply_markup=ikb.admin_cancel
            )
            return

        data = await state.get_data()

        notify_id = data.get("notify_id")

        await update_notify_date(
            notify_id,
            date_obj
        )

        notify_info = await get_notify(notify_id)

        await message.answer(
            await get_notify_text(
                notify_info,
                message.from_user.id
            ),
            reply_markup=await bkb.edit_notify(notify_id)
        )

        await state.clear()

    except ValueError:
        await message.answer(
            "⚠️ Неверный формат!",
            reply_markup=ikb.admin_cancel
        )


@notify.callback_query(F.data.startswith("edit_notify_pull_"))
async def edit_notify_pull(callback: CallbackQuery, state: FSMContext):
    notify_id = int(callback.data.split("_")[3])

    await state.update_data(
        notify_id=notify_id
    )

    await callback.message.edit_text(
        "<b>Выберите новый пул:</b>",
        reply_markup=await bkb.users_pulls_cb()
    )

    await state.set_state(EditNotify.new_select_team)


@notify.callback_query(
    EditNotify.new_select_team,
    F.data.startswith("userspull_")
)
async def select_new_notify_team(
        callback: CallbackQuery,
        state: FSMContext
):
    team_id = int(callback.data.split("_")[1])

    data = await state.get_data()

    notify_id = data.get("notify_id")

    await update_notify_team_id(
        notify_id,
        team_id
    )

    # получаем уже обновленное напоминание
    notify_info = await get_notify(notify_id)

    await callback.message.edit_text(
        await get_notify_text(
            notify_info,
            callback.from_user.id
        ),
        reply_markup=await bkb.edit_notify(notify_id)
    )

    await state.clear()


@notify.callback_query(F.data.startswith("delete_notify_"))
async def remove_notify(callback: CallbackQuery):
    notify_id = int(callback.data.split("_")[2])
    await delete_notify(notify_id)

    tg_id = callback.from_user.id

    admin = await get_admin_by_tg_id(tg_id)
    team_member = await get_user_by_tg_id(tg_id)

    if admin:
        notifies = await get_all_notify()

    elif team_member:
        notifies = await get_notify_by_team_id(team_id=team_member.team_id)

    else:
        await callback.answer(
            "У вас нет доступа!",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "<b>Напоминание было успешно удалено!</b>\n",
        reply_markup=await bkb.notify_cb(notifies)
    )


