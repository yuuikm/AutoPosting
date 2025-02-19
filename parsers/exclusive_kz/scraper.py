import requests
import os
from bs4 import BeautifulSoup
import asyncio
from shared.constants import EXCLUSIVE_IMAGE_DIR, EXCLUSIVE_OUTPUT_DIR, EXCLUSIVE_TARGET_DATE
from shared.config import USER_AGENT
from .utils import download_image, load_processed_articles, save_processed_articles
from .image_generator import create_social_media_image, extract_photo_author
from .telegram_bot import send_to_telegram

BASE_URL = "https://exclusive.kz/category/kontekst-dnya/"
PROCESSED_FILE = "data/exclusive_processed.txt"

def scrape_page():
    url = BASE_URL
    data = []
    count = 1
    page_count = 0
    max_pages = 1

    # processed_articles = load_processed_articles()

    print(f"🔍 Собираем новости за {EXCLUSIVE_TARGET_DATE}")

    while url and page_count < max_pages:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
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
            link_tag = title_tag.find("a") if title_tag else None
            article_url = link_tag["href"] if link_tag else None

            if title_tag and image_tag and article_url:
                title = title_tag.get_text(strip=True)

                # if title in processed_articles:
                #     print(f"⏩ Уже обработано: {title}")
                #     continue

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

                data.append([title, article_url, image_author, output_image_path])
                # processed_articles.add(title)
                count += 1

                asyncio.run(send_to_telegram(output_image_path, article_url, article_content))

        page_count += 1

    # save_processed_articles(processed_articles)

def extract_article_content(article_url):
    response = requests.get(article_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    content = []

    title_tag = soup.find("h1", class_="section__title")
    if title_tag:
        content.append(f"**{title_tag.get_text(strip=True)}**\n")

    article_body = soup.find("div", class_="entry-content")
    if not article_body:
        return ""

    for element in article_body.find_all(["p", "blockquote", "strong", "a"], recursive=True):
        text = element.get_text(strip=True)

        if element.name == "p":
            if element.find("strong"):
                content.append(f"**{text}**")
            else:
                content.append(text)
        elif element.name == "blockquote":
            content.append(f"> {text}")
        elif element.name == "a":
            link_url = element.get("href")
            if link_url:
                link_text = element.get_text(strip=True)
                content.append(f"[{link_text}]({link_url})")

    return "\n\n".join(content[:6])
