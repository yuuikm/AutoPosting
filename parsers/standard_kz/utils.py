import json
import os
import requests

def download_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"✅ Изображение загружено: {filename}")
            return True
        else:
            print(f"❌ Ошибка загрузки {url}: статус {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при скачивании {url}: {e}")
        return False

def load_processed_articles(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                return []
        except json.JSONDecodeError:
            return []

def save_processed_articles(file_path, articles):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(articles, file, ensure_ascii=False, indent=4)

def add_processed_article(file_path, title, url, status="processed"):
    articles = load_processed_articles(file_path)
    if not isinstance(articles, list):
        articles = []

    articles.append({
        "title": title,
        "url": url,
        "status": status
    })

    save_processed_articles(file_path, articles)

