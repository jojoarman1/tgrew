from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from database import GiveAway, TelegramChannel, GiveAwayStatistic
from states import CreatedGivesStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bt_admin_start_give = InlineKeyboardButton('Запустить', callback_data='admin_start_give')
bt_admin_delete_give = InlineKeyboardButton('Удалить', callback_data='admin_delete_give')
bt_admin_manage_channels = InlineKeyboardButton('Каналы', callback_data='admin_manage_channels')
bt_admin_change_over_date = InlineKeyboardButton('Изменить дату окончания', callback_data='admin_change_over_date')

bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)
kb_admin_manage_created_gives = InlineKeyboardMarkup().add(bt_admin_start_give, bt_admin_delete_give).add(bt_admin_manage_channels).add(bt_admin_change_over_date).add(
    bt_admin_cancel_action
)


@dp.callback_query_handler(
    text=bt_admin_delete_give.callback_data,
    state=CreatedGivesStates.manage_selected_give,
)
async def delete_give(
    jam: types.CallbackQuery,
    state: FSMContext
):
    state_data = await state.get_data()
    give_callback_value = state_data.get('give_callback_value')

    await GiveAway().delete_give(
        callback_value=give_callback_value
    )

    await TelegramChannel().delete_channel(
        give_callback_value=give_callback_value
    )

    await GiveAwayStatistic().delete_statistic(
        giveaway_callback_value=give_callback_value
    )


    await jam.message.edit_text(
        '✅  <b>Розыгрыш успешно удален</b>',
        reply_markup=kb_admin_menu
    )
    await state.finish()