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
            return True
        return False
    except Exception:
        return False

def load_processed_articles(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def save_processed_articles(file_path, articles):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(articles, file, ensure_ascii=False, indent=4)

def add_processed_article(file_path, title, url, status="processed"):
    articles = load_processed_articles(file_path)
    articles.append({
        "title": title,
        "url": url,
        "status": status
    })
    save_processed_articles(file_path, articles)
