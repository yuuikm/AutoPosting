import logging
import sys
import os
import asyncio
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from parsers.standard_kz import scraper as standard_scraper
from shared.config import STANDARD_TELEGRAM_BOT_TOKEN, USER_ID

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Standard.kz бот активен. Напиши /run для запуска.")

async def run_scraper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        return

    await update.message.reply_text("🚀 Запуск скрапера Standard.kz")

    try:
        await asyncio.to_thread(standard_scraper.scrape_posts)
        await update.message.reply_text("Скрапер для Standard.kz завершил работу. Публикации отправлены в Telegram, Instagram и Facebook.")
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        return
    await update.message.reply_text("🚀 Бот работает и готов к выполнению команд.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Доступные команды:*\n"
        "/start \\- Запустить бота\n"
        "/run \\- Запустить скрапер\n"
        "/status \\- Проверка статуса бота\n"
        "/help \\- Справка\n\n"
        "👉 [Подробнее о работе бота на GitHub](https://github.com/yuuikm/AutoPosting)",
        parse_mode="MarkdownV2"
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(STANDARD_TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_scraper))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()
