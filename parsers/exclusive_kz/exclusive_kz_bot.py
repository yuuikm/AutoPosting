import logging
import sys
import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from parsers.exclusive_kz import scraper as exclusive_scraper
from shared.config import EXCLUSIVE_TELEGRAM_BOT_TOKEN, USER_ID

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

main_menu = [["/run", "/status"], ["/help"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    await update.message.reply_text(
        "🚀 Exclusive.kz Бот запущен! Выбери команду из меню:",
        reply_markup=reply_markup
    )

async def run_scraper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        await update.message.reply_text("⛔ У тебя нет прав для запуска скрапера.")
        return

    await update.message.reply_text("🔍 Запускаем скрапер для Exclusive.kz...")
    try:
        await asyncio.to_thread(exclusive_scraper.scrape_page)
        await update.message.reply_text("✅ Скрапер для Exclusive.kz завершил работу. Публикации отправлены в Telegram, Instagram и Facebook.")
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        await update.message.reply_text("⛔ У тебя нет прав для проверки статуса.")
        return

    await update.message.reply_text("💡 Бот работает и готов к выполнению команд.")

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
    app = ApplicationBuilder().token(EXCLUSIVE_TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_scraper))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))

    print("🚀 Exclusive.kz Telegram бот запущен!")
    app.run_polling()
