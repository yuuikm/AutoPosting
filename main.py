import requests
from bs4 import BeautifulSoup
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from datetime import datetime
import locale
from babel.dates import format_date
import textwrap

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

BASE_URL = "https://exclusive.kz/category/kontekst-dnya/"
TARGET_DATE = format_date(datetime.today(), format="d MMMM, yyyy", locale="ru")

TEMPLATE_PATH = "psd/post-image.png"
IMAGE_DIR = "scraped_images"
OUTPUT_DIR = "generated_posts"
FONT_PATH = "font/Montserrat-Bold.ttf"

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        print(f"❌ Не удалось скачать изображение: {url}")


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

def create_social_media_image(title, image_path, output_path):
    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    news_image = Image.open(image_path).convert("RGB")

    enhancer = ImageEnhance.Color(news_image)
    news_image = enhancer.enhance(2.5)

    target_height = 1000
    aspect_ratio = news_image.width / news_image.height
    new_width = int(target_height * aspect_ratio)
    news_image = news_image.resize((new_width, target_height))

    final_image = Image.new("RGB", template.size, (0, 0, 0))
    x_offset = (template.width - new_width) // 2
    final_image.paste(news_image, (x_offset, 0))
    final_image.paste(template, (0, 0), mask=template)

    draw = ImageDraw.Draw(final_image)
    max_text_width = template.width - 100
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


    def fit_text_into_lines(text, font, max_width, target_lines, force_split):
        if force_split:
            words = text.split()
            avg_words_per_line = len(words) // target_lines
            lines = [" ".join(words[i * avg_words_per_line: (i + 1) * avg_words_per_line]) for i in range(target_lines)]
            if len(lines) < target_lines:
                lines.append(" ".join(words[len(lines) * avg_words_per_line:]))
            return lines[:target_lines]
        else:
            wrapped_lines = textwrap.wrap(text, width=30)  # Обычный перенос
            return wrapped_lines[:target_lines] + [""] * (target_lines - len(wrapped_lines))

    wrapped_text = fit_text_into_lines(title.upper(), font, max_text_width, target_lines, force_split)

    # Проверка выхода за границы и уменьшение шрифта, если нужно (только для 4 строк)
    if target_lines == 4:
        while any(draw.textbbox((0, 0), line, font=font)[2] > max_text_width for line in wrapped_text):
            font_size -= 2
            font = ImageFont.truetype(FONT_PATH, font_size)
            wrapped_text = fit_text_into_lines(title.upper(), font, max_text_width, target_lines, force_split)

    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    total_text_height = target_lines * line_height

    text_start_y = text_y + (max_text_height - total_text_height) // 2
    current_y = text_start_y

    for line in wrapped_text:
        draw.text((text_x, current_y), line, font=font, fill="white")
        current_y += line_height

    final_image.save(output_path)
    print(f"✅ Создано изображение: {output_path} (Шрифт: {font_size}px, Строк: {target_lines})")

def scrape_page():
    url = BASE_URL
    data = []
    count = 1
    page_count = 0
    max_pages = 1

    print(f"🔍 Собираем новости за {TARGET_DATE}")

    while url and page_count < max_pages:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print("❌ Ошибка загрузки страницы")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", class_="section__item item")

        if not items:
            print("❌ Не найдено ни одной статьи. Проверь структуру HTML.")
            break

        for item in items:
            title_tag = item.find("h2", class_="item__title")
            image_tag = item.find("img", class_="item__image")
            time_tag = item.find("p", class_="item__time")

            if time_tag:
                post_date = time_tag.text.strip().lower()
                if TARGET_DATE in post_date:
                    print(f"✅ Найдена статья за {TARGET_DATE}: {post_date}")
                else:
                    print(f"❌ Дата не совпадает: {post_date} (ожидали {TARGET_DATE})")

            if title_tag and image_tag and time_tag:
                post_date = time_tag.text.strip()

                if TARGET_DATE in post_date:
                    title = title_tag.find("a").text.strip()
                    image_url = image_tag.get("src", "").strip()

                    if not image_url:
                        print(f"❌ Не найдено изображение для: {title}")
                        continue

                    print(f"{count}. {title}")
                    image_filename = os.path.join(IMAGE_DIR, f"{count}.jpg")
                    download_image(image_url, image_filename)

                    output_image_path = os.path.join(OUTPUT_DIR, f"post_{count}.png")
                    create_social_media_image(title, image_filename, output_image_path)

                    data.append([title, post_date, output_image_path])
                    count += 1

        page_count += 1
        next_page = soup.find("a", class_="next page-numbers")
        if next_page and page_count < max_pages:
            url = next_page.get("href")
            print(f"➡ Переход на следующую страницу: {url}")
        else:
            url = None


if __name__ == "__main__":
    scrape_page()
