import requests
import json
import re
from shared.config import EXCLUSIVE_FACEBOOK_PAGE_ID, EXCLUSIVE_INSTAGRAM_ACCESS_TOKEN
from shared.constants import EMOJI_PATH

def publish_to_facebook(image_url: object, text_content: object, post_url: object) -> object:
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

        full_message = (
            f"{selected_emoji} {text_content}\n\n"
            f"🌐Наш сайт: exclusive.kz\n"
            f"✅ Telegram канал: https://t.me/kzexclusive\n\n"
            f"Источник: {post_url}\n\n"
            f"#Новости #События"
        )

        post_url_fb = f"https://graph.facebook.com/v17.0/{EXCLUSIVE_FACEBOOK_PAGE_ID}/photos"

        payload = {
            'url': image_url,
            'caption': full_message,
            'access_token': EXCLUSIVE_INSTAGRAM_ACCESS_TOKEN
        }

        response = requests.post(post_url_fb, data=payload)

        if response.status_code == 200:
            print("🎉 Публикация успешно создана на Facebook!")
        else:
            print(f"❌ Ошибка публикации в Facebook: {response.text}")

    except Exception as e:
        print(f"⚠️ Ошибка при публикации в Facebook: {e}")
