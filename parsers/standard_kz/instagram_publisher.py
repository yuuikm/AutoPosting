import requests
import re
import json
import random
from shared.config import STANDARD_ACCESS_TOKEN, STANDARD_INSTAGRAM_ACCOUNT_ID
from shared.constants import EMOJI_PATH, HASHTAGS_PATH

def get_hashtags(text_content):
    try:
        with open(HASHTAGS_PATH, "r", encoding="utf-8") as f:
            hashtag_rules = json.load(f)

        found_hashtags = set()

        for keyword, hashtags in hashtag_rules.items():
            if re.search(rf"\b{re.escape(keyword)}\b", text_content, re.IGNORECASE):
                found_hashtags.update(hashtags)

        return random.sample(list(found_hashtags), min(len(found_hashtags), 3)) if found_hashtags else []

    except Exception as e:
        print(f"⚠️ Ошибка загрузки хештегов: {e}")
        return []

def publish_to_instagram_standard(image_url, post_url, text_content):
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
        paragraphs = [p for p in paragraphs if not re.match(r"(?i)^фото[:\s]", p)]

        if paragraphs:
            paragraphs[0] = f"{selected_emoji} {paragraphs[0]}"

        formatted_text = "\n\n".join(paragraphs)
        formatted_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', formatted_text)

        hashtags = get_hashtags(text_content)
        hashtags_str = " ".join(hashtags)

        static_footer = (
            f"\n\n🌐 Наш сайт: standard.kz\n"
            f"✅ Telegram канал: https://t.me/standardkz\n\n"
            f"Источник: {post_url}\n\n"
            f"#Новости #Казахстан {hashtags_str}"
        )

        MAX_INSTAGRAM_CAPTION_LENGTH = 2200
        max_content_length = MAX_INSTAGRAM_CAPTION_LENGTH - len(static_footer)

        if len(formatted_text) > max_content_length:
            truncated_text = formatted_text[:max_content_length]
            truncated_text = re.sub(r"[^.!?]*$", "", truncated_text)
            formatted_text = truncated_text

        caption = f"{formatted_text}{static_footer}"

        upload_url = f"https://graph.facebook.com/v17.0/{STANDARD_INSTAGRAM_ACCOUNT_ID}/media"

        data = {
            'image_url': image_url,
            'caption': caption,
            'access_token': STANDARD_ACCESS_TOKEN
        }

        response = requests.post(upload_url, data=data)

        if response.status_code != 200:
            print(f"❌ Ошибка загрузки изображения: {response.text}")
            return

        media_id = response.json().get('id')
        print(f"✅ Медиа загружено. Media ID: {media_id}")

        publish_url = f"https://graph.facebook.com/v17.0/{STANDARD_INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_data = {
            'creation_id': media_id,
            'access_token': STANDARD_ACCESS_TOKEN
        }

        publish_response = requests.post(publish_url, data=publish_data)

        if publish_response.status_code == 200:
            print("🎉 Публикация успешно создана в Instagram (Standard.kz)!")
        else:
            print(f"❌ Ошибка публикации в Instagram: {publish_response.text}")

    except Exception as e:
        print(f"⚠️ Ошибка при публикации в Instagram: {e}")
