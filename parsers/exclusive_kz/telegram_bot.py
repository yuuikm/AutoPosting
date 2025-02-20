import logging
import re
from aiogram import Bot
from aiogram.types import FSInputFile
from shared.config import EXCLUSIVE_TELEGRAM_BOT_TOKEN, EXCLUSIVE_TELEGRAM_CHANNEL_ID

async def send_to_telegram(image_path, post_url, article_content):
    caption_limit = 1024
    text_limit = 950
    kazakhstan_keywords = ["Казахстан", "Алматы", "Астана", "РК"]

    flag_emoji = "🇰🇿" if any(word in article_content for word in kazakhstan_keywords) else "📰"

    article_content = re.sub(r"Фото:\s*.*", "", article_content)

    paragraphs = [p.strip() for p in article_content.split("\n") if p.strip()]

    formatted_text = "\n\n".join(paragraphs)

    caption = f"{flag_emoji} {formatted_text}\n\n[🔗 Читать на Exclusive.kz]({post_url})"

    if len(caption) > caption_limit:
        truncated_text = formatted_text[:text_limit]
        truncated_text = re.sub(r"[^.!?]*$", "", truncated_text)
        caption = f"{flag_emoji} {truncated_text}\n\n[🔗 Читать на Exclusive.kz]({post_url})"

    async with Bot(token=EXCLUSIVE_TELEGRAM_BOT_TOKEN) as bot:
        try:
            image = FSInputFile(image_path)
            await bot.send_photo(chat_id=EXCLUSIVE_TELEGRAM_CHANNEL_ID, photo=image, caption=caption, parse_mode="Markdown")
            logging.info("✅ Успешно отправлено в Telegram")
        except Exception as e:
            logging.error(f"❌ Ошибка отправки в Telegram: {e}")
