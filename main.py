import requests
from bs4 import BeautifulSoup
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from datetime import datetime
import locale
from babel.dates import format_date
from dotenv import load_dotenv
import asyncio
import re
import html
from aiogram import Bot
from aiogram.types import FSInputFile
import logging

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

BASE_URL = "https://exclusive.kz/category/kontekst-dnya/"
TARGET_DATE = format_date(datetime.today(), format="d MMMM, yyyy", locale="ru")

TEMPLATE_PATH = "psd/post-image.png"
IMAGE_DIR = "scraped_images"
OUTPUT_DIR = "generated_posts"
FONT_PATH = "font/Montserrat-Bold.ttf"

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_published_articles():
    if not os.path.exists("published_articles.txt"):
        return set()
    with open("published_articles.txt", "r", encoding="utf-8") as file:
        return set(line.strip() for line in file.readlines())

def save_published_article(article_url):
    with open("published_articles.txt", "a", encoding="utf-8") as file:
        file.write(f"{article_url}\n")


async def send_to_telegram(image_path, post_url, article_content):
    caption_limit = 1024
    text_limit = 995

    exclude_texts = ["Избранные материалы от Exclusive", "наших рассылках"]
    article_content = "\n".join(
        [line for line in article_content.split("\n") if not any(ex in line for ex in exclude_texts)]
    )

    kazakhstan_keywords = ["Казахстан", "Алматы", "Астана", "РК"]
    flag_emoji = "🇰🇿" if any(word in article_content for word in kazakhstan_keywords) else "📰"

    article_content = html.unescape(article_content)

    paragraphs = article_content.split("\n")
    formatted_text = []
    first_paragraph_added = False

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if not first_paragraph_added and paragraph.startswith("**") and paragraph.endswith("**"):
            formatted_text.append(f"{flag_emoji} {paragraph}")
            first_paragraph_added = True
            continue

        paragraph = re.sub(r"\n?(https?://\S+)", r"\1", paragraph)

        paragraph = re.sub(r"(\S)(https?://)", r"\1 \2", paragraph)

        formatted_text.append(paragraph)

    formatted_text = "\n\n".join(formatted_text)

    caption = f"{formatted_text}\n\n[🔗 Читать на Exclusive.kz]({post_url})"

    if len(caption) > caption_limit:
        truncated_text = formatted_text[:text_limit]
        truncated_text = re.sub(r"[^.!?]*$", "", truncated_text)
        caption = f"{truncated_text}\n\n[🔗 Читать на Exclusive.kz]({post_url})"

    async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
        try:
            image = FSInputFile(image_path)
            await bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=image, caption=caption, parse_mode="Markdown")
            logging.info(f"✅ Успешно отправлено в Telegram: {post_url}")
            save_published_article(post_url)
        except Exception as e:
            logging.error(f"❌ Ошибка отправки в Telegram: {e}")


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


def load_processed_articles():
    if not os.path.exists("processed_articles.txt"):
        return set()
    with open("processed_articles.txt", "r", encoding="utf-8") as file:
        return set(line.strip() for line in file.readlines())

def save_processed_articles(processed_articles):
    with open("processed_articles.txt", "w", encoding="utf-8") as file:
        file.writelines(f"{article}\n" for article in processed_articles)

def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        print(f"❌ Не удалось скачать изображение: {url}")


def extract_photo_author(article_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(article_url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Ошибка загрузки страницы: {article_url}")
        return "Фото: из открытых источников"

    soup = BeautifulSoup(response.text, "html.parser")

    entry_content = soup.find("div", class_="entry-content")
    if not entry_content:
        print("❌ Не найден блок entry-content")
        return "Фото: из открытых источников"

    author_tag = entry_content.find("p", string=lambda text: text and "Фото" in text)

    if author_tag:
        return author_tag.get_text(strip=True)

    return "Фото: из открытых источников"


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        text_width = draw.textbbox((0, 0), test_line, font=font)[2]

        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return "\n".join(lines)

import textwrap

def fit_text_into_lines(text, font, max_width, target_lines, force_split, draw):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = (current_line + " " + word).strip()
        text_width = draw.textbbox((0, 0), test_line, font=font)[2]

        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

        if len(lines) == target_lines - 1:
            remaining_text = " ".join(words[words.index(word):])
            lines.append(remaining_text)
            break

    if current_line and len(lines) < target_lines:
        lines.append(current_line)

    while len(lines) < target_lines:
        lines.append("")

    if force_split and target_lines == 3:
        wrapped_lines = textwrap.wrap(text, width=len(text) // target_lines)
        if len(wrapped_lines) == 3:
            return wrapped_lines

    return lines[:target_lines]

def create_social_media_image(title, image_path, output_path, image_author):
    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    news_image = Image.open(image_path).convert("RGB")

    enhancer = ImageEnhance.Color(news_image)
    news_image = enhancer.enhance(1.5)

    target_height = 1000
    aspect_ratio = news_image.width / news_image.height
    new_width = int(target_height * aspect_ratio)
    news_image = news_image.resize((new_width, target_height))

    final_image = Image.new("RGB", template.size, (0, 0, 0))
    x_offset = (template.width - new_width) // 2
    final_image.paste(news_image, (x_offset, 0))
    final_image.paste(template, (0, 0), mask=template)

    draw = ImageDraw.Draw(final_image)
    max_text_width = template.width - 86
    text_x = 43
    text_y = 792
    text_bottom = 947
    max_text_height = text_bottom - text_y

    if len(title) <= 60:
        font_size = 49
        target_lines = 3
        force_split = True
    elif len(title) <= 90:
        font_size = 49
        target_lines = 3
        force_split = False
    else:
        font_size = 35
        target_lines = 4
        force_split = False

    font = ImageFont.truetype(FONT_PATH, font_size)
    wrapped_text = fit_text_into_lines(title.upper(), font, max_text_width, target_lines, force_split, draw)

    wrapped_text = [line for line in wrapped_text if line.strip()]

    while len(wrapped_text) < target_lines:
        words = " ".join(wrapped_text).split()
        avg_words_per_line = len(words) // target_lines
        wrapped_text = [" ".join(words[i * avg_words_per_line: (i + 1) * avg_words_per_line]) for i in
                        range(target_lines)]

    while any(draw.textbbox((0, 0), line, font=font)[2] > max_text_width for line in wrapped_text):
        font_size -= 2
        font = ImageFont.truetype(FONT_PATH, font_size)
        wrapped_text = fit_text_into_lines(title.upper(), font, max_text_width, target_lines, force_split, draw)

    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    total_text_height = target_lines * line_height

    text_start_y = text_y + (max_text_height - total_text_height) // 2
    current_y = text_start_y

    rect_x = 17
    rect_width = 14
    rect_height = total_text_height
    rect_y = text_start_y

    draw.rectangle(
        [(rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height)],
        fill="#cc2321"
    )

    for line in wrapped_text:
        draw.text((text_x, current_y), line, font=font, fill="white")
        current_y += line_height

    author_font = ImageFont.truetype(FONT_PATH, 15)
    author_x = 17
    author_y = 975
    draw.text((author_x, author_y), image_author.upper(), font=author_font, fill=(255, 255, 255, 80))

    final_image.save(output_path)
    print(f"✅ Создано изображение: {output_path} (Шрифт: {font_size}px, Строк: {target_lines})")


def scrape_page():
    url = BASE_URL
    data = []
    count = 1
    page_count = 0
    max_pages = 1

    processed_articles = load_processed_articles()

    print(f"🔍 Собираем новости за {TARGET_DATE}")

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

                if title in processed_articles:
                    print(f"⏩ Уже обработано: {title}")
                    continue

                image_url = image_tag.get("src", "").strip()
                if not image_url:
                    print(f"❌ Не найдено изображение для: {title}")
                    continue

                print(f"{count}. {title}")
                image_filename = os.path.join(IMAGE_DIR, f"{count}.jpg")
                download_image(image_url, image_filename)

                image_author = extract_photo_author(article_url)
                article_content = extract_article_content(article_url)

                output_image_path = os.path.join(OUTPUT_DIR, f"post_{count}.png")
                create_social_media_image(title, image_filename, output_image_path, image_author)

                data.append([title, article_url, image_author, output_image_path])
                processed_articles.add(title)
                count += 1

                asyncio.run(send_to_telegram(output_image_path, article_url, article_content))

        page_count += 1

    save_processed_articles(processed_articles)

if __name__ == "__main__":
    scrape_page()
