from aiogram.fsm.state import State, StatesGroup


class AddAdmin(StatesGroup):
    tg_id = State()


class AddUser(StatesGroup):
    username = State()
    created_at = State()


class EditUser(StatesGroup):
    new_username = State()
    new_created_at = State()


class AddNotify(StatesGroup):
    username = State()
    notify_date = State()


class EditNotify(StatesGroup):
    new_username = State()
    new_notify_date = State()


class AddTeam(StatesGroup):
    name = State()


class EditTeam(StatesGroup):
    new_name = State()


class AddTeamUser(StatesGroup):
    tg_id = State()