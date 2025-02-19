import os
import requests

def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        print(f"❌ Не удалось скачать изображение: {url}")

def load_processed_articles(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file.readlines())

def save_processed_articles(filename, processed_articles):
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(f"{article}\n" for article in processed_articles)
