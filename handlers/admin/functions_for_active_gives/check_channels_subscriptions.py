from database import GiveAway, TelegramChannel
from app import bot

async def check_channels_subscriptions(
        give_callback_value: str,
        user_id: int,
        owner_id: int = False
) -> (bool, list):
    if not owner_id:
        owner_id = await GiveAway().get_owner_by_callback_value(
            give_callback_value=give_callback_value
        )

    channels_data = await TelegramChannel().get_channel_data(
        owner_id=owner_id
    )

    unsubscribed_channels = []

    for channel in channels_data:
        channel_id = channel.get('channel_id')

        if not channel_id:
            print(f"Отсутствует channel_id для канала: {channel}")
            continue  # Пропускаем итерацию, если channel_id отсутствует

        try:
            # Получаем информацию о канале по channel_id
            channel_info = await bot.get_chat(chat_id=channel_id)
            channel_name = channel_info.title  # Получаем название канала

            user_channel_info = await bot.get_chat_member(
                chat_id=channel_id,
                user_id=user_id
            )

            if user_channel_info.status != 'member':
                try:
                    invite_link = await bot.export_chat_invite_link(chat_id=channel_id)
                    unsubscribed_channels.append({
                        'channel_name': channel_name,
                        'invite_link': invite_link
                    })
                except Exception as e:
                    print(f"Ошибка при получении ссылки на приглашение для {channel_name}: {e}")
                    unsubscribed_channels.append({
                        'channel_name': channel_name,
                        'invite_link': None
                    })
        except Exception as e:
            print(f"Ошибка при получении информации о канале {channel_id}: {e}")

    return (len(unsubscribed_channels) == 0, unsubscribed_channels)
