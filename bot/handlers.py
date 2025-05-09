from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)

from bot.buttons import start_buttons
from bot.utils import parse_datetime, is_future_datetime
from bot.reminders import schedule_reminders
from core.database import delete_event, get_events, user_exists, add_event

ASK_NAME, ASK_DATETIME, ASK_EVENT_ID = range(3)
    


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await start_buttons(update, context)

    await update.message.reply_text(
        "Привет! Я бот-напоминалка 📅\n"
        "Напиши /create чтобы добавить событие\n"
        "Напиши /list чтобы посмотреть все события\n"
        "Напиши /delete чтобы удалить событие\n"
    )
    user_id = update.effective_chat.id
    db_conn = context.bot_data['db_conn']
    user_exists(db_conn, user_id) 

    return ConversationHandler.END



async def create_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите название события:")
    return ASK_NAME 



async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['event_name'] = update.message.text  
    await update.message.reply_text("Теперь введите дату и время в формате ГГГГ‑ММ‑ДД ЧЧ:ММ")
    return ASK_DATETIME 



async def ask_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date_str = update.message.text
    dt = parse_datetime(date_str)
    if not dt or not is_future_datetime(dt):
        await update.message.reply_text(
            "Неверный формат или дата в прошлом. Попробуйте ещё раз:"
        )
        return ASK_DATETIME

    event_name = context.user_data['event_name']
    user_id = update.effective_chat.id
    db_conn = context.bot_data['db_conn']
    add_event(db_conn, user_id, event_name, "", dt.isoformat())
    schedule_reminders(context.job_queue, user_id, event_name, dt)

    await update.message.reply_text(
        f"✅ Событие «{event_name}» запланировано на {dt.strftime('%d.%m.%Y %H:%M')}"
    )
    return ConversationHandler.END



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END



async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_chat.id
    db_conn = context.bot_data['db_conn']

    rows = get_events(db_conn, user_id)
    if not rows:
        await update.message.reply_text("У вас нет запланированных событий.")
        return ConversationHandler.END

    message = "Ваши запланированные события:\n"
    for id, title, event_dt_str in rows:
        event_dt = parse_datetime(event_dt_str)
        if event_dt is None:
            print(f"Ошибка парсинга даты: {event_dt_str}")
            return ConversationHandler.END
        message += f"-ID: {id} \t {title} в {event_dt.strftime('%Y.%m.%d %H:%M')}\n"

    await update.message.reply_text(message)

    return ConversationHandler.END



async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_chat.id
    db_conn = context.bot_data['db_conn']

    rows = get_events(db_conn, user_id)
    if not rows:
        await update.message.reply_text("У вас нет запланированных событий.")
        return ConversationHandler.END

    message = "Ваши запланированные события:\n"
    for id, title, event_dt_str in rows:
        event_dt = parse_datetime(event_dt_str)
        message += f"-ID: {id} \t {title} в {event_dt.strftime('%d.%m.%Y %H:%M')}\n"
    await update.message.reply_text(message)

    await update.message.reply_text("Выберите ID события для удаления:\n")
    return ASK_EVENT_ID



async def ask_event_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    db_conn = context.bot_data['db_conn']

    event_id = int(update.message.text)

    rows = delete_event(db_conn, event_id)
    if rows>0:
        await update.message.reply_text(f"Событие с ID {event_id} удалено.")
    else:
        await update.message.reply_text(f"Событие с ID {event_id} не найдено. Попробуйте ещё раз.")
        return ASK_EVENT_ID
    return ConversationHandler.END



def register_handlers(application):
    create_conv = ConversationHandler(
        entry_points=[CommandHandler("create", create_event)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_datetime)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    delete_conv = ConversationHandler(
        entry_points=[CommandHandler("delete", delete)],
        states={
            ASK_EVENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_event_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    application.add_handler(delete_conv, group = 0)
    application.add_handler(create_conv, group = 0)

    application.add_handler(CommandHandler("start", start), group = 1)
    application.add_handler(CommandHandler("list", list), group = 1)

    
    
