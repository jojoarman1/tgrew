from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from database import TelegramChannel
from states import CreateGiveStates, CreatedGivesStates

from .manage_created_giveaways import show_created_gives, show_selected_give, process_manage_channels
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_text = "Главное меню:"

bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)


@dp.callback_query_handler(
    text=bt_admin_cancel_action.callback_data,
    state='*'
)
async def cancel_admin_action(
    jam: types.CallbackQuery,
    state: FSMContext
):
    current_state = await state.get_state()

    if current_state in CreateGiveStates.states_names:
        await jam.message.edit_text(
            start_text,
            reply_markup=kb_admin_menu
        )
        await state.finish()

    elif current_state == CreatedGivesStates.manage_selected_give.state:
        await show_created_gives(
            jam=jam
        )

    elif current_state == CreatedGivesStates.select_give.state:
        await jam.message.edit_text(
            start_text,
            reply_markup=kb_admin_menu
        )
        await state.finish()

    elif current_state == CreatedGivesStates.manage_channels.state:
        state_data = await state.get_data()

        await show_selected_give(
            jam=jam,
            state=state,
            give_callback_value=state_data['give_callback_value']
        )

    elif current_state == CreatedGivesStates.add_channel.state:
        await process_manage_channels(
            jam=jam
        )

    elif current_state == CreatedGivesStates.show_connected_channel.state:
        markup = await TelegramChannel().get_keyboard(
            owner_id=jam.from_user.id,
        )

        if markup:
            markup.add(bt_admin_cancel_action)

            await jam.message.edit_text(
                'Выберите канал для просмотра: ',
                reply_markup=markup
            )

            await CreatedGivesStates.select_connected_channel.set()

        else:
            await process_manage_channels(
                jam=jam
            )

    elif current_state == CreatedGivesStates.select_connected_channel.state:
        await process_manage_channels(
            jam=jam
        )

    else:
        await jam.message.edit_text(
            start_text,
            reply_markup=kb_admin_menu
        )
        await state.finish()
