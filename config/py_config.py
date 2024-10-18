import pytz
from tortoise import Tortoise

OWNERS = []
bot_token = '7866636026:AAH10oVR5P4zBCMx3GgbJRKNWuPt8Pgy6pE'
database_url = 'sqlite://db.sqlite3'  # Используем SQLite, файл будет называться db.sqlite3
timezone_info = pytz.timezone('Europe/Moscow')

text_for_participation_in_comments_giveaways = 'Участвую'

async def initialize_database():
    await Tortoise.init(
        db_url=database_url,
        modules={"models": ["your_app.models"]}  # Замените `your_app.models` на путь к вашим моделям
    )
    await Tortoise.generate_schemas()
