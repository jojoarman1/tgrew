from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from database import GiveAway
from states import CreatedGivesStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
bt_admin_start_give = InlineKeyboardButton('Запустить', callback_data='admin_start_give')
bt_admin_delete_give = InlineKeyboardButton('Удалить', callback_data='admin_delete_give')
bt_admin_manage_channels = InlineKeyboardButton('Каналы', callback_data='admin_manage_channels')
bt_admin_change_over_date = InlineKeyboardButton('Изменить дату окончания', callback_data='admin_change_over_date')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
kb_back = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)
kb_admin_manage_created_gives = InlineKeyboardMarkup().add(bt_admin_start_give, bt_admin_delete_give).add(bt_admin_manage_channels).add(bt_admin_change_over_date).add(
    bt_admin_cancel_action
)

@dp.callback_query_handler(
    text=bt_admin_created_gives.callback_data,
    state='*'
)
async def show_created_gives(jam: types.CallbackQuery):
    markup = await GiveAway().get_keyboard_of_created_gives(
        user_id=jam.from_user.id
    )

    if markup:
        markup.add(bt_admin_cancel_action)

        await jam.message.edit_text(
            '💎  <b>Выберите розыгрыш для просмотра:</b> ',
            reply_markup=markup
        )
        await CreatedGivesStates.select_give.set()

    else:
        await jam.answer('У вас нет созданных розыгрышей')




@dp.callback_query_handler(
    lambda c: c.data != bt_admin_cancel_action.callback_data,
    state=CreatedGivesStates.select_give,
)
async def show_selected_give(
    jam: types.CallbackQuery,
    state: FSMContext,
    give_callback_value: str = False
):
    await CreatedGivesStates.manage_selected_give.set()


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
        message_text = f'<b>Тип розыгрыша:</b> <code>{"По комментариям" if give["type"] == "comments" else "По кнопке"}</code>\n<b>Название розыгрыша:</b> <code>{give["name"]}</code>\n\n<b>Текст:</b>\n{give["text"]}\n\n<b>Фото:</b> <code>{"Нет" if give["photo_id"] is None else "Да"}</code>\n<b>Видео:</b> <code>{"Нет" if give["video_id"] is None else "Да"}</code>\n<b>Капча:</b> <code' \
                       f'>{"Да" if give["captcha"] else "Нет"}</code>\n<b>Количество ' \
                       f'победителей:</b> <code' \
                       f'>{give["winners_count"]}</code>\n<b>Дата окончания:</b> <code>{give["over_date"]}</code>'


    await jam.message.edit_text(
        message_text,
        reply_markup=kb_admin_manage_created_gives
    )
