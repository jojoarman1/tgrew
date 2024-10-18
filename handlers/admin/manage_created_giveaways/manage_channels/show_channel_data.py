from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from database import TelegramChannel
from states import CreatedGivesStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
bt_admin_add_group_for_channel = InlineKeyboardButton('Добавить группу', callback_data='admin_add_group')
bt_admin_delete_channel = InlineKeyboardButton('Удалить канал', callback_data='admin_delete_channel')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_manage_selected_channel = InlineKeyboardMarkup().add().add(bt_admin_delete_channel).add(bt_admin_cancel_action)



@dp.callback_query_handler(
    lambda c: c.data != bt_admin_cancel_action.callback_data,
    state=CreatedGivesStates.select_connected_channel,
)
async def show_selected_channel(
    jam: types.CallbackQuery,
    state: FSMContext
):
    channel_callback_value = jam.data
    await state.update_data(channel_callback_value=channel_callback_value)

    channel_data = await TelegramChannel().get_channel_data(
        channel_callback_value=channel_callback_value
    )

    for channel in channel_data:
        await jam.message.edit_text(
            f'<b>ID канала:</b> <code>{channel["channel_id"]}</code>\n<b>Название канала:</b> <code>{channel["name"]}</code>',
            reply_markup=kb_admin_manage_selected_channel
        )

    await CreatedGivesStates.show_connected_channel.set()
