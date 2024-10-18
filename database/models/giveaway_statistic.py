from datetime import datetime, timedelta
from typing import NamedTuple

from tortoise import Model, fields

from config import timezone_info


class GiveAwayStatisticInfo(NamedTuple):
    count_members_in_24_hours: int
    count_members_summary: int



class GiveAwayStatistic(Model):
    giveaway_callback_value = fields.TextField(pk=True)
    members = fields.JSONField(null=True)
    post_link = fields.TextField()
    winners = fields.JSONField(null=True)

    async def add_statistic(
            self,
            giveaway_callback_value: str,
            members: list,
            winners: list,
            post_link: str,
    ):
        existing = await self.filter(giveaway_callback_value=giveaway_callback_value).first()

        if existing:
            await self.filter(giveaway_callback_value=giveaway_callback_value).update(
                members=members,
                winners=winners,
                post_link=post_link
            )
        else:
            await self.create(
                giveaway_callback_value=giveaway_callback_value,
                members=members,
                winners=winners,
                post_link=post_link
            )

    async def delete_statistic(self, giveaway_callback_value: str):
        await self.filter(giveaway_callback_value=giveaway_callback_value).delete()



    async def exists_member(self, giveaway_callback_value: str, member_username: str) -> bool:
        old_data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')

        try:
            members = old_data[0]['members']

            for member in members:
                if member_username == member['username']:
                    return True

            else:
                return False

        except (KeyError, IndexError):
            return False

    async def get_data(self, giveaway_callback_value: str) -> dict:
        data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')

        return data

    async def get_statistic(self, giveaway_callback_value: str) -> GiveAwayStatisticInfo | bool:
        data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).values('members')

        if data:
            members = data[0]['members']
            now = datetime.now(timezone_info)
            count_members_in_24_hours = [
                member for member in members if
                datetime.strptime(member["join_date"], "%Y-%m-%d %H:%M:%S.%f%z") > now - timedelta(days=1)
            ]
            return GiveAwayStatisticInfo(
                count_members_in_24_hours=len(count_members_in_24_hours),
                count_members_summary=len(members)
            )
        else:
            return False

    async def update_statistic_members(
        self,
        giveaway_callback_value: str,
        new_member_username: str,
        new_member_id: int,
    ) -> bool:


        old_data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')

        members = old_data[0]['members']


        for member in members:
            if new_member_id == member['user_id']:
                return False


        else:
            members.append({
                'username': new_member_username,
                'user_id': new_member_id,
                'join_date': str(datetime.now(timezone_info))
            })

            await self.filter(
                giveaway_callback_value=giveaway_callback_value
            ).update(members=members)

            return True




