from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
from shared.config import STANDARD_INSTAGRAM_USERNAME, STANDARD_INSTAGRAM_PASSWORD

def post_to_instagram(image_path: object, caption: object) -> object:
    cl = Client()

    try:
        cl.login(STANDARD_INSTAGRAM_USERNAME, STANDARD_INSTAGRAM_PASSWORD)
    except TwoFactorRequired as e:
        verification_code = input("Введите код из Instagram: ")
        cl.complete_two_factor_login(verification_code)

    cl.photo_upload(
        path=image_path,
        caption=caption
    )

    print("✅ Публикация успешно добавлена в Instagram")
