import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

BASE_URL = "https://exclusive.kz/category/kontekst-dnya/"
TARGET_DATE = "11 февраля, 2025"

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
        print(f"Не удалось скачать изображение: {url}")


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

    font_size = 80
    line_spacing = 10
    font = ImageFont.truetype(FONT_PATH, font_size)

    wrapped_text = wrap_text(draw, title.upper(), font, max_text_width)

    while True:
        lines = wrapped_text.split("\n")
        total_text_height = sum(
            draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines) + (
                                        len(lines) - 1) * line_spacing

        if total_text_height <= max_text_height or font_size <= 30:
            break

        font_size -= 2
        line_spacing -= 1 if line_spacing > 5 else 0
        font = ImageFont.truetype(FONT_PATH, font_size)
        wrapped_text = wrap_text(draw, title.upper(), font, max_text_width)

    text_start_y = text_y + (max_text_height - total_text_height) // 2
    current_y = text_start_y

    for line in wrapped_text.split("\n"):
        draw.text((text_x, current_y), line, font=font, fill="white")
        current_y += draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[
            1] + line_spacing

    final_image.save(output_path)
    print(f"✅ Создано изображение: {output_path}")


def scrape_page():
    url = BASE_URL
    data = []
    count = 1
    page_count = 0
    max_pages = 3

    while url and page_count < max_pages:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print("Ошибка загрузки страницы")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", class_="section__item item")

        if not items:
            print("Не найдено ни одной статьи. Проверь структуру HTML.")
            break

        for item in items:
            title_tag = item.find("h2", class_="item__title")
            image_tag = item.find("img", class_="item__image")
            time_tag = item.find("p", class_="item__time")

            if title_tag and image_tag and time_tag:
                post_date = time_tag.text.strip()
                print(f"Дата поста: {post_date}")

                if TARGET_DATE in post_date:
                    title = title_tag.find("a").text.strip()
                    image_url = image_tag.get("src", "").strip()

                    if not image_url:
                        print(f"Не найдено изображение для: {title}")
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
            print(f"Переход на следующую страницу: {url}")
        else:
            url = None

    if data:
        df = pd.DataFrame(data, columns=["Title", "Date", "Image Path"])
        df.to_excel("scraped_data.xlsx", index=False)
        print("Данные успешно сохранены в scraped_data.xlsx")
    else:
        print("Данные не найдены. Проверь TARGET_DATE и структуру HTML.")


if __name__ == "__main__":
    scrape_page()