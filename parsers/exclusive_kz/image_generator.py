import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from bs4 import BeautifulSoup

from shared.constants import EXCLUSIVE_TEMPLATE_PATH, FONT_PATH

def extract_photo_author(article_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(article_url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Ошибка загрузки страницы: {article_url}")
        return "Фото: из открытых источников"

    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", class_="entry-content")
    if not content:
        print("❌ Не найден основной контент статьи")
        return "Фото: из открытых источников"

    paragraphs = content.find_all("p")
    for p in paragraphs:
        if "Фото" in p.get_text():
            link_tag = p.find("a")
            if link_tag:
                author_text = link_tag.get_text(strip=True)
                return f"Фото: {author_text}"
            else:
                author_text = p.get_text(strip=True).replace("Фото", "").replace(":", "").strip()
                return f"Фото: {author_text}"

    return "Фото: из открытых источников"

def fit_text_dynamically(text, font, max_width, draw):
    wrapped_lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        text_width = draw.textbbox((0, 0), test_line, font=font)[2]

        if text_width <= max_width:
            current_line = test_line
        else:
            wrapped_lines.append(current_line)
            current_line = word

    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines

def create_social_media_image(title, image_path, output_path, image_author):
    template = Image.open(EXCLUSIVE_TEMPLATE_PATH).convert("RGBA")
    news_image = Image.open(image_path).convert("RGB")

    color_enhancer = ImageEnhance.Color(news_image)
    news_image = color_enhancer.enhance(1.5)

    contrast_enhancer = ImageEnhance.Contrast(news_image)
    news_image = contrast_enhancer.enhance(1.5)

    brightness_enhancer = ImageEnhance.Brightness(news_image)
    news_image = brightness_enhancer.enhance(1)

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

    title_length = len(title)

    if title_length <= 40:
        font_size = 58
    elif title_length <= 60:
        font_size = 49
    elif title_length <= 90:
        font_size = 35
    else:
        font_size = 30

    font = ImageFont.truetype(FONT_PATH, font_size)

    wrapped_text = fit_text_dynamically(title.upper(), font, max_text_width, draw)

    while any(draw.textbbox((0, 0), line, font=font)[2] > max_text_width for line in wrapped_text):
        font_size -= 2
        font = ImageFont.truetype(FONT_PATH, font_size)
        wrapped_text = fit_text_dynamically(title.upper(), font, max_text_width, draw)

    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    total_text_height = len(wrapped_text) * line_height
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
    print(f"✅ Создано изображение: {output_path} (Шрифт: {font_size}px, Строк: {len(wrapped_text)})")
