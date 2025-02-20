from datetime import datetime

EXCLUSIVE_TARGET_DATE = datetime.today().day
EXCLUSIVE_TEMPLATE_PATH = "data/templates/exclusive-post.png"
EXCLUSIVE_IMAGE_DIR = "data/exclusive_scraped_images"
EXCLUSIVE_OUTPUT_DIR = "data/exclusive_generated_posts"

STANDARD_TARGET_DATE = datetime.now().strftime("%d.%m.%Y")
STANDARD_TEMPLATE_PATH = "data/templates/standard-post.png"
STANDARD_IMAGE_DIR = "data/standard_scraped_images"
STANDARD_OUTPUT_DIR = "data/standard_generated_posts"

EMOJI_PATH = "data/emoji_rules.json"
FONT_PATH = "data/fonts/Montserrat-Bold.ttf"
