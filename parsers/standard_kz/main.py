import os
import requests
import asyncio
from scraper import scrape_posts
from image_generator import create_social_media_image
from telegram_bot import send_to_telegram
from config import IMAGE_DIR, OUTPUT_DIR

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return True
        else:
            print(f"Ошибка загрузки {url}: статус {response.status_code}")
            return False
    except Exception as e:
        print(f"Ошибка при скачивании {url}: {e}")
        return False


posts = scrape_posts()
for count, (post_datetime, title, post_url, image_url, image_author, text_content) in enumerate(posts, 1):
    image_filename = f"{IMAGE_DIR}/post_{count}.jpg"

    if not download_image(image_url, image_filename):
        print(f"Пропускаем пост: {title}, так как изображение не загружено.")
        continue

    output_image_path = f"{OUTPUT_DIR}/post_{count}.png"

    create_social_media_image(title, image_filename, image_author, output_image_path)

    asyncio.run(send_to_telegram(output_image_path, title, post_url, text_content))

print("✅ Все посты обработаны успешно.")
