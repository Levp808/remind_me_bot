from telegram.ext import ApplicationBuilder
from config.config import Config
from core.database import get_db
from bot.handlers import register_handlers
from bot.reminders import restore_reminders
from bot.buttons import start_buttons

async def on_startup(application):
    db = application.bot_data["db_conn"]
    await restore_reminders(db, application.job_queue)

def main():
    cfg = Config()
    db = get_db(cfg.DB_PATH)

    application = (
        ApplicationBuilder()
        .token(cfg.BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )
    application.bot_data["db_conn"] = db

    register_handlers(application)

    print("Бот запущен…")
    application.run_polling()

if __name__ == "__main__":
    main()
