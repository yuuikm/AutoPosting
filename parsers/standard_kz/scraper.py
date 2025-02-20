import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
from config import BASE_URLS, today_date
import time

def get_dynamic_html(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service("msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)

    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    driver.quit()
    return html

def scrape_posts():
    posts = []

    for base_url in BASE_URLS:
        print(f"Загружаем страницу: {base_url}")
        html = get_dynamic_html(base_url)
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select("table.table-striped tbody tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            post_datetime = cols[0].text.strip()
            post_date, post_time = post_datetime.split(" ")
            if post_date != today_date:
                continue

            title_tag = cols[1].find("a")
            if not title_tag:
                continue

            title = title_tag.text.strip()
            post_url = title_tag["href"].strip()

            post_response = requests.get(post_url)
            post_soup = BeautifulSoup(post_response.text, "html.parser")

            image_tag = post_soup.select_one("div.entry__img-holder img")
            author_tag = post_soup.select_one("div.entry__img-holder span")
            article_tag = post_soup.select_one("div.entry__article")

            image_author = author_tag.text.strip() if author_tag else "Источник: Standard.kz"
            text_content = "\n".join([p.text.strip() for p in article_tag.find_all("p")]) if article_tag else ""

            image_url = "https://standard.kz" + image_tag["src"].strip()

            posts.append((post_datetime, title, post_url, image_url, image_author, text_content))

    posts.sort(reverse=True, key=lambda x: x[0])
    return posts
