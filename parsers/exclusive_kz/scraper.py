import requests
import os
from bs4 import BeautifulSoup
import asyncio
from shared.constants import EXCLUSIVE_IMAGE_DIR, EXCLUSIVE_OUTPUT_DIR, EXCLUSIVE_TARGET_DATE
from shared.config import USER_AGENT
from parsers.exclusive_kz.utils import download_image, load_processed_articles, add_processed_article
from parsers.exclusive_kz.image_generator import create_social_media_image, extract_photo_author
from parsers.exclusive_kz.telegram_bot import send_to_telegram, get_telegram_file_url
from parsers.exclusive_kz.instagram_publisher import publish_to_instagram
from parsers.exclusive_kz.facebook_publisher import publish_to_facebook

BASE_URL = "https://exclusive.kz/category/kontekst-dnya/"
PROCESSED_FILE = "data/exclusive_processed.json"

def scrape_page():
    url = BASE_URL
    count = 1
    page_count = 0
    max_pages = 1

    processed_articles = load_processed_articles(PROCESSED_FILE)

    print(f"🔍 Собираем новости за {EXCLUSIVE_TARGET_DATE} число")

    while url and page_count < max_pages:
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
        if response.status_code != 200:
            print("❌ Ошибка загрузки страницы")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", class_="section__item item")

        if not items:
            print("❌ Не найдено ни одной статьи.")
            break

        for item in items:
            title_tag = item.find("h2", class_="item__title")
            image_tag = item.find("img", class_="item__image")
            date_tag = item.find("p", class_="item__time")
            link_tag = title_tag.find("a") if title_tag else None
            article_url = link_tag["href"] if link_tag else None

            if not date_tag:
                continue

            try:
                post_day = int(date_tag.get_text(strip=True).split()[0])
            except (IndexError, ValueError):
                continue

            if post_day != EXCLUSIVE_TARGET_DATE:
                print(f"⏩ Пропущена статья за {post_day} число")
                continue

            if title_tag and image_tag and article_url:
                title = title_tag.get_text(strip=True)

                if any(article.get("title") == title and article.get("status") == "processed" for article in processed_articles):
                    print(f"⏩ Уже обработано: {title}")
                    continue

                image_url = image_tag.get("src", "").strip()
                if not image_url:
                    print(f"❌ Не найдено изображение для: {title}")
                    continue

                print(f"{count}. {title}")
                image_filename = os.path.join(EXCLUSIVE_IMAGE_DIR, f"{count}.jpg")
                download_image(image_url, image_filename)

                image_author = extract_photo_author(article_url)
                article_content = extract_article_content(article_url)

                output_image_path = os.path.join(EXCLUSIVE_OUTPUT_DIR, f"post_{count}.png")
                create_social_media_image(title, image_filename, output_image_path, image_author)

                file_id = asyncio.run(send_to_telegram(output_image_path, title, article_url, article_content))

                if file_id:
                    public_image_url = get_telegram_file_url(file_id)
                    if public_image_url:
                        publish_to_instagram(public_image_url, article_url, article_content)
                        publish_to_facebook(public_image_url, article_url, article_content)

                    else:
                        print("❌ Не удалось получить публичный URL изображения")
                else:
                    print("❌ Ошибка отправки изображения в Telegram")

                add_processed_article(PROCESSED_FILE, title, article_url)
                count += 1

        page_count += 1

def extract_article_content(article_url):
    response = requests.get(article_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    content = []

    article_body = soup.find("div", class_="entry-content")
    if not article_body:
        return ""

    seen_quotes = set()

    for element in article_body.find_all(["p", "blockquote"], recursive=True):
        if element.name == "blockquote":
            quote_text = element.get_text(" ", strip=True)
            cite_tag = element.find("cite")
            cite_text = cite_tag.get_text(" ", strip=True) if cite_tag else ""

            formatted_quote = f"{quote_text} — {cite_text}" if cite_text else quote_text

            if formatted_quote not in seen_quotes:
                content.append(formatted_quote)
                seen_quotes.add(formatted_quote)

        elif element.name == "p":
            text = element.get_text(" ", strip=True)
            content.append(text)

    clean_content = list(dict.fromkeys([line.strip() for line in content if line.strip()]))
    return "\n\n".join(clean_content[:10])

