import logging
import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from parsers.exclusive_kz import scraper as exclusive_scraper
from shared.config import EXCLUSIVE_TELEGRAM_BOT_TOKEN, USER_ID

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Exclusive.kz Бот запущен! Напиши /run для старта скрапера.")

async def run_scraper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        await update.message.reply_text("⛔ У тебя нет прав для запуска скрапера.")
        return

    await update.message.reply_text("🔍 Запускаем скрапер для Exclusive.kz...")

    try:
        await asyncio.to_thread(exclusive_scraper.scrape_page)
        await update.message.reply_text("✅ Скрапер для Exclusive.kz завершил работу.")
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(EXCLUSIVE_TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_scraper))

    print("🚀 Exclusive.kz Telegram бот запущен!")
    app.run_polling()
