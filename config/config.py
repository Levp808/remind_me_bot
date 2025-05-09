import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Загружаем переменные окружения из файла .env
        load_dotenv()

        # Токен Telegram-бота
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        print(f"BOT_TOKEN successfully loaded")
        if not self.BOT_TOKEN:
            raise RuntimeError("Не задана переменная BOT_TOKEN в .env")

        # Путь к файлу базы данных (SQLite)
        self.DB_PATH = os.getenv("DB_PATH", "bot.db")
        print(f"DB_PATH successfully loaded")

