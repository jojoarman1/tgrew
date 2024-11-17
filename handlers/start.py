from aiogram import types
from aiogram.dispatcher import FSMContext
from app import dp
from .admin.functions_for_active_gives.handle_new_members_from_button_giveaways import manage_new_members_from_button_gives
from .admin.functions_for_active_gives.check_channels_subscriptions import check_channels_subscriptions
from database import TemporaryUsers, GiveAwayStatistic, ReferralStatistic
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_text = "Главное меню:"
admin_id = 1247124939  # Замените на ID администратора

# Добавляем новый текст для раздела вопросов и ответов
faq_texts = {
    'how_it_works': (
        "💡 <b>Как это работает?</b>\n\n"
        "Чтобы участвовать в розыгрышах, вам необходимо подписаться на наших спонсоров. "
        "Нажмите кнопку «Участвовать» в паблике где происходит розыгрыш, и вы увидите условия участия — это может быть минимальное количество приглашённых друзей или обязательная подписка на указанных спонсоров. "
        "Выполнив все условия, вы сможете претендовать на победу и получить шанс на выигрыш!"
    ),
    'referral_system': (
        "👥 <b>Система рефералов</b>\n\n"
        "Если ваш реферал выигрывает в розыгрыше, то вместе с ним выигрываете и вы — даже если сами не участвовали! "
        "Приглашая друзей, вы не только увеличиваете шансы на победу для них, но и получаете возможность стать победителем вместе с ними. "
        "Это добавляет дополнительный стимул привлекать новых участников и получать выгоду от их успехов!"
    ),
    'invitation_rules': (
        "🤝 <b>Правила приглашения друзей (рефералов)</b>\n\n"
        "Приглашение работает следующим образом: если вы уже зашли в бота без реферальной ссылки, другие пользователи не смогут вас пригласить. "
        "Также самоприглашение невозможно, как и приглашение пользователей, которые уже были приглашены кем-то другим. "
        "Приглашать можно только тех, кто еще не заходил в бота.\n"
    )
}

required_referrals = 1

@dp.message_handler(commands=['ref'])
async def change_referral_count(jam: types.Message):
    global required_referrals
    if jam.from_user.id == admin_id:
        try:
            # Получаем новое значение из сообщения
            new_value = int(jam.text.split()[1])  # Извлекаем значение после команды
            if new_value < 0:
                await jam.answer('❌ <b>Число рефералов не может быть отрицательным.</b>')
                return
            required_referrals = new_value
            await jam.answer(f'✅ <b>Количество рефералов для участия изменено на {required_referrals}.</b>')
        except (IndexError, ValueError):
            await jam.answer('❌ <b>Пожалуйста, укажите корректное число рефералов после команды.</b>')
    else:
        await jam.answer('❌ <b>У вас нет прав на выполнение этой команды.</b>')


async def get_channel_invite_link(channel_username: str) -> str:
    try:
        channel = await dp.bot.get_chat(channel_username)
        invite_link = await channel.export_chat_invite_link()
        return invite_link
    except Exception as e:
        print(f"Не удалось получить ссылку на приглашение для {channel_username}: {e}")
        return f"https://t.me/{channel_username}"


@dp.message_handler(commands=['start'], state='*')
async def process_start(jam: types.Message, state: FSMContext):
    await state.finish()

    # Check if the user has a username
    if not jam.from_user.username:
        await jam.answer("❌ <b>Извините, для использования бота необходимо иметь username в Telegram. "
                         "Пожалуйста, установите username в настройках Telegram и попробуйте снова.</b>")
        return

    if ' ' in jam.text:
        give_callback_value = jam.text.split(' ')[1]
        if 'referral=' in give_callback_value:
            # Обработка рефералов
            referrer_id = int(give_callback_value.split('=')[1])
            referred_user_id = jam.from_user.id

            try:
                await ReferralStatistic.add_referral(user_id=referrer_id, referred_user_id=referred_user_id)
                await dp.bot.send_message(referrer_id, f'🎉 У вас новый реферал: @{jam.from_user.username}!')
                await jam.answer("💎  <b>Вы были приглашены в бота!</b>")
            except ValueError as e:
                await jam.answer(f"❌ {e}")

        elif '=watchresult' in give_callback_value:
            # Подписка на результаты розыгрыша
            await TemporaryUsers().add_user(
                callback_value=give_callback_value,
                new_member_id=jam.from_user.id,
                new_member_username=jam.from_user.username
            )
            await jam.answer('💎  <b>Вы подписались на результаты розыгрыша, ожидайте!</b>')

        else:
            try:
                is_subscribed, unsubscribed_channels = await check_channels_subscriptions(
                    give_callback_value=give_callback_value,
                    user_id=jam.from_user.id
                )

                if is_subscribed:
                    # Пользователь подписан на все каналы
                    referral_count = await ReferralStatistic.get_referral_count(user_id=jam.from_user.id)
                    if referral_count < required_referrals:
                        # Создаем клавиатуру с кнопками
                        kb_unsubscribed = InlineKeyboardMarkup()

                        # Добавляем кнопку "Участвовать снова"
                        participate_again_link = f"https://t.me/MYWMESTE_bot?start={give_callback_value}"
                        bt_participate_again = InlineKeyboardButton("Участвовать снова", url=participate_again_link)
                        kb_unsubscribed.add(bt_participate_again)

                        # Добавляем кнопку "Пригласить друга"
                        referral_link = f"Присоединяйтесь и участвуйте в розыгрышах: https://t.me/MYWMESTE_bot?start=referral={jam.from_user.id}"
                        bt_invite_friend = InlineKeyboardButton(
                            'Пригласить друга',
                            switch_inline_query=referral_link
                        )
                        kb_unsubscribed.add(bt_invite_friend)

                        await jam.answer(
                            f'💎 Для участия в розыгрыше вам необходимо иметь минимум {required_referrals} рефералов.',
                            reply_markup=kb_unsubscribed
                        )
                        return

                    await manage_new_members_from_button_gives(
                        jam=jam,
                        state=state,
                        give_callback_value=give_callback_value
                    )
                else:
                    # Пользователь не подписан на некоторые каналы
                    kb_unsubscribed = InlineKeyboardMarkup()
                    for channel in unsubscribed_channels:
                        invite_link = channel.get('invite_link') or await get_channel_invite_link(
                            channel['channel_name'])
                        bt_channel = InlineKeyboardButton(channel['channel_name'], url=invite_link)
                        kb_unsubscribed.add(bt_channel)

                    # Добавляем кнопку "Участвовать снова"
                    participate_again_link = f"https://t.me/MYWMESTE_bot?start={give_callback_value}"
                    bt_participate_again = InlineKeyboardButton("Участвовать снова", url=participate_again_link)
                    kb_unsubscribed.add(bt_participate_again)
                    await jam.answer(
                        'Чтобы пользоваться ботом, подпишись на каналы наших замечательных спонсоров:\n\n',
                        reply_markup=kb_unsubscribed
                    )

            except Exception as e:
                print(f"Ошибка при проверке подписок: {e}")
                await jam.answer('💔 К сожалению, розыгрыш уже был завершен.')


    else:
        # Обработка, если команда start без параметров
        await state.finish()

        bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
        bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
        bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
        kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(
            bt_admin_started_gives)

        referral_link = f"Присоединяйтесь и участвуйте в розыгрышах: https://t.me/MYWMESTE_bot?start=referral={jam.from_user.id}"
        bt_invite_friend = InlineKeyboardButton(
            'Пригласить друга',
            switch_inline_query=referral_link
        )
        bt_my_referrals = InlineKeyboardButton('Список моих рефералов', callback_data='my_referrals')
        bt_faq = InlineKeyboardButton('Вопросы на ответы', callback_data='faq')  # Новая кнопка для FAQ

        # Создание клавиатуры с двумя кнопками в строке
        kb_user_menu = InlineKeyboardMarkup().add(bt_invite_friend, bt_my_referrals).add(bt_faq)

        if jam.from_user.id == admin_id:
            await jam.answer(start_text, reply_markup=kb_admin_menu)
        else:
            await jam.answer(
                '<b>Главное меню</b> 💎',
                reply_markup=kb_user_menu
            )


async def is_user_participating(self, giveaway_callback_value: str, user_id: int) -> bool:
    data = await self.filter(giveaway_callback_value=giveaway_callback_value).values('users')
    if data:
        return any(user['user_id'] == user_id for user in data[0]['users'])
    return False

async def add_winner_and_check_referrals(self, giveaway_id: str, winner_id: int) -> list:
    referrals = await ReferralStatistic.get_referrals(user_id=winner_id)
    additional_winners = []

    referred_user_ids = [ref['referred_user_id'] for ref in referrals]
    participating_users = await TemporaryUsers().filter(
        giveaway_callback_value=giveaway_id,
        users__contains=referred_user_ids
    ).values('users')

    for ref_user_id in referred_user_ids:
        if any(user['user_id'] == ref_user_id for user in participating_users[0]['users']):
            additional_winners.append(ref_user_id)
            await GiveAwayStatistic.add_winner(giveaway_id, ref_user_id)

    return additional_winners

async def get_winners(self, giveaway_callback_value: str) -> list:
    data = await self.filter(giveaway_callback_value=giveaway_callback_value).values('winners')
    return data[0]['winners'] if data else []


@dp.callback_query_handler(lambda c: c.data == 'my_referrals')
async def my_referrals(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    referrals = await ReferralStatistic.get_referrals(user_id)

    if referrals:
        referral_list = "\n".join([f"- ID: {ref['referred_user_id']}" for ref in referrals])
        text = f'Ваши рефералы:\n{referral_list}'
    else:
        text = 'У вас пока нет рефералов.'

    # Кнопка "Назад" для возврата в главное меню
    back_button = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    back_markup = InlineKeyboardMarkup().add(back_button)

    # Обновляем сообщение
    await callback_query.message.edit_text(text, reply_markup=back_markup)
    await callback_query.answer()  # Закрываем уведомление с индикацией нажатия

@dp.callback_query_handler(lambda c: c.data == 'back_to_menu')
async def back_to_menu(callback_query: types.CallbackQuery):
    # Создаем клавиатуру главного меню
    bt_admin_create_give = InlineKeyboardButton('Создать розыгрыш', callback_data='admin_gives')
    bt_admin_created_gives = InlineKeyboardButton('Созданные розыгрыши', callback_data='admin_created_gives')
    bt_admin_started_gives = InlineKeyboardButton('Активные розыгрыши', callback_data='admin_started_gives')
    kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)

    # Уникальная реферальная ссылка для пользователя
    referral_link = f"https://t.me/MYWMESTE_bot?start=referral={callback_query.from_user.id}"
    share_text = f"Присоединяйтесь и участвуйте в розыгрышах: {referral_link}"

    bt_invite_friend = InlineKeyboardButton('Пригласить друга', switch_inline_query=share_text)
    bt_my_referrals = InlineKeyboardButton('Список моих рефералов', callback_data='my_referrals')
    bt_faq = InlineKeyboardButton('Ответы на вопросы', callback_data='faq')  # Кнопка для FAQ

    # Создание клавиатуры с двумя кнопками в строке
    kb_user_menu = InlineKeyboardMarkup().add(bt_invite_friend, bt_my_referrals).add(bt_faq)

    # Обновляем сообщение
    if callback_query.from_user.id == admin_id:
        await callback_query.message.edit_text(start_text, reply_markup=kb_admin_menu)
    else:
        await callback_query.message.edit_text(
            '💎  <b>Добро пожаловать! Используйте кнопки ниже, чтобы пригласить друзей и узнать список своих рефералов.</b>',
            reply_markup=kb_user_menu
        )

# Обработчик для кнопки "Вопросы на ответы"
@dp.callback_query_handler(lambda c: c.data == 'faq')
async def faq_menu(callback_query: types.CallbackQuery):
    # Кнопки для подменю FAQ
    bt_how_it_works = InlineKeyboardButton('Как это работает', callback_data='how_it_works')
    bt_referral_system = InlineKeyboardButton('Система рефералов', callback_data='referral_system')
    bt_invite_friends = InlineKeyboardButton('Приглашение друзей', callback_data='invite_friends')  # Новая кнопка
    bt_contact_support = InlineKeyboardButton('Связаться с оператором', url='https://t.me/Statenkov')  # Новая кнопка
    bt_back = InlineKeyboardButton('Назад', callback_data='back_to_menu')

    # Создаем клавиатуру FAQ с новыми кнопками
    kb_faq = InlineKeyboardMarkup().add(bt_how_it_works, bt_referral_system).add(bt_invite_friends,
                                                                                 bt_contact_support).add(bt_back)

    await callback_query.message.edit_text('📖 <b>Выберите тему:</b>', reply_markup=kb_faq)
    await callback_query.answer()

# Обработчик для кнопки "Как это работает"
@dp.callback_query_handler(lambda c: c.data == 'how_it_works')
async def how_it_works(callback_query: types.CallbackQuery):
    text = faq_texts['how_it_works']
    back_button = InlineKeyboardButton('Назад', callback_data='faq')
    markup = InlineKeyboardMarkup().add(back_button)

    await callback_query.message.edit_text(text, reply_markup=markup)
    await callback_query.answer()

# Обработчик для кнопки "Система рефералов"
@dp.callback_query_handler(lambda c: c.data == 'referral_system')
async def referral_system(callback_query: types.CallbackQuery):
    text = faq_texts['referral_system']
    back_button = InlineKeyboardButton('Назад', callback_data='faq')
    markup = InlineKeyboardMarkup().add(back_button)

    await callback_query.message.edit_text(text, reply_markup=markup)
    await callback_query.answer()

# Обработчик для кнопки "Приглашение друзей"
@dp.callback_query_handler(lambda c: c.data == 'invite_friends')
async def invite_friends(callback_query: types.CallbackQuery):
    text = faq_texts['invitation_rules']
    back_button = InlineKeyboardButton('Назад', callback_data='faq')
    markup = InlineKeyboardMarkup().add(back_button)

    await callback_query.message.edit_text(text, reply_markup=markup)
    await callback_query.answer()
