from datetime import datetime, timedelta
from telegram.ext import CallbackContext

# Напоминание: просто отправить сообщение
async def send_reminder(context: CallbackContext) -> None:
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=f"⏰ Напоминание: {job.data}")

# Создание двух напоминаний (за 24 часа и за 1 час до события)
def schedule_reminders(job_queue, chat_id: int, event_name: str, event_time: datetime) -> None:
    now = datetime.now()
    
    # Время напоминаний
    reminders = [
        (event_time - timedelta(hours=24), "через 24 часа"),
        (event_time - timedelta(hours=1), "через 1 час")
    ]

    for remind_time, label in reminders:
        if remind_time > now:
            job_queue.run_once(
                send_reminder,
                when=(remind_time - now),
                chat_id=chat_id,
                data="Событие \"%s\" начинается %s!" % (event_name, label)
            )

async def restore_reminders(db_conn ,job_queue):
    cursor = db_conn.cursor()

    # Получаем все события из БД
    cursor.execute("SELECT chat_id, title, event_dt FROM events", ())
    rows = cursor.fetchall()

    for chat_id, title, event_dt_str in rows:
        event_dt = datetime.fromisoformat(event_dt_str)

        # Повторно планируем напоминания
        schedule_reminders(job_queue, chat_id, title, event_dt)
    print("All data is restored")