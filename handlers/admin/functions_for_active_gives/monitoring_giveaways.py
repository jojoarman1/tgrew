import asyncio
import datetime as datetime_

from datetime import datetime
from config import timezone_info
from app import dp
from database import GiveAway

from .giveaway_end_notification import send_giveaway_end_notification
from .process_end_giveaway import process_end_of_giveaway


async def manage_active_giveaways():
    while True:
        giveaways = await GiveAway().filter(run_status=True).all().values(
            'type', 'over_date', 'callback_value', 'captcha', 'owner_id'
        )

        if giveaways:
            current_time = datetime.now(tz=timezone_info)
            for giveaway in giveaways:
                if giveaway['type'] == 'button' and giveaway['captcha']:
                    hours_to_end = 3
                    time_diff = giveaway["over_date"] - current_time
                    if time_diff == datetime_.timedelta(hours=hours_to_end):
                        await send_giveaway_end_notification(
                            give_callback_value=giveaway['callback_value']
                        )

                if current_time >= giveaway["over_date"]:
                    await process_end_of_giveaway(
                        give_callback_value=giveaway['callback_value'],
                        owner_id=giveaway['owner_id']
                    )

        await asyncio.sleep(30)
