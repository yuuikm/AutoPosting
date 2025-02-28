from parsers.exclusive_kz import scraper as exclusive_scraper
from parsers.standard_kz import scraper as standard_scraper

if __name__ == '__main__':
    print("🔍 Запускаем скрапер exclusive_kz...")
    exclusive_scraper.scrape_page()

    print("\n🔍 Запускаем скрапер standard_kz...")
    standard_scraper.scrape_posts()

    print("\n✅ Оба скрапера успешно завершили работу.")
