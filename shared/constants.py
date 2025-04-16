import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUSIVE_TARGET_DATE = datetime.today().day
EXCLUSIVE_TEMPLATE_PATH = os.path.join(BASE_DIR, "data", "templates", "exclusive-post.png")
EXCLUSIVE_IMAGE_DIR = os.path.join(BASE_DIR, "data", "exclusive_scraped_images")
EXCLUSIVE_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "exclusive_generated_posts")
EXCLUSIVE_PROCESSED_FILE = os.path.join(BASE_DIR, "data", "exclusive_processed.json")

STANDARD_TARGET_DATE = datetime.now().strftime("%d.%m.%Y")
STANDARD_TEMPLATE_PATH = os.path.join(BASE_DIR, "data", "templates", "standard-post.png")
STANDARD_IMAGE_DIR = os.path.join(BASE_DIR, "data", "standard_scraped_images")
STANDARD_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "standard_generated_posts")
STANDARD_PROCESSED_FILE = os.path.join(BASE_DIR, "data", "standard_processed.json")
STANDARD_PUBLIC_URL = "https://refreshme.cloud/standard"

EMOJI_PATH = os.path.join(BASE_DIR, "data", "emoji_rules.json")
HASHTAGS_PATH = os.path.join(BASE_DIR, "data", "hashtags.json")
FONT_PATH = os.path.join(BASE_DIR, "data", "fonts", "Montserrat-Bold.ttf")