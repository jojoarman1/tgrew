from tortoise import Model, fields

class TemporaryUsers(Model):
    giveaway_callback_value = fields.TextField(pk=True)
    users = fields.JSONField(null=True)

    async def add_user(
        self,
        callback_value: str,
        new_member_id: str,
        new_member_username: str
    ):
        # Получаем старую запись по callback_value
        existing_record = await self.filter(giveaway_callback_value=callback_value).first()

        members = []
        if existing_record:
            members = existing_record.users or []  # Если users пустой, присваиваем пустой список

            # Проверяем, существует ли уже пользователь
            if any(member['user_id'] == new_member_id for member in members):
                print(f"Пользователь {new_member_id} уже существует в розыгрыше.")
                return False

            # Добавляем нового пользователя
            members.append({
                'user_id': new_member_id,
                'username': new_member_username,
            })
            print(f"Добавлен новый пользователь: {new_member_username} с ID {new_member_id}.")

            # Обновляем запись
            existing_record.users = members
            await existing_record.save()
            print(f"Обновлена запись для {callback_value}.")
        else:
            # Создаем новую запись, если ее не существует
            members.append({
                'user_id': new_member_id,
                'username': new_member_username,
            })
            await self.create(
                giveaway_callback_value=callback_value,
                users=members
            )
            print(f"Создана новая запись для {callback_value} с пользователем {new_member_username}.")

        return True

    async def get_all_users(self, callback_value: str) -> list:
        data = await self.filter(giveaway_callback_value=callback_value).all().values('users')

        # Отладочный вывод данных
        print(f"Данные для {callback_value}: {data}")

        try:
            return data[0]['users'] if data else []
        except (KeyError, IndexError):
            print(f"Ошибка при извлечении данных для {callback_value}.")
            return []
