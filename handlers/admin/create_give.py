import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import CantParseEntities
from aiogram_calendar import dialog_cal_callback, DialogCalendar

from app import dp, bot
from states import CreateGiveStates
from .save_giveaway import save_giveaway
from database import GiveAway
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
bt_admin_cancel_action = InlineKeyboardButton('« Назад', callback_data='admin_cancel_action')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
# Универсальные кнопки
bt_admin_edit_give_date = InlineKeyboardButton('« Редактировать дату', callback_data='admin_edit_give_date')
bt_admin_continue_create_give = InlineKeyboardButton('Продолжить »', callback_data='admin_continue_create_give')
bt_admin_add_captcha_for_give = InlineKeyboardButton('Да', callback_data='admin_add_captcha_for_give')
bt_admin_not_add_captcha_for_give = InlineKeyboardButton('Нет', callback_data='admin_not_add_captcha_for_give')
bt_admin_not_add_give_photo = InlineKeyboardButton('Нет', callback_data='admin_not_add_give_photo')
bt_admin_add_give_photo = InlineKeyboardButton('Да', callback_data='admin_add_give_photo')
bt_admin_add_media_video = InlineKeyboardButton('Видео', callback_data='admin_add_media_video')
bt_admin_add_media_photo = InlineKeyboardButton('Фото', callback_data='admin_add_media_photo')
back_button = InlineKeyboardButton('« Назад', callback_data='back')

# Универсальные клавиатуры
kb_back = InlineKeyboardMarkup().add(back_button)
kb_admin_select_media_file_type = InlineKeyboardMarkup().add(bt_admin_add_media_video, bt_admin_add_media_photo).add(back_button)
kb_admin_add_give_photo = InlineKeyboardMarkup().add(bt_admin_not_add_give_photo, bt_admin_add_give_photo)
kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)
kb_admin_add_captcha_for_give = InlineKeyboardMarkup().add(bt_admin_add_captcha_for_give,bt_admin_not_add_captcha_for_give).add(bt_admin_cancel_action)
kb_admin_edit_give_date = InlineKeyboardMarkup().add(bt_admin_edit_give_date, bt_admin_continue_create_give).add(bt_admin_cancel_action)

@dp.callback_query_handler(text='back', state='*')
async def go_back(jam: types.CallbackQuery, state: FSMContext):
    # Логика для возвращения назад
    await jam.message.edit_text(
        'Вы вернулись назад.',
        reply_markup=kb_admin_menu  # Или любая другая клавиатура, которую хотите использовать
    )
    await state.finish()  # Если нужно вернуться в начальное состояние


@dp.callback_query_handler(text=bt_admin_create_give.callback_data, state='*')
async def start_create_give(jam: types.CallbackQuery, state: FSMContext):
    await state.update_data(give_type='button')

    # Сохраняем ID текущего сообщения в состояние
    await state.update_data(prev_message_id=jam.message.message_id)

    # Редактируем сообщение с запросом на ввод названия розыгрыша
    await jam.message.edit_text(
        'Введите название розыгрыша: ',
        reply_markup=kb_back
    )
    await CreateGiveStates.get_name.set()

@dp.message_handler(state=CreateGiveStates.get_name)
async def get_give_name(jam: types.Message, state: FSMContext):
    give_name = jam.text
    keyboard = InlineKeyboardMarkup().add(back_button)

    # Получаем ID предыдущего сообщения
    user_data = await state.get_data()
    prev_message_id = user_data.get('prev_message_id')

    if await GiveAway().exists_give_name(user_id=jam.from_user.id, name=give_name):
        try:
            # Удаляем сообщение пользователя
            await jam.delete()
            # Редактируем предыдущее сообщение, если название существует
            await bot.edit_message_text(
                chat_id=jam.chat.id,
                message_id=prev_message_id,
                text='Розыгрыш с таким названием уже существует, попробуйте еще раз: ',
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Ошибка редактирования сообщения: {e}")
    else:
        await state.update_data(give_name=give_name)

        # Редактируем сообщение с запросом на ввод текста
        new_message = await bot.edit_message_text(
            chat_id=jam.chat.id,
            message_id=prev_message_id,
            text='Введите текст для розыгрыша: \n\n<code>Можно использовать HTML разметку</code>',
            reply_markup=keyboard
        )

        # Сохраняем ID редактированного сообщения
        await state.update_data(bot_message_id=new_message.message_id)

        # Устанавливаем следующее состояние
        await CreateGiveStates.get_text.set()

        # Удаляем сообщение пользователя после успешного получения названия
        await jam.delete()




# Определяем callback_data для кнопок
callback_edit_text = 'edit_text'
callback_continue = 'continue'

@dp.message_handler(state=CreateGiveStates.get_text)
async def get_give_text(jam: types.Message, state: FSMContext):
    give_text = jam.text
    edit_keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Редактировать текст', callback_data=callback_edit_text),
        InlineKeyboardButton('Продолжить', callback_data=callback_continue)
    )

    state_data = await state.get_data()
    bot_message_id = state_data.get("bot_message_id")

    try:
        # Удаляем сообщение пользователя
        await jam.delete()

        # Если ID сообщения сохранено, редактируем его
        if bot_message_id:
            await bot.edit_message_text(
                chat_id=jam.chat.id,
                message_id=bot_message_id,
                text=give_text,
                reply_markup=edit_keyboard
            )
        else:
            # В случае отсутствия ID, отправляем новое сообщение и сохраняем ID
            message = await jam.answer(
                give_text,
                reply_markup=edit_keyboard
            )
            await state.update_data(bot_message_id=message.message_id)

        await state.update_data(give_text=give_text)

    except CantParseEntities:
        await jam.answer(
            'Ошибка в разметке текста, попробуйте еще раз: \n\n<code>Возможно вы забыли закрыть тег</code>',
            reply_markup=kb_back
        )




@dp.callback_query_handler(
    text=[callback_edit_text, callback_continue],
    state=CreateGiveStates.get_text
)
async def edit_give_text(jam: types.CallbackQuery, state: FSMContext):
    callback = jam.data

    if callback == callback_edit_text:
        await jam.message.edit_text(
            'Введите текст для розыгрыша: \n\n<code>Можно использовать HTML разметку</code>',
            reply_markup=kb_back
        )
        await CreateGiveStates.get_text.set()
    elif callback == callback_continue:
        await jam.message.edit_text(
            'Хотите добавить медиафайл для розыгрыша?',
            reply_markup=kb_admin_add_give_photo
        )

@dp.callback_query_handler(
    text=[
        bt_admin_add_give_photo.callback_data,
        bt_admin_not_add_give_photo.callback_data
    ],
    state=CreateGiveStates.get_text
)
async def ask_about_media_files_for_give(jam: types.CallbackQuery, state: FSMContext):
    callback = jam.data

    if callback == bt_admin_add_give_photo.callback_data:
        await jam.message.edit_text(
            'Выберите тип медиафайла: ',
            reply_markup=kb_admin_select_media_file_type
        )
        await CreateGiveStates.get_type_of_media_file.set()

    else:
        await state.update_data(give_media_type=False)

        await jam.message.edit_text(
            "Выберите дату завершения розыгрыша: ",
            reply_markup=await DialogCalendar().start_calendar()
        )
        await CreateGiveStates.get_date.set()


@dp.callback_query_handler(
    text=[
        bt_admin_add_media_video.callback_data,
        bt_admin_add_media_photo.callback_data
    ],
    state=CreateGiveStates.get_type_of_media_file
)
async def get_type_of_media_file(
        jam: types.CallbackQuery,
        state: FSMContext
):
    callback = jam.data


    if callback == bt_admin_add_media_video.callback_data:
        await state.update_data(give_media_type='video')
        await jam.message.edit_text(
            'Отправьте видео для розыгрыша: ',
            reply_markup=kb_back
        )
    else:  # Если это фото
        await state.update_data(give_media_type='photo')
        await jam.message.edit_text(
            'Отправьте фото для розыгрыша: ',
            reply_markup=kb_back
        )

    await CreateGiveStates.get_media_file.set()




@dp.message_handler(
    content_types=[
        'photo',
        'video',
        'animation'
    ],
    state=CreateGiveStates.get_media_file
)
async def download_give_photo(jam: types.Message, state: FSMContext):
    # Получаем ID сообщения бота, чтобы удалить его позже
    state_data = await state.get_data()
    bot_message_id = state_data.get("bot_message_id")

    # Если пользователь отправил фото, получаем его file_id
    if jam.content_type == 'photo':
        file_id = jam.photo[-1].file_id
    else:
        file_id = jam[jam.content_type].file_id

    await state.update_data(give_media_id=file_id)

    # Удаляем предыдущее сообщение бота, если оно существует
    if bot_message_id:
        try:
            await bot.delete_message(chat_id=jam.chat.id, message_id=bot_message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отвечаем пользователю
    await jam.answer(
        "Выберите дату завершения розыгрыша: ",
        reply_markup=await DialogCalendar().start_calendar()
    )
    await CreateGiveStates.get_date.set()



@dp.callback_query_handler(
    dialog_cal_callback.filter(),
    state=CreateGiveStates.get_date
)
async def get_over_date_give(jam: types.CallbackQuery, state: FSMContext, callback_data):
    selected, date = await DialogCalendar().process_selection(jam, callback_data)

    if selected:
        await state.update_data(give_over_date=date)

        await jam.message.edit_text(
            f'Выбранная дата: {date.strftime("%d/%m/%Y")}',
            reply_markup=kb_admin_edit_give_date  # Используем новую клавиатуру
        )


@dp.callback_query_handler(
    text=[
        bt_admin_edit_give_date.callback_data,
        bt_admin_continue_create_give.callback_data
    ],
    state=CreateGiveStates.get_date
)

async def ask_about_edit_give_date(jam: types.CallbackQuery, state: FSMContext):
    callback = jam.data
    if callback == bt_admin_edit_give_date.callback_data:
        await jam.message.edit_text(
            "Выберите дату завершения розыгрыша: ",
            reply_markup=await DialogCalendar().start_calendar()
        )

    else:
        state_data = await state.get_data()
        if state_data['give_type'] == 'button':
            await jam.message.edit_text(
                'Хотите добавить капчу для розыгрыша? (Защита от ботов)',
                reply_markup=kb_admin_add_captcha_for_give  # Используем новую клавиатуру для капчи
            )
            await CreateGiveStates.get_answer_of_captcha.set()
        else:
            await state.update_data(give_captcha=False)

            await jam.message.edit_text(
                'Введите время завершения розыгрыша по МСК: \n\n<code>Например: 09:23</code>',
                reply_markup=kb_back  # Используем клавиатуру с кнопкой "Назад"
            )
            await CreateGiveStates.get_time.set()


@dp.callback_query_handler(
    text=[
        bt_admin_add_captcha_for_give.callback_data,
        bt_admin_not_add_captcha_for_give.callback_data
    ],
    state=CreateGiveStates.get_answer_of_captcha
)
async def ask_about_captcha_for_give(jam: types.CallbackQuery, state: FSMContext):
    callback = jam.data

    if callback == bt_admin_add_captcha_for_give.callback_data:
        await state.update_data(give_captcha=True)
    else:
        await state.update_data(give_captcha=False)

    # Сохраняем ID сообщения в состояние
    await state.update_data(prev_message_id=jam.message.message_id)

    await jam.message.edit_text(
        'Введите время завершения розыгрыша по МСК: \n\n<code>Например: 09:23</code>',
        reply_markup=kb_back
    )
    await CreateGiveStates.get_time.set()


@dp.message_handler(
    state=CreateGiveStates.get_time,
    regexp=re.compile(r'\d{2}:\d{2}')
)
async def get_over_time_for_give(jam: types.Message, state: FSMContext):
    hours, minutes = jam.text.split(':')

    if hours.isdigit() and int(hours) in range(0, 24) and minutes.isdigit() and int(minutes) in range(0, 60):
        await state.update_data(give_over_time=jam.text)
        await jam.delete()  # Удаляем сообщение пользователя

        # Получаем данные из состояния
        user_data = await state.get_data()
        prev_message_id = user_data.get('prev_message_id')

        # Редактируем сообщение для запроса количества победителей
        await bot.edit_message_text(
            chat_id=jam.from_user.id,
            message_id=prev_message_id,
            text='Введите количество победителей: ',
            reply_markup=kb_back  # Здесь можно оставить старую клавиатуру, если она нужна
        )
        await CreateGiveStates.get_winners_count.set()
    else:
        await jam.answer(
            '🚫  Неверный формат времени, попробуйте еще раз: ',
            reply_markup=kb_back  # Используем клавиатуру с кнопкой "Назад"
        )


@dp.message_handler(
    state=CreateGiveStates.get_winners_count,
    regexp=re.compile(r'\d+')
)
async def get_count_winners_for_give(jam: types.Message, state: FSMContext):
    await state.update_data(give_winners_count=int(jam.text))
    await jam.delete()  # Удаляем сообщение пользователя

    # Получаем данные из состояния
    user_data = await state.get_data()
    prev_message_id = user_data.get('prev_message_id')

    await save_giveaway(
        user_id=jam.from_user.id,
        state=state,
    )

    # Редактируем сообщение о создании розыгрыша
    await bot.edit_message_text(
        chat_id=jam.from_user.id,
        message_id=prev_message_id,
        text='✅  Розыгрыш успешно создан',
        reply_markup=kb_admin_menu  # Используем новую клавиатуру
    )

    await state.finish()
