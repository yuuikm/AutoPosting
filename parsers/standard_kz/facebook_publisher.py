import requests
import re
import json
import random
from shared.config import STANDARD_ACCESS_TOKEN, STANDARD_FACEBOOK_PAGE_ID
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

def clean_source_spacing(text):
    return re.sub(r"(\b(?:Zakon\.kz|Informburo\.kz|Exclusive\.kz|Orda\.kz|Tengrinews\.kz|Standard\.kz)) \.", r"\1.", text)

def publish_to_facebook_standard(image_url, post_url, text_content):
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

        text_content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text_content)
        text_content = re.sub(r'\[([^\]]+)\]', r'\1', text_content)

        text_content = clean_source_spacing(text_content)

        paragraphs = [p.strip() for p in text_content.split("\n") if p.strip()]
        paragraphs = [p for p in paragraphs if not re.match(r"(?i)^фото[:\s]", p)]

        if paragraphs:
            primary_content = f"{selected_emoji} {paragraphs[0]}"
            if len(paragraphs) > 1:
                primary_content += f"\n\n{paragraphs[1]}"
        else:
            primary_content = f"{selected_emoji} {text_content[:450]}"

        hashtags = get_hashtags(text_content)
        hashtags_str = " ".join(hashtags)

        static_footer = (
            f"\n\n🌐 Наш сайт: standard.kz\n"
            f"✅ Telegram канал: https://t.me/standardkz\n\n"
            f"Источник: {post_url}\n\n"
            f"#Новости #Казахстан {hashtags_str}"
        )

        caption = f"{primary_content}{static_footer}"

        upload_url = f"https://graph.facebook.com/v17.0/{STANDARD_FACEBOOK_PAGE_ID}/photos"

        data = {
            'url': image_url,
            'message': caption,
            'access_token': STANDARD_ACCESS_TOKEN
        }

        response = requests.post(upload_url, data=data)

        if response.status_code == 200:
            print("🎉 Публикация успешно создана на Facebook (Standard.kz)!")
        else:
            print(f"❌ Ошибка публикации в Facebook: {response.text}")

    except Exception as e:
        print(f"⚠️ Ошибка при публикации в Facebook: {e}")
