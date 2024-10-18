import random

from typing import Dict
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import MessageNotModified

from database import GiveAwayStatistic


class Captcha:
    captcha_id = 0
    passed_captcha_users = []

    def __init__(self, choices: Dict[str, str] = None) -> None:
        if choices and isinstance(choices, dict):
            self.choices = choices
        else:
            self.choices = {
                "яблоко": "🍎",
                "машину": "🚗",
                "собаку": "🐶",
                "дерево": "🌳",
                "радугу": "🌈",
                "банан": "🍌",
                "телефон": "📱",
                "солнце": "☀️",
                "конфету": "🍬",
                "мяч": "⚽️",
                "часы": "⌚️",
                "стул": "🪑",
                "календар": "📆",
                "замок": "🔒",
                "клубнику": "🍓"
            }
        self.correct_choice = random.choice(list(self.choices.keys()))

        Captcha.captcha_id += 1
        self.captcha_id = Captcha.captcha_id
        self.callback_name = f"_Captcha{self.captcha_id}"

        self.captcha_passed = False

    def get_captcha_keyboard(self) -> InlineKeyboardMarkup:
        captcha_keyboard = InlineKeyboardMarkup()

        for choice in random.sample(list(self.choices.keys()), len(self.choices)):
            captcha_keyboard.insert(
                InlineKeyboardButton(
                    self.choices[choice],
                    callback_data=f"{self.callback_name}_choice_"
                    + ("1" if choice == self.correct_choice else "0")
                )
            )

        return captcha_keyboard

    def get_caption(self) -> str:
        return f"<b>Нажми на {self.correct_choice}</b>"

    async def captcha_choice_handler(
        self,
        callback_query: types.CallbackQuery,
        state: FSMContext
    ) -> None:
        if callback_query.data.split("_")[-1] == "0":
            self.correct_choice = random.choice(list(self.choices.keys()))
            try:
                await callback_query.message.edit_text(
                    f"<b>Выбор неверный\n\nНажми на {self.correct_choice}</b>",
                    reply_markup=self.get_captcha_keyboard(),
                )
            except MessageNotModified:
                ...
            return

        self.captcha_passed = True
        Captcha.passed_captcha_users.append(callback_query.from_user.id)

        await callback_query.message.delete()
        await callback_query.message.answer(
          "Ты - супергерой! 💪🏻\n"
          "Ты только что стал частью “МЫ С ТОБОЙ”! 🔥\n"
          "Спасибо за доверие! 🎉 Теперь ты участвуешь в розыгрыше невероятного приза!\n\n"
          "Чем больше друзей ты пригласишь, тем больше шансов на супер-благодарность от нас! 🤝🏻\n\n"
          "Всю информацию о розыгрышах и том, как мы помогаем людям ты найдешь здесь: [ссылка на канал]\n\n"
          "Объединившись, мы творим чудеса 💫 каждый день мы даем шанс на полноценную жизнь нуждающимся, а вы можете стать богаче и счастливее!\n\n"
          "Чем больше людей участвует, тем больше приз! 🥳 1 000 000 ежедневных пользователей бота - и мы разыграем 1 000 000 рублей! 💰"
        )


        state_data = await state.get_data()
        give_callback_value = state_data.get('give_callback_value')

        await GiveAwayStatistic().update_statistic_members(
            giveaway_callback_value=give_callback_value,
            new_member_username=callback_query.from_user.username,
            new_member_id=callback_query.from_user.id
        )


    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(
            self.captcha_choice_handler,
            lambda c: c.data.startswith(f"{self.callback_name}_choice_"),
        )
