from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from database import TelegramChannel
from states import CreatedGivesStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bt_admin_add_channel = InlineKeyboardButton('Добавить канал', callback_data='admin_add_channel')
bt_admin_active_channels = InlineKeyboardButton('Подключенные каналы', callback_data='admin_active_channels')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_manage_channels = InlineKeyboardMarkup().add(bt_admin_add_channel).add(bt_admin_active_channels).add(bt_admin_cancel_action)

bt_admin_add_group_for_channel = InlineKeyboardButton('Добавить группу', callback_data='admin_add_group')
bt_admin_delete_channel = InlineKeyboardButton('Удалить канал', callback_data='admin_delete_channel')
kb_admin_manage_selected_channel = InlineKeyboardMarkup().add(bt_admin_add_group_for_channel).add(bt_admin_delete_channel).add(bt_admin_cancel_action)



@dp.callback_query_handler(
    text=bt_admin_delete_channel.callback_data,
    state=CreatedGivesStates.show_connected_channel
)
async def delete_channel(
    jam: types.CallbackQuery,
    state: FSMContext
):
    state_data = await state.get_data()

    await TelegramChannel().delete_channel(
        channel_callback_value=state_data['channel_callback_value']
    )

    await jam.message.edit_text(
        '✅  <b>Канал успешно удален</b>',
        reply_markup=kb_admin_manage_channels
    )

    await CreatedGivesStates.manage_channels.set()
