import logging
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from parsers.standard_kz import scraper as standard_scraper
from shared.config import STANDARD_TELEGRAM_BOT_TOKEN, USER_ID

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Standard.kz Бот запущен! Напиши /run для старта скрапера.")

async def run_scraper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        await update.message.reply_text("⛔ У тебя нет прав для запуска скрапера.")
        return

    await update.message.reply_text("🔍 Запускаем скрапер для Standard.kz...")

    try:
        loop = asyncio.get_event_loop()

        if asyncio.iscoroutinefunction(standard_scraper.scrape_posts):
            await standard_scraper.scrape_posts()
        else:
            await loop.run_in_executor(None, standard_scraper.scrape_posts)

        await update.message.reply_text("✅ Скрапер для Standard.kz завершил работу.")
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(STANDARD_TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_scraper))

    print("🚀 Standard.kz Telegram бот запущен!")
    app.run_polling()
