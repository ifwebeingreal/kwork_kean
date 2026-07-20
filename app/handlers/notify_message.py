from datetime import datetime

import pytz
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards.builder as bkb
import app.keyboards.inline as ikb

from app.database.requests.notify.add import set_notify
from app.database.requests.notify.select import get_notify
from app.database.requests.notify.delete import delete_notify
from app.database.requests.notify.update import update_notify_date, update_notify_username

from app.states import AddNotify, EditNotify


notify = Router()


@notify.callback_query(F.data == "all_notify")
async def all_notify(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Добавленные напоминания:</b>",
        reply_markup=await bkb.notify_cb()
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
        date_obj = datetime.strptime(message.text, "%d.%m.%Y %H:%M")

        # Получаем Москву
        msk_tz = pytz.timezone('Europe/Moscow')
        now_msk = datetime.now(msk_tz).replace(tzinfo=None)  # Чистое время МСК

        if date_obj < now_msk:
            await message.answer("❌ Дата и время не могут быть в прошлом (по МСК)!",
                                 reply_markup=ikb.admin_cancel)
            return

        data = await state.get_data()
        await set_notify(data.get("username"), date_obj)

        await message.answer(f"✅ Создано на {message.text} (МСК)",
                             reply_markup=await bkb.notify_cb())
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Неверный формат!",
                             reply_markup=ikb.admin_cancel)


@notify.callback_query(F.data.startswith("notify_"))
async def check_notify(callback: CallbackQuery):
    notify_id = int(callback.data.split("notify_")[1])
    notify_info = await get_notify(notify_id)

    await callback.message.edit_text(
        f"<b>Панель управления напоминанием</b>\n\n"
        f"<b>Username:</b> {notify_info.username}\n"
        f"<b>Дата напоминания:</b> {notify_info.notify_date}\n\n"
        f"<i>Выберите действие:</i>\n",
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

        await update_notify_username(notify_id, username)
        notify_info = await get_notify(notify_id)

        await message.answer(
            f"<b>Панель управления напоминанием</b>\n\n"
            f"<b>Username:</b> {notify_info.username}\n"
            f"<b>Дата напоминания:</b> {notify_info.notify_date}\n\n"
            f"<i>Выберите действие:</i>\n",
            reply_markup=await bkb.edit_notify(notify_id)
        )

        await state.clear()

    else:
        await message.answer("Username должен быть текстом до 200 символов!",
                             reply_markup=ikb.admin_cancel)


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
        date_obj = datetime.strptime(message.text, "%d.%m.%Y %H:%M")

        # Получаем Москву
        msk_tz = pytz.timezone('Europe/Moscow')
        now_msk = datetime.now(msk_tz).replace(tzinfo=None)  # Чистое время МСК

        if date_obj < now_msk:
            await message.answer("❌ Дата и время не могут быть в прошлом (по МСК)!",
                                 reply_markup=ikb.admin_cancel)
            return

        data = await state.get_data()

        notify_id = data.get("notify_id")

        await update_notify_date(notify_id, date_obj)
        notify_info = await get_notify(notify_id)

        await message.answer(
            f"<b>Панель управления напоминанием</b>\n\n"
            f"<b>Username:</b> {notify_info.username}\n"
            f"<b>Дата напоминания:</b> {notify_info.notify_date}\n\n"
            f"<i>Выберите действие:</i>\n",
            reply_markup=await bkb.edit_notify(notify_id)
        )

        await state.clear()

    except ValueError:
        await message.answer("⚠️ Неверный формат!",
                             reply_markup=ikb.admin_cancel)



@notify.callback_query(F.data.startswith("delete_notify_"))
async def remove_notify(callback: CallbackQuery):
    notify_id = int(callback.data.split("_")[2])
    await delete_notify(notify_id)

    await callback.message.edit_text(
        "<b>Напоминание было успешно удалено!</b>\n",
        reply_markup=await bkb.notify_cb()
    )


