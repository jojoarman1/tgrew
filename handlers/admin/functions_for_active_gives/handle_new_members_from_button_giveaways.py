from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app import dp, bot
from database import GiveAway, GiveAwayStatistic
from utils import Captcha

captcha = Captcha()

async def manage_new_members_from_button_gives(
    jam: types.Message,
    give_callback_value: str,
    state: FSMContext
):

    if not await GiveAwayStatistic().exists_member(
        giveaway_callback_value=give_callback_value,
        member_username=jam.from_user.username
    ):

        give_data = await GiveAway().filter(callback_value=give_callback_value).all().values(
            'over_date',
            'captcha'
        )

        for give in give_data:

            if give['captcha']:
                await state.update_data(give_callback_value=give_callback_value)

                captcha.register_handlers(dp)
                await bot.send_message(
                    jam.from_user.id,
                    captcha.get_caption(),
                    reply_markup=captcha.get_captcha_keyboard()
                )

            else:
                # Создание кнопки "Главное меню"
                keyboard = InlineKeyboardMarkup()
                menu_button = InlineKeyboardButton("Главное меню", callback_data="/start")
                keyboard.add(menu_button)

                await jam.answer(
                    "Ты - супергерой! 💪🏻\n"
                    "Ты только что стал частью “МЫ С ТОБОЙ”! 🔥\n"
                    "Спасибо за доверие! 🎉 Теперь ты участвуешь в розыгрыше невероятного приза!\n\n"
                    "Чем больше друзей ты пригласишь, тем больше шансов на супер-благодарность от нас! 🤝🏻\n\n"
                    "Всю информацию о розыгрышах и том, как мы помогаем людям ты найдешь здесь: [ссылка на канал]\n\n"
                    "Объединившись, мы творим чудеса 💫 каждый день мы даем шанс на полноценную жизнь нуждающимся, а вы можете стать богаче и счастливее!\n\n"
                    "Чем больше людей участвует, тем больше приз! 🥳 1 000 000 ежедневных пользователей бота - и мы разыграем 1 000 000 рублей! 💰",
                    reply_markup=keyboard  # Отправка клавиатуры с кнопкой
                )

                await GiveAwayStatistic().update_statistic_members(
                    giveaway_callback_value=give_callback_value,
                    new_member_username=jam.from_user.username,
                    new_member_id=jam.from_user.id
                )

    else:
        await jam.answer(
            '<b>Вы уже участвуете! Ожидайте итогов!</b>'
        )
