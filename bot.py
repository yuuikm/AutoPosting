import logging
import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import scraper
from shared.config import TELEGRAM_BOT_TOKEN, USER_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_summary(stats):
    if stats["total"] == 0:
        return "📭 Новых статей не найдено."

    lines = [
        f"📊 Скрапер завершил работу.\n",
        f"📰 Всего статей: {stats['total']}\n",
        f"✅ Telegram: {stats['telegram']}/{stats['total']}"
        + (f" (❌ {stats['telegram_fail']} не опубликовано)" if stats['telegram_fail'] else ""),
        f"✅ Instagram: {stats['instagram']}/{stats['total']}"
        + (f" (❌ {stats['instagram_fail']} не опубликовано)" if stats['instagram_fail'] else ""),
        f"✅ Facebook: {stats['facebook']}/{stats['total']}"
        + (f" (❌ {stats['facebook_fail']} не опубликовано)" if stats['facebook_fail'] else ""),
    ]
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Standard.kz бот активен. Напиши /run для запуска.")


async def run_scraper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        return

    await update.message.reply_text("🚀 Запуск скрапера Standard.kz")

    try:
        stats = await asyncio.to_thread(scraper.scrape_posts)
        await update.message.reply_text(format_summary(stats))
    except Exception as e:
        logger.error("Scraper failed: %s", e, exc_info=True)
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
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_scraper))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()
