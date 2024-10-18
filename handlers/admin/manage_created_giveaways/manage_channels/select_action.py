from aiogram import types

from app import bot, dp
from states import CreatedGivesStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bt_admin_add_channel = InlineKeyboardButton('Добавить канал', callback_data='admin_add_channel')
bt_admin_active_channels = InlineKeyboardButton('Подключенные каналы', callback_data='admin_active_channels')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_manage_channels = InlineKeyboardMarkup().add(bt_admin_add_channel).add(bt_admin_active_channels).add(bt_admin_cancel_action)

bt_admin_manage_channels = InlineKeyboardButton('Каналы', callback_data='admin_manage_channels')


@dp.callback_query_handler(
    text=bt_admin_manage_channels.callback_data,
    state=CreatedGivesStates.manage_selected_give,
)
async def process_manage_channels(jam: types.CallbackQuery):
    await jam.message.edit_text(
        'Выберите действие: ',
        reply_markup=kb_admin_manage_channels
    )
    await CreatedGivesStates.manage_channels.set()
