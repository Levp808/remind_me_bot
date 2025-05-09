from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
)

async def start_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [ KeyboardButton("/create"), KeyboardButton("/list") ],
        [ KeyboardButton("/delete"), KeyboardButton("/cancel") ],
    ]
    
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=markup
    )
    