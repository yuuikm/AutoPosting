from datetime import datetime
from babel.dates import format_date

EXCLUSIVE_TARGET_DATE = format_date(datetime.today(), format="d MMMM, yyyy", locale="ru")
EXCLUSIVE_TEMPLATE_PATH = "data/templates/exclusive-post.png"
EXCLUSIVE_IMAGE_DIR = "data/exclusive_scraped_images"
EXCLUSIVE_OUTPUT_DIR = "data/exclusive_generated_posts"



FONT_PATH = "data/fonts/Montserrat-Bold.ttf"
