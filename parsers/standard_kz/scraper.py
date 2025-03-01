import requests
import os
import asyncio
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from shared.constants import STANDARD_IMAGE_DIR, STANDARD_OUTPUT_DIR, STANDARD_TARGET_DATE
from shared.config import USER_AGENT
from .utils import download_image, load_processed_articles, add_processed_article
from .image_generator import create_social_media_image
from .telegram_bot import send_to_telegram, get_telegram_file_url
from .instagram_publisher import publish_to_instagram_standard
from .facebook_publisher import publish_to_facebook_standard

BASE_URLS = [
    "https://standard.kz/ru/post/archive",
    "https://standard.kz/kz/post/archive"
]

PROCESSED_FILE = "data/standard_processed.json"

def get_dynamic_html(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    driver.quit()
    return html

def extract_article_content(article_url):
    response = requests.get(article_url, headers={"User-Agent": USER_AGENT})
    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    content = []

    article_body = soup.find("div", class_="entry__article")
    if not article_body:
        return ""

    for element in article_body.find_all(["p", "blockquote", "strong", "a"], recursive=True):
        text = element.get_text(" ", strip=True)

        if element.name == "p" and text:
            for link in element.find_all("a", href=True):
                href = link["href"]
                link_text = link.get_text(strip=True)
                text = text.replace(link_text, f"[{link_text}]({href})")
            content.append(text)

    clean_content = []
    seen = set()
    for line in content:
        if line and line not in seen:
            clean_content.append(line.strip())
            seen.add(line)

    formatted_content = "\n\n".join(clean_content[:10])
    return formatted_content

def scrape_posts():
    count = 1
    processed_articles = load_processed_articles(PROCESSED_FILE)
    print(f"🔍 Собираем новости за {STANDARD_TARGET_DATE}")

    posts = []

    for base_url in BASE_URLS:
        print(f"📄 Загружаем страницу: {base_url}")
        html = get_dynamic_html(base_url)
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table.table-striped tbody tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            post_datetime = cols[0].text.strip()
            post_date, _ = post_datetime.split(" ")
            if post_date != STANDARD_TARGET_DATE:
                continue

            title_tag = cols[1].find("a")
            if not title_tag:
                continue

            title = title_tag.text.strip()
            post_url = title_tag["href"].strip()

            if any(article.get("title") == title for article in processed_articles):
                print(f"⏩ Уже обработано: {title}")
                continue

            post_response = requests.get(post_url, headers={"User-Agent": USER_AGENT})
            post_soup = BeautifulSoup(post_response.text, "html.parser")

            image_tag = post_soup.select_one("div.entry__img-holder img")
            author_tag = post_soup.select_one("div.entry__img-holder span")

            image_author = author_tag.text.strip() if author_tag else "Источник: Standard.kz"
            text_content = extract_article_content(post_url)
            image_url = "https://standard.kz" + image_tag["src"].strip() if image_tag else ""

            if not image_url:
                print(f"❌ Не найдено изображение для: {title}")
                continue

            print(f"{count}. {title}")
            image_filename = os.path.join(STANDARD_IMAGE_DIR, f"{count}.jpg")
            download_image(image_url, image_filename)

            output_image_path = os.path.join(STANDARD_OUTPUT_DIR, f"post_{count}.png")
            create_social_media_image(title, image_filename, image_author, output_image_path)

            posts.append({
                "image_path": output_image_path,
                "title": title,
                "post_url": post_url,
                "text_content": text_content
            })

            add_processed_article(PROCESSED_FILE, title, post_url)
            count += 1

    print(f"✅ Собрано {len(posts)} постов. Передаю их на публикацию...")

    asyncio.run(send_to_social_media(posts))


async def send_to_social_media(posts, send_message_callback=None):

    print("🚀 Начинаем публикацию в Telegram, Instagram и Facebook...")
    if send_message_callback:
        await send_message_callback("🚀 Начинаем публикацию в Telegram, Instagram и Facebook...")

    if not posts:
        print("❌ Ошибка: нет постов для публикации.")
        if send_message_callback:
            await send_message_callback("📰 Ошибка: нет постов для публикации.")
        return

    for index, post in enumerate(posts):
        image_path = post["image_path"]
        post_url = post["post_url"]
        text_content = post["text_content"]
        title = post["title"]

        print(f"📤 Отправка в Telegram: {title}")
        if send_message_callback:
            await send_message_callback(f"📤 Отправка в Telegram: {title}")

        file_id = await send_to_telegram(image_path, title, post_url, text_content)

        if not file_id:
            error_msg = f"❌ Ошибка: Telegram НЕ ОТПРАВИЛ {title}! Пропускаем Instagram и Facebook."
            print(error_msg)
            if send_message_callback:
                await send_message_callback(error_msg)
            continue

        print(f"✅ Telegram отправлен. file_id: {file_id}")
        if send_message_callback:
            await send_message_callback(f"✅ Telegram отправлен. file_id: `{file_id}`")

        public_image_url = get_telegram_file_url(file_id)

        if not public_image_url:
            error_msg = f"❌ Ошибка: не удалось получить URL изображения из Telegram для {title}."
            print(error_msg)
            if send_message_callback:
                await send_message_callback(error_msg)
            continue

        print(f"📷 Публикация в Instagram: {title}")
        if send_message_callback:
            await send_message_callback(f"📷 Публикация в Instagram: {title}")

        try:
            publish_to_instagram_standard(public_image_url, post_url, text_content)
            print(f"✅ Успешно опубликовано в Instagram: {title}")
            if send_message_callback:
                await send_message_callback(f"✅ Успешно опубликовано в Instagram: {title}")
        except Exception as e:
            error_msg = f"❌ Ошибка публикации в Instagram: {e}"
            print(error_msg)
            if send_message_callback:
                await send_message_callback(error_msg)

        print(f"📘 Публикация в Facebook: {title}")
        if send_message_callback:
            await send_message_callback(f"📘 Публикация в Facebook: {title}")

        try:
            publish_to_facebook_standard(public_image_url, post_url, text_content)
            print(f"✅ Успешно опубликовано в Facebook: {title}")
            if send_message_callback:
                await send_message_callback(f"✅ Успешно опубликовано в Facebook: {title}")
        except Exception as e:
            error_msg = f"❌ Ошибка публикации в Facebook: {e}"
            print(error_msg)
            if send_message_callback:
                await send_message_callback(error_msg)

        if index < len(posts) - 1:
            delay = random.randint(250, 600)
            print(f"⏳ Ожидание {delay} секунд перед следующим постом...")
            if send_message_callback:
                await send_message_callback(f"⏳ Ожидание {delay} секунд перед следующим постом...")
            await asyncio.sleep(delay)
