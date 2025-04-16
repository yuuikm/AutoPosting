import re
import json
import requests
from telegram import Bot, error
from shared.config import STANDARD_TELEGRAM_BOT_TOKEN, STANDARD_TELEGRAM_CHANNEL_ID
from shared.constants import EMOJI_PATH

CAPTION_LIMIT = 1024
TEXT_LIMIT = CAPTION_LIMIT - 50

def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def clean_text(text):
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(https?:\/\/[^\s]+?\)", "", text)
    return re.sub(r"\s+", " ", text).strip()

def format_text_with_tabs(text):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return "\n\n".join(paragraphs)

async def send_to_telegram(image_path, title, post_url, text_content, send_message_callback=None):
    try:
        with open(EMOJI_PATH, "r", encoding="utf-8") as f:
            emoji_rules = json.load(f)

        matched_emojis = [
            emoji for emoji, keywords in emoji_rules.items()
            if any(re.search(rf"\b{re.escape(word)}\b", text_content, re.IGNORECASE) for word in keywords)
        ][:2]

        selected_emoji = " ".join(matched_emojis or ["📰"])
        safe_title = escape_html(title)
        safe_post_url = escape_html(post_url)
        safe_text_content = escape_html(clean_text(text_content))
        formatted_text = format_text_with_tabs(safe_text_content)

        caption = f"{selected_emoji} {formatted_text}\n\n<a href='{safe_post_url}'>🔗 Читать на Standard.kz</a>"

        if len(caption) > CAPTION_LIMIT:
            truncated = formatted_text[:TEXT_LIMIT]
            truncated = re.sub(r"[^.!?]*$", "", truncated)
            caption = f"{selected_emoji} {truncated}\n\n<a href='{safe_post_url}'>🔗 Читать на Standard.kz</a>"

        async with Bot(token=STANDARD_TELEGRAM_BOT_TOKEN) as bot:
            with open(image_path, "rb") as image:
                message = await bot.send_photo(
                    chat_id=STANDARD_TELEGRAM_CHANNEL_ID,
                    photo=image,
                    caption=caption,
                    parse_mode="HTML"
                )

        if send_message_callback:
            await send_message_callback(f"Отправлено в Telegram: {safe_title}")

        return message.photo[-1].file_id

    except (error.BadRequest, error.TelegramError, Exception) as e:
        if send_message_callback:
            await send_message_callback(f"Telegram ошибка: {e}")
        return None

def get_telegram_file_url(file_id):
    url = f"https://api.telegram.org/bot{STANDARD_TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    response = requests.get(url)
    if response.status_code == 200:
        path = response.json()['result']['file_path']
        return f"https://api.telegram.org/file/bot{STANDARD_TELEGRAM_BOT_TOKEN}/{path}"
    return None
