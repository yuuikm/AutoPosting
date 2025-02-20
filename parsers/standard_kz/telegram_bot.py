import asyncio
import re
from telegram import Bot
from shared.config import STANDARD_TELEGRAM_BOT_TOKEN, STANDARD_TELEGRAM_CHANNEL_ID

async def send_to_telegram(image_path, title, post_url, text_content):
    CAPTION_LIMIT = 1024
    TEXT_LIMIT = 995
    KAZAKHSTAN_KEYWORDS = ["Казахстан", "Алматы", "Астана", "РК"]

    flag_emoji = "🇰🇿" if any(word in text_content for word in KAZAKHSTAN_KEYWORDS) else "📰"

    paragraphs = [p.strip() for p in text_content.split("\n") if p.strip()]

    if paragraphs:
        paragraphs[0] = f"**{paragraphs[0]}**"

    formatted_text = "\n\n".join(paragraphs)

    caption = f"{flag_emoji} {formatted_text}\n\n[🔗 Читать на Standard.kz]({post_url})"

    if len(caption) > CAPTION_LIMIT:
        truncated_text = formatted_text[:TEXT_LIMIT]
        truncated_text = re.sub(r"[^.!?]*$", "", truncated_text)
        caption = f"{flag_emoji} {truncated_text}\n\n[🔗 Читать на Standard.kz]({post_url})"

    async with Bot(token=STANDARD_TELEGRAM_BOT_TOKEN) as bot:
        with open(image_path, "rb") as image:
            await bot.send_photo(
                chat_id=STANDARD_TELEGRAM_CHANNEL_ID,
                photo=image,
                caption=caption,
                parse_mode="Markdown"
            )

    print(f"✅ Публикация отправлена: {title}")
