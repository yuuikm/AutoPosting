import logging
from aiogram import Bot
from aiogram.types import FSInputFile
from shared.config import EXCLUSIVE_TELEGRAM_BOT_TOKEN, EXCLUSIVE_TELEGRAM_CHANNEL_ID

async def send_to_telegram(image_path, post_url, article_content):
    caption = f"{article_content[:950]}...\n\n[🔗 Читать на Exclusive.kz]({post_url})"

    async with Bot(token=EXCLUSIVE_TELEGRAM_BOT_TOKEN) as bot:
        try:
            image = FSInputFile(image_path)
            await bot.send_photo(chat_id=EXCLUSIVE_TELEGRAM_CHANNEL_ID, photo=image, caption=caption, parse_mode="Markdown")
            logging.info("✅ Успешно отправлено в Telegram")
        except Exception as e:
            logging.error(f"❌ Ошибка отправки в Telegram: {e}")
