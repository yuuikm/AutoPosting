import requests
import os
import asyncio
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from shared.constants import STANDARD_IMAGE_DIR, STANDARD_OUTPUT_DIR, STANDARD_TARGET_DATE
from shared.config import USER_AGENT
from .utils import download_image, load_processed_articles, save_processed_articles, add_processed_article
from .image_generator import create_social_media_image
from .telegram_bot import send_to_telegram


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

    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)

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

    title_tag = soup.find("h1", class_="entry__title")
    if title_tag:
        content.append(f"**{title_tag.get_text(strip=True)}**")

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

    for base_url in BASE_URLS:
        print(f"Загружаем страницу: {base_url}")
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
            article_tag = post_soup.select_one("div.entry__article")

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

            asyncio.run(send_to_telegram(output_image_path, title, post_url, text_content))
            add_processed_article(PROCESSED_FILE, title, post_url)

            count += 1

    print("✅ Все посты обработаны успешно.")
