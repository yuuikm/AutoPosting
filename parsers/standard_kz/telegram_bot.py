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

        matched_emojis = []
        for emoji, keywords in emoji_rules.items():
            if any(re.search(rf"\b{re.escape(word)}\b", text_content, re.IGNORECASE) for word in keywords):
                matched_emojis.append(emoji)
                if len(matched_emojis) == 2:
                    break

        if not matched_emojis:
            matched_emojis = ["📰"]

        selected_emoji = " ".join(matched_emojis)

        safe_title = escape_html(title)
        safe_post_url = escape_html(post_url)

        cleaned_text = clean_text(text_content)
        safe_text_content = escape_html(cleaned_text)
        
        formatted_text = format_text_with_tabs(safe_text_content)

        caption = f"{selected_emoji} {formatted_text}\n\n <a href='{safe_post_url}'>🔗 Читать на Standard.kz</a>"

        if len(caption) > CAPTION_LIMIT:
            truncated_text = formatted_text[:TEXT_LIMIT]
            truncated_text = re.sub(r"[^.!?]*$", "", truncated_text)
            caption = f"{selected_emoji} {truncated_text}\n\n <a href='{safe_post_url}'>🔗 Читать на Standard.kz</a>"

        async with Bot(token=STANDARD_TELEGRAM_BOT_TOKEN) as bot:
            with open(image_path, "rb") as image:
                message = await bot.send_photo(
                    chat_id=STANDARD_TELEGRAM_CHANNEL_ID,
                    photo=image,
                    caption=caption,
                    parse_mode="HTML"
                )

        file_id = message.photo[-1].file_id
        print(f"✅ Публикация отправлена в Telegram! file_id: {file_id}")

        if send_message_callback:
            await send_message_callback(f"✅ Отправлено в Telegram: {safe_title}")

        return file_id

    except error.BadRequest as e:
        print(f"❌ Ошибка Telegram (BadRequest): {e}")
        if send_message_callback:
            await send_message_callback(f"❌ Ошибка Telegram: {e}")
    except error.TelegramError as e:
        print(f"❌ Ошибка Telegram API: {e}")
        if send_message_callback:
            await send_message_callback(f"❌ Ошибка Telegram API: {e}")
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        if send_message_callback:
            await send_message_callback(f"❌ Ошибка отправки в Telegram: {e}")

    return None

def get_telegram_file_url(file_id):
    file_info_url = f"https://api.telegram.org/bot{STANDARD_TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"

    print(f"🔍 Запрос к Telegram API для получения пути файла: {file_info_url}")

    response = requests.get(file_info_url)

    if response.status_code == 200:
        file_path = response.json()['result']['file_path']
        file_url = f"https://api.telegram.org/file/bot{STANDARD_TELEGRAM_BOT_TOKEN}/{file_path}"
        print(f"✅ Telegram URL получен: {file_url}")
        return file_url

    print(f"❌ Ошибка получения файла из Telegram: {response.text}")
    return None
