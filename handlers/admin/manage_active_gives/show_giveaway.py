from aiogram import types
from aiogram.dispatcher import FSMContext
from app import dp
from database import GiveAway

from states import ActiveGivesStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем кнопки с более строгим стилем
bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
bt_admin_show_statistic = InlineKeyboardButton('Статистика', callback_data='admin_show_statistic')
bt_admin_stop_give = InlineKeyboardButton('Остановить', callback_data='admin_stop_give')
bt_admin_cancel_action = InlineKeyboardButton('Назад', callback_data='admin_cancel_action')

# Создаем клавиатуры
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_active_gives = InlineKeyboardMarkup().add(bt_admin_show_statistic, bt_admin_stop_give).add(bt_admin_cancel_action)
kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)

# Обработчик для выбора активного розыгрыша
@dp.callback_query_handler(
    lambda c: c.data != bt_admin_cancel_action.callback_data,
    state=ActiveGivesStates.select_give,
)
async def show_active_selected_give(
    jam: types.CallbackQuery,
    state: FSMContext,
    give_callback_value: str = False
):
    if not give_callback_value:
        give_callback_value = jam.data
    await state.update_data(give_callback_value=give_callback_value)

    give_data = await GiveAway().get_give_data(
        user_id=jam.from_user.id,
        callback_value=give_callback_value
    )

    message_text = ''
    for give in give_data:
        await state.update_data(type_of_give=give['type'])
        message_text = (
            f"<b>Название розыгрыша:</b> <code>{give['name']}</code>\n\n"
            f"<b>Описание:</b>\n{give['text']}\n\n"
            f"<b>Фото:</b> <code>{'Нет' if give['photo_id'] == 'False' else 'Да'}</code>\n"
            f"<b>Дата окончания:</b> <code>{give['over_date']}</code>\n"
            f"<b>Капча:</b> <code>{'Да' if give['captcha'] else 'Нет'}</code>\n"
            f"<b>Количество победителей:</b> <code>{give['winners_count']}</code>"
        )

    await jam.message.edit_text(
        message_text,
        reply_markup=kb_admin_active_gives
    )
    await ActiveGivesStates.manage_selected_give.set()
