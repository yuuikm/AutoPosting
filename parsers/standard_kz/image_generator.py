from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from config import TEMPLATE_PATH, FONT_PATH

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

def create_social_media_image(title, image_path, image_author, output_path):
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
    max_text_width = 983 - 17
    text_x = 17
    text_y = 703
    text_bottom = 950
    max_text_height = text_bottom - text_y

    font_size = 80
    line_spacing = 15
    font = ImageFont.truetype(FONT_PATH, font_size)

    wrapped_text = wrap_text(draw, title.upper(), font, max_text_width)

    while True:
        lines = wrapped_text.split("\n")
        total_text_height = len(lines) * font_size + (len(lines) - 1) * line_spacing

        if total_text_height <= max_text_height or font_size <= 30:
            break

        font_size -= 2
        font = ImageFont.truetype(FONT_PATH, font_size)
        wrapped_text = wrap_text(draw, title.upper(), font, max_text_width)

    text_start_y = text_y + (max_text_height - total_text_height) // 2
    current_y = text_start_y

    for line in wrapped_text.split("\n"):
        text_width = draw.textbbox((0, 0), line, font=font)[2]
        centered_x = text_x + (max_text_width - text_width) // 2
        draw.text((centered_x, current_y), line, font=font, fill="white")
        current_y += font_size + line_spacing

    author_font = ImageFont.truetype(FONT_PATH, 15)
    author_x = 17
    author_y = 975
    draw.text((author_x, author_y), image_author.upper(), font=author_font, fill=(255, 255, 255, 80))

    final_image.save(output_path)
    print(f"✅ Создано изображение: {output_path}")
