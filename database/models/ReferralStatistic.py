from tortoise import fields, models
from tortoise.exceptions import IntegrityError

class ReferralStatistic(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()  # ID пользователя, который пригласил рефералов
    referred_user_id = fields.IntField()  # ID реферала

    class Meta:
        table = "referral_statistics"
        unique_together = ("user_id", "referred_user_id")  # Одинаковые рефералы не будут засчитываться дважды

    @classmethod
    async def get_referral_count(cls, user_id: int) -> int:
        # Получает количество рефералов для указанного пользователя
        count = await cls.filter(user_id=user_id).count()
        return count

    @classmethod
    async def add_referral(cls, user_id: int, referred_user_id: int):
        # Проверка на самоинвайт
        if user_id == referred_user_id:
            raise ValueError("Пользователь не может пригласить самого себя.")

        # Проверка на обратный инвайт (реферал не может пригласить пригласившего его пользователя)
        if await cls.filter(user_id=referred_user_id, referred_user_id=user_id).exists():
            raise ValueError("Реферал не может пригласить пользователя, который пригласил его.")

        # Проверка на существование пользователя в качестве нереферала
        if await cls.filter(referred_user_id=user_id).exists():
            raise ValueError("Пользователя, уже вошедшего в бота, нельзя пригласить заново.")

        # Проверка на то, что реферал уже не приглашен другим пользователем
        if await cls.filter(referred_user_id=referred_user_id).exists():
            raise ValueError("Вы уже были приглашены другим пользователем.")

        # Проверка на наличие рефералов у пользователя
        if await cls.filter(user_id=referred_user_id).exists():
            raise ValueError("Пользователь уже имеет рефералов и не может быть приглашен снова.")

        # Добавляет реферала, если все проверки пройдены
        try:
            await cls.get_or_create(user_id=user_id, referred_user_id=referred_user_id)
        except IntegrityError:
            # Реферал уже существует
            pass

    @classmethod
    async def get_referrals(cls, user_id: int):
        # Получает список рефералов для указанного пользователя
        referrals = await cls.filter(user_id=user_id).values("referred_user_id")
        return referrals

    @classmethod
    async def get_inviter(cls, referred_user_id: int):
        # Получает ID пользователя, который пригласил указанного реферала
        inviter = await cls.filter(referred_user_id=referred_user_id).first()
        if inviter:
            return inviter.user_id
        return None
