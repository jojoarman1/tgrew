from aiogram import types
from aiogram.dispatcher import FSMContext
from app import dp, bot
from states import CreatedGivesStates
from database import GiveAway, TelegramChannel, GiveAwayStatistic
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
bt_admin_show_statistic = InlineKeyboardButton('Статистика', callback_data='admin_show_statistic')
bt_admin_stop_give = InlineKeyboardButton('Остановить', callback_data='admin_stop_give')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
kb_admin_active_gives = InlineKeyboardMarkup().add(bt_admin_show_statistic, bt_admin_stop_give).add(bt_admin_cancel_action)
kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)
bt_admin_start_give = InlineKeyboardButton('Запустить', callback_data='admin_start_give')


@dp.callback_query_handler(
    text=bt_admin_start_give.callback_data,
    state=CreatedGivesStates.manage_selected_give
)
async def start_give(jam: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    give_callback_value = state_data['give_callback_value']

    give_model = GiveAway()
    give_data = await give_model.get_give_data(
        user_id=jam.from_user.id,
        callback_value=give_callback_value
    )

    post_link = ''
    message_id = 0

    for give in give_data:
        message_text = f'{give["name"]}\n\n{give["text"]}\n\nКоличество победителей: {give["winners_count"]}\nДата завершения: {give["over_date"].strftime("%d.%m.%Y %H:%M")} по МСК'

        # Получение данных о боте для формирования ссылки на участие
        bot_data = await bot.get_me()
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                text='Участвовать',
                url=f'https://t.me/{bot_data.username}?start={give_callback_value}'
            )
        )

        # В зависимости от типа контента отправляем пользователю текст, фото или видео
        if give["photo_id"] is None and give["video_id"] is None:
            message = await bot.send_message(
                chat_id=jam.from_user.id,
                text=message_text,
                reply_markup=markup if give["type"] == 'button' else None
            )

        elif give["photo_id"]:
            message = await bot.send_photo(
                chat_id=jam.from_user.id,
                photo=give["photo_id"],
                caption=message_text,
                reply_markup=markup if give["type"] == 'button' else None
            )

        elif give["video_id"]:
            message = await bot.send_video(
                chat_id=jam.from_user.id,
                video=give["video_id"],
                caption=message_text,
                reply_markup=markup if give["type"] == 'button' else None
            )

        post_link = f'https://t.me/{bot_data.username}/{message.message_id}'
        message_id = message.message_id

    # Сохраняем данные о посте в базе данных
    await GiveAwayStatistic().add_statistic(
        giveaway_callback_value=give_callback_value,
        members=[],
        winners=[],
        post_link=post_link
    )

    # Обновляем статус розыгрыша в базе данных
    await give_model.update_give_status(
        callback_value=give_callback_value,
        status=True
    )

    # Отправляем сообщение пользователю о запуске розыгрыша
    await jam.message.edit_text(
        '<b> Розыгрыш успешно запущен</b> ✅',
        reply_markup=kb_admin_menu
    )
    await state.finish()





