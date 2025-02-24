import requests
from shared.config import EXCLUSIVE_INSTAGRAM_ACCESS_TOKEN, EXCLUSIVE_INSTAGRAM_ACCOUNT_ID

def publish_to_instagram(image_url, caption):
    try:
        upload_url = f"https://graph.facebook.com/v17.0/{EXCLUSIVE_INSTAGRAM_ACCOUNT_ID}/media"

        data = {
            'image_url': image_url,
            'caption': caption,
            'access_token': EXCLUSIVE_INSTAGRAM_ACCESS_TOKEN
        }

        response = requests.post(upload_url, data=data)

        if response.status_code != 200:
            print(f"❌ Ошибка загрузки изображения: {response.text}")
            return

        media_id = response.json().get('id')
        print(f"✅ Медиа загружено. Media ID: {media_id}")

        publish_url = f"https://graph.facebook.com/v17.0/{EXCLUSIVE_INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_data = {
            'creation_id': media_id,
            'access_token': EXCLUSIVE_INSTAGRAM_ACCESS_TOKEN
        }

        publish_response = requests.post(publish_url, data=publish_data)

        if publish_response.status_code == 200:
            print("🎉 Публикация успешно создана в Instagram!")
        else:
            print(f"❌ Ошибка публикации в Instagram: {publish_response.text}")

    except Exception as e:
        print(f"⚠️ Ошибка при публикации в Instagram: {e}")
