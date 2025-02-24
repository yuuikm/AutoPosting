import asyncio
import re
import json
import requests
from telegram import Bot
from shared.config import EXCLUSIVE_TELEGRAM_BOT_TOKEN, EXCLUSIVE_TELEGRAM_CHANNEL_ID
from shared.constants import EMOJI_PATH

async def send_to_telegram(image_path, title, post_url, text_content):
    CAPTION_LIMIT = 1024
    TEXT_LIMIT = 995

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

    paragraphs = [p.strip() for p in text_content.split("\n") if p.strip()]
    paragraphs = [p for p in paragraphs if not p.lower().startswith("фото:")]

    if paragraphs:
        paragraphs[0] = f"**{paragraphs[0]}**"

    formatted_text = "\n\n".join(paragraphs)

    caption = f"{selected_emoji} {formatted_text}\n\n[🔗 Читать на Exclusive.kz]({post_url})"

    if len(caption) > CAPTION_LIMIT:
        truncated_text = formatted_text[:TEXT_LIMIT]
        truncated_text = re.sub(r"[^.!?]*$", "", truncated_text)
        caption = f"{selected_emoji} {truncated_text}\n\n[🔗 Читать на Exclusive.kz]({post_url})"

    async with Bot(token=EXCLUSIVE_TELEGRAM_BOT_TOKEN) as bot:
        with open(image_path, "rb") as image:
            message = await bot.send_photo(
                chat_id=EXCLUSIVE_TELEGRAM_CHANNEL_ID,
                photo=image,
                caption=caption,
                parse_mode="Markdown"
            )

    print(f"✅ Публикация отправлена: {title}")

    return message.photo[-1].file_id

def get_telegram_file_url(file_id):
    file_info_url = f"https://api.telegram.org/bot{EXCLUSIVE_TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    response = requests.get(file_info_url)

    if response.status_code == 200:
        file_path = response.json()['result']['file_path']
        file_url = f"https://api.telegram.org/file/bot{EXCLUSIVE_TELEGRAM_BOT_TOKEN}/{file_path}"
        return file_url
    else:
        print(f"❌ Ошибка получения файла из Telegram: {response.text}")
        return None
