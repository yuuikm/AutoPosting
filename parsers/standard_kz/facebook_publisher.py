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
        return []

def clean_source_spacing(text):
    return re.sub(
        r"(\b(?:Zakon\.kz|Informburo\.kz|Exclusive\.kz|Orda\.kz|Tengrinews\.kz|Standard\.kz)) \.",
        r"\1.",
        text
    )

def publish_to_facebook_standard(image_url, post_url, text_content):
    try:
        with open(EMOJI_PATH, "r", encoding="utf-8") as f:
            emoji_rules = json.load(f)

        matched_emojis = [
            emoji for emoji, keywords in emoji_rules.items()
            if any(re.search(rf"\b{re.escape(word)}\b", text_content, re.IGNORECASE) for word in keywords)
        ][:2]

        selected_emoji = " ".join(matched_emojis or ["📰"])

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

        hashtags = " ".join(get_hashtags(text_content))

        caption = (
            f"{primary_content}\n\n"
            f"🌐 Наш сайт: standard.kz\n"
            f"✅ Telegram канал: https://t.me/standardkz\n\n"
            f"Источник: {post_url}\n\n"
            f"#Новости #Казахстан {hashtags}"
        )

        response = requests.post(
            f"https://graph.facebook.com/v17.0/{STANDARD_FACEBOOK_PAGE_ID}/photos",
            data={
                "url": image_url,
                "message": caption,
                "access_token": STANDARD_ACCESS_TOKEN
            }
        )

        if response.status_code != 200:
            raise Exception(f"Facebook error: {response.text}")

    except:
        pass
