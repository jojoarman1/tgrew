from app import bot
from database import GiveAway, TemporaryUsers, ReferralStatistic

async def delete_and_inform_of_the_end_give(
        give_callback_value: str,
        winners: list,
        summary_count_users: int,
):
    # Получаем данные о розыгрыше
    give_data = await GiveAway().filter(callback_value=give_callback_value).all().values(
        'owner_id',
        'name',
        'winners_count'
    )

    for give in give_data:
        winners_required = give["winners_count"]

        # Проверяем, что участников меньше, чем требуется победителей
        if summary_count_users < winners_required:
            text = (
                '🎁  <b>Розыгрыш завершен</b>\n\n'
                f'<b>Название:</b> {give["name"]}\n'
                f'<b>Общее количество участников:</b> {summary_count_users}\n\n'
                '<b>Победителей Нет 🚫</b>\n'
                'Причина: недостаточное количество участников'
            )
            await bot.send_message(chat_id=give['owner_id'], text=text, parse_mode="HTML")
        else:
            # Если участников достаточно, отправляем сообщение с победителями
            text = f'🎁  <b>Розыгрыш завершен</b>\n\n<b>Название:</b> {give["name"]}\n<b>Общее количество участников:</b> {summary_count_users}\n\n<b>Победители:</b>\n\n'

            for i, user_info in enumerate(winners):
                text += f"{user_info['place']} место - @{user_info['username']}\n"

                # Проверяем, является ли победитель рефералом
                inviter_id = await ReferralStatistic.get_inviter(user_info['user_id'])

                if inviter_id:
                    # Получаем информацию о пригласителе
                    inviter_info = await bot.get_chat(inviter_id)
                    inviter_username = f"@{inviter_info.username}" if inviter_info.username else inviter_info.first_name
                    text += f"Пригласитель: {inviter_username}\n"
                else:
                    text += "Пригласитель: нет\n"

            await bot.send_message(chat_id=give['owner_id'], text=text, parse_mode="HTML")

    await GiveAway().delete_give(callback_value=give_callback_value)
    await TemporaryUsers().filter(giveaway_callback_value=give_callback_value).delete()
