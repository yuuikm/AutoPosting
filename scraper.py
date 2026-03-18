import logging
import os
import requests
import asyncio
import time
import random
from uuid import uuid4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from shared.constants import IMAGE_DIR, OUTPUT_DIR, TARGET_DATE, PUBLIC_URL, PROCESSED_FILE
from shared.config import USER_AGENT
from utils import download_image, load_processed_articles, add_processed_article, update_article_status
from image_generator import create_social_media_image
from publishers.telegram import send_to_telegram
from publishers.instagram import publish_to_instagram
from publishers.facebook import publish_to_facebook

logger = logging.getLogger(__name__)

BASE_URLS = [
    "https://standard.kz/ru/post/archive",
    "https://standard.kz/kz/post/archive"
]


def get_dynamic_html(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Added for stability in containers
    
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
    service = Service(chromedriver_path)
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
            if post_date != TARGET_DATE:
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
            image_filename = os.path.join(IMAGE_DIR, f"{count}.jpg")
            download_image(image_url, image_filename)
            output_image_path = os.path.join(OUTPUT_DIR, f"post_{count}.png")
            create_social_media_image(title, image_filename, image_author, output_image_path)
            posts.append({
                "image_path": output_image_path,
                "title": title,
                "post_url": post_url,
                "text_content": text_content
            })
            add_processed_article(PROCESSED_FILE, title, post_url)
            count += 1
    summary = asyncio.run(send_to_social_media(posts))
    return summary


async def send_to_social_media(posts, send_message_callback=None):
    stats = {"total": len(posts), "telegram": 0, "instagram": 0, "facebook": 0,
             "telegram_fail": 0, "instagram_fail": 0, "facebook_fail": 0}

    if not posts:
        return stats

    for index, post in enumerate(posts):
        image_path = post["image_path"]
        post_url = post["post_url"]
        text_content = post["text_content"]
        title = post["title"]

        # Telegram
        file_id = await send_to_telegram(image_path, title, post_url, text_content)
        tg_ok = file_id is not None
        if tg_ok:
            stats["telegram"] += 1
        else:
            stats["telegram_fail"] += 1
        update_article_status(PROCESSED_FILE, title, "telegram", tg_ok)

        # Instagram & Facebook need public URL
        unique_suffix = uuid4().hex[:8]
        public_image_url = f"{PUBLIC_URL}/{os.path.basename(image_path)}?v={unique_suffix}"

        # Instagram
        ig_ok = False
        try:
            ig_ok = publish_to_instagram(public_image_url, post_url, text_content)
        except Exception:
            pass
        if ig_ok:
            stats["instagram"] += 1
        else:
            stats["instagram_fail"] += 1
        update_article_status(PROCESSED_FILE, title, "instagram", ig_ok)

        # Facebook
        fb_ok = False
        try:
            fb_ok = publish_to_facebook(public_image_url, post_url, text_content)
        except Exception:
            pass
        if fb_ok:
            stats["facebook"] += 1
        else:
            stats["facebook_fail"] += 1
        update_article_status(PROCESSED_FILE, title, "facebook", fb_ok)

        if index < len(posts) - 1:
            await asyncio.sleep(random.randint(250, 600))

    return stats
