import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGET_DATE = datetime.now().strftime("%d.%m.%Y")
TEMPLATE_PATH = os.path.join(BASE_DIR, "data", "templates", "standard-post.png")
IMAGE_DIR = os.path.join(BASE_DIR, "data", "standard_scraped_images")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "standard_generated_posts")
PROCESSED_FILE = os.path.join(BASE_DIR, "data", "standard_processed.json")
PUBLIC_URL = "https://img.odyx.cc"

EMOJI_PATH = os.path.join(BASE_DIR, "data", "emoji_rules.json")
HASHTAGS_PATH = os.path.join(BASE_DIR, "data", "hashtags.json")
FONT_PATH = os.path.join(BASE_DIR, "data", "fonts", "Montserrat-Bold.ttf")