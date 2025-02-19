import argparse
from parsers.exclusive_kz import scraper as exclusive_scraper

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run exclusive_kz scraper')
    parser.add_argument('--parser', choices=['exclusive_kz'], default='exclusive_kz', help='Choose which parser to run')
    args = parser.parse_args()

    if args.parser == 'exclusive_kz':
        exclusive_scraper.scrape_page()
