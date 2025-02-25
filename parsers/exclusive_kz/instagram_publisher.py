import requests
import re
import json
from shared.config import EXCLUSIVE_INSTAGRAM_ACCESS_TOKEN, EXCLUSIVE_INSTAGRAM_ACCOUNT_ID
from shared.constants import EMOJI_PATH

def publish_to_instagram(image_url, post_url, text_content):
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

        paragraphs = [p.strip() for p in text_content.split("\n") if p.strip()]
        paragraphs = [p for p in paragraphs if not p.lower().startswith("фото:")]

        if paragraphs:
            paragraphs[0] = f"{selected_emoji} {paragraphs[0]}"

        formatted_text = "\n\n".join(paragraphs)

        formatted_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', formatted_text)

        caption = (
            f"{formatted_text}\n\n"
            f"🌐 Наш сайт: exclusive.kz\n"
            f"✅ Telegram канал: https://t.me/kzexclusive\n\n"
            f"Источник: {post_url}\n\n"
            f"#Новости #События"
        )

        MAX_INSTAGRAM_CAPTION_LENGTH = 1900
        if len(caption) > MAX_INSTAGRAM_CAPTION_LENGTH:
            truncated_caption = caption[:MAX_INSTAGRAM_CAPTION_LENGTH]
            truncated_caption = re.sub(r"[^.!?]*$", "", truncated_caption)
            caption = truncated_caption

        upload_url = f"https://graph.facebook.com/v17.0/{EXCLUSIVE_INSTAGRAM_ACCOUNT_ID}/media"

        data = {
            'image_url': image_url,
            'caption': caption,
            'access_token': EXCLUSIVE_INSTAGRAM_ACCESS_TOKEN
        }

        response = requests.post(upload_url, data=data)

        if response.status_code != 200:
            print(f"❌ Ошибка загрузки изображения: {response.text}")
            return

        media_id = response.json().get('id')
        print(f"✅ Медиа загружено. Media ID: {media_id}")

        publish_url = f"https://graph.facebook.com/v17.0/{EXCLUSIVE_INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_data = {
            'creation_id': media_id,
            'access_token': EXCLUSIVE_INSTAGRAM_ACCESS_TOKEN
        }

        publish_response = requests.post(publish_url, data=publish_data)

        if publish_response.status_code == 200:
            print("🎉 Публикация успешно создана в Instagram!")
        else:
            print(f"❌ Ошибка публикации в Instagram: {publish_response.text}")

    except Exception as e:
        print(f"⚠️ Ошибка при публикации в Instagram: {e}")
