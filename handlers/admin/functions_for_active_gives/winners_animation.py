import asyncio
import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app import bot
from database import TemporaryUsers, GiveAwayStatistic
from .inform_of_the_end_give import delete_and_inform_of_the_end_give


async def create_markup_for_watch_results(give_callback_value: str) -> InlineKeyboardMarkup:
    bot_data = await bot.get_me()
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            text='Присоединиться »',
            url=f'https://t.me/{bot_data.username}?start={give_callback_value}=watchresult'
        )
    )

    return markup


async def create_markup_for_watch_winners(give_callback_value: str) -> InlineKeyboardMarkup:
    bot_data = await bot.get_me()
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            text='Результаты »',
            url=f'https://t.me/{bot_data.username}?start={give_callback_value}=getresults'
        )
    )

    return markup


async def run_winners_animation(
        give_callback_value: str,
        organizer_user_id: int,  # ID организатора должен быть целым числом
        members_from_giveaway: list,
        winners_count: int,
        winners_users: list = None
):
    if winners_users is None:
        winners_users = []

    summary_members_count = len(members_from_giveaway)

    if summary_members_count >= winners_count:
        markup = await create_markup_for_watch_results(give_callback_value)
        await asyncio.sleep(20)

        # Выбор победителей
        while len(winners_users) < winners_count:
            member_info = random.choice(members_from_giveaway)
            if not any(winner['user_id'] == member_info['user_id'] for winner in winners_users):
                winners_users.append({
                    'place': len(winners_users) + 1,
                    'user_id': member_info['user_id'],
                    'username': member_info['username']
                })
                members_from_giveaway.remove(member_info)

        # Уведомление участников о начале выбора победителей
        temporary_users_for_watch_results = await TemporaryUsers().get_all_users(callback_value=give_callback_value)

        if temporary_users_for_watch_results:
            users_to_send_messages = []
            for user in temporary_users_for_watch_results:
                message = await bot.send_message(
                    chat_id=user['user_id'],
                    text='💎 <b>Начинается выбор победителя</b>'
                )
                users_to_send_messages.append({
                    'user_id': user['user_id'],
                    'message_id': message.message_id
                })

            members_usernames = [member['username'] for member in members_from_giveaway]

            while len(members_usernames) > 1:
                text = ''
                try:
                    chunks = [members_usernames[i:i + 12] for i in range(0, len(members_usernames), 8)]
                    for chunk in chunks:
                        index = random.randint(0, len(chunk) - 1)
                        username = chunk[index]
                        chunk.pop(index)
                        members_usernames.remove(username)
                        users_formatted = [f'🎁 {user}  ' for user in chunk]
                        text += '\n'.join(users_formatted)
                        await asyncio.sleep(0.3)
                except ValueError:
                    continue

            text += "\n".join([f"{winner['place']} место - @{winner['username']}" for winner in winners_users])

        await GiveAwayStatistic().filter(giveaway_callback_value=give_callback_value).update(winners=winners_users)

    await delete_and_inform_of_the_end_give(
        give_callback_value=give_callback_value,
        winners=winners_users,
        summary_count_users=summary_members_count
    )
