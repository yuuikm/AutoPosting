import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
import re

async def send_to_telegram(image_path, title, post_url, text_content):
    caption_limit = 1024
    text_limit = 995

    paragraphs = text_content.split("\n")
    kazakhstan_keywords = ["Казахстан", "Алматы", "Астана", "РК"]
    flag_emoji = "🇰🇿" if any(word in text_content for word in kazakhstan_keywords) else "📰"

    if paragraphs:
        paragraphs[0] = f"**{paragraphs[0]}**"
    text_content = "\n\n".join(paragraphs)

    caption = f"{flag_emoji} {text_content}\n\n🔗 [Читать на standard.kz]({post_url})"

    if len(caption) > caption_limit:
        truncated_text = text_content[:text_limit]
        truncated_text = re.sub(r"[^.!?]*$", "", truncated_text)
        caption = f"{flag_emoji} {truncated_text}\n\n🔗 [Читать на standard.kz]({post_url})"

    async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
        with open(image_path, "rb") as image:
            await bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=image, caption=caption, parse_mode="Markdown")
