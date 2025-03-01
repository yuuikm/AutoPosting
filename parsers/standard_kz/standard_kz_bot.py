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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

main_menu = [["/run", "/status"], ["/help"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Standard.kz Бот запущен! Напиши /run для старта скрапера.")

async def run_scraper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        await update.message.reply_text("⛔ У тебя нет прав для запуска скрапера.")
        return

    await update.message.reply_text("🔍 Запускаем скрапер для Standard.kz...")

    try:
        posts = await asyncio.to_thread(standard_scraper.scrape_posts)

        if not posts:
            await update.message.reply_text("❌ Нет новых постов для публикации.")
            return

        for index, post in enumerate(posts):
            title = post["title"]
            await update.message.reply_text(f"📤 Отправка в Telegram: {title}")

            file_id = await standard_scraper.send_to_telegram(
                post["image_path"], title, post["post_url"], post["text_content"],
                send_message_callback=lambda message: context.bot.send_message(
                    chat_id=update.effective_chat.id, text=message
                )
            )

            if not file_id:
                await update.message.reply_text(f"❌ Ошибка отправки {title} в Telegram! Пропускаем Instagram и Facebook.")
                continue

            await update.message.reply_text(f"✅ Telegram отправлен: {title}")

            public_image_url = standard_scraper.get_telegram_file_url(file_id)

            if not public_image_url:
                await update.message.reply_text(f"❌ Ошибка: не удалось получить URL изображения из Telegram для {title}.")
                continue

            await update.message.reply_text(f"📷 Публикация в Instagram: {title}")
            try:
                standard_scraper.publish_to_instagram_standard(public_image_url, post["post_url"], post["text_content"])
                await update.message.reply_text(f"✅ Instagram опубликован: {title}")
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка Instagram: {e}")

            await update.message.reply_text(f"📘 Публикация в Facebook: {title}")
            try:
                standard_scraper.publish_to_facebook_standard(public_image_url, post["post_url"], post["text_content"])
                await update.message.reply_text(f"✅ Facebook опубликован: {title}")
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка Facebook: {e}")

            if index < len(posts) - 1:
                delay = random.randint(250, 600)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"⏳ Ожидание {delay} секунд перед следующим постом..."
                )
                await asyncio.sleep(delay)

        await update.message.reply_text("✅ Скрапер для Standard.kz завершил работу. Публикации отправлены в Telegram, Instagram и Facebook..")
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
    app = ApplicationBuilder().token(STANDARD_TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_scraper))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))

    print("🚀 Standard.kz Telegram бот запущен!")
    app.run_polling()
