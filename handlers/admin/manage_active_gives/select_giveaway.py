from aiogram import types
from app import dp
from database import GiveAway
from states import ActiveGivesStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)


@dp.callback_query_handler(
    text=bt_admin_started_gives.callback_data,
    state='*'
)
async def show_active_gives(jam: types.CallbackQuery):
    markup = await GiveAway().get_keyboard_of_active_gives(
        user_id=jam.from_user.id
    )

    if markup:
        markup.add(bt_admin_cancel_action)

        await jam.message.edit_text(
            '💎  <b>Выберите розыгрыш для просмотра:</b> ',
            reply_markup=markup
        )
        await ActiveGivesStates.select_give.set()

    else:
        await jam.answer('У вас нет активных розыгрышей')
