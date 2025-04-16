import requests
import os
import asyncio
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from shared.constants import STANDARD_IMAGE_DIR, STANDARD_OUTPUT_DIR, STANDARD_TARGET_DATE, STANDARD_PUBLIC_URL
from shared.config import USER_AGENT
from .utils import download_image, load_processed_articles, add_processed_article
from .image_generator import create_social_media_image
from .telegram_bot import send_to_telegram, get_telegram_file_url
from .instagram_publisher import publish_to_instagram_standard
from .facebook_publisher import publish_to_facebook_standard
from shared.constants import STANDARD_PROCESSED_FILE

BASE_URLS = [
    "https://standard.kz/ru/post/archive",
    "https://standard.kz/kz/post/archive"
]

PROCESSED_FILE = STANDARD_PROCESSED_FILE

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
    return "\n\n".join(clean_content[:10])

def scrape_posts():
    count = 1
    processed_articles = load_processed_articles(PROCESSED_FILE)
    posts = []
    for base_url in BASE_URLS:
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
                continue
            post_response = requests.get(post_url, headers={"User-Agent": USER_AGENT})
            post_soup = BeautifulSoup(post_response.text, "html.parser")
            image_tag = post_soup.select_one("div.entry__img-holder img")
            author_tag = post_soup.select_one("div.entry__img-holder span")
            image_author = author_tag.text.strip() if author_tag else "Источник: Standard.kz"
            text_content = extract_article_content(post_url)
            image_url = "https://standard.kz" + image_tag["src"].strip() if image_tag else ""
            if not image_url:
                continue
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
    asyncio.run(send_to_social_media(posts))

async def send_to_social_media(posts, send_message_callback=None):
    if not posts:
        return
    for index, post in enumerate(posts):
        image_path = post["image_path"]
        post_url = post["post_url"]
        text_content = post["text_content"]
        title = post["title"]
        file_id = await send_to_telegram(image_path, title, post_url, text_content)
        if not file_id:
            continue
        public_image_url = f"{STANDARD_PUBLIC_URL}/{os.path.basename(image_path)}"
        try:
            publish_to_instagram_standard(public_image_url, post_url, text_content)
        except Exception:
            pass
        try:
            publish_to_facebook_standard(public_image_url, post_url, text_content)
        except Exception:
            pass
        if index < len(posts) - 1:
            await asyncio.sleep(random.randint(250, 600))