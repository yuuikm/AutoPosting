import os
import requests
import json

def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        print(f"❌ Не удалось скачать изображение: {url}")

def load_processed_articles(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def save_processed_articles(filepath, processed_articles):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(processed_articles, file, ensure_ascii=False, indent=4)

def add_processed_article(filepath, article_title, article_url):
    processed_articles = load_processed_articles(filepath)
    processed_articles[article_title] = {
        "url": article_url,
        "status": "published"
    }
    save_processed_articles(filepath, processed_articles)

