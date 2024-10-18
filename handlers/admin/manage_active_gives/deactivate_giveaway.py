from aiogram import types
from aiogram.dispatcher import FSMContext
from app import dp
from database import GiveAway, GiveAwayStatistic
from states import ActiveGivesStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
bt_admin_show_statistic = InlineKeyboardButton('Статистика', callback_data='admin_show_statistic')
bt_admin_stop_give = InlineKeyboardButton('Остановить', callback_data='admin_stop_give')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_active_gives = InlineKeyboardMarkup().add(bt_admin_show_statistic, bt_admin_stop_give).add(bt_admin_cancel_action)
kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)



@dp.callback_query_handler(
    text=bt_admin_stop_give.callback_data,
    state=ActiveGivesStates.manage_selected_give
)
async def stop_give(jam: types.CallbackQuery, state: FSMContext):
    await ActiveGivesStates.stop_give.set()
    state_data = await state.get_data()

    await GiveAway().update_give_status(
        callback_value=state_data['give_callback_value'],
        status=False
    )

    await GiveAwayStatistic().filter(
        giveaway_callback_value=state_data['give_callback_value']
    ).delete()

    await jam.message.edit_text(
        '✅  <b>Розыгрыш остановлен</b>',
        reply_markup=kb_admin_menu
    )
    await state.finish()