# 📡 Web Parser & Social Media Publisher

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4B8BBE?style=for-the-badge&logo=beautifulsoup&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Telegram Bot](https://img.shields.io/badge/Telegram-BOT-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

---

## 📖 About the Project

This project is an **automated web parser** that scrapes news articles from two websites and **publishes them directly to social media platforms**. The system is designed to run smoothly and handle large volumes of data while ensuring content is delivered in the correct format for each platform.

The parser uses **Selenium** and **BeautifulSoup** for data scraping, and **Telegram Bot API** for publishing posts to Telegram channels. Future updates aim to extend its functionality across other major social networks.

---

## 🚀 Features

- ✅ **Automatic Web Scraping** — Collects news articles from two distinct websites.
- ✅ **Dynamic Content Filtering** — Publishes only relevant and up-to-date articles.
- ✅ **Custom Image Generation** — Generates social media-friendly images with titles and sources.
- ✅ **Auto-Publishing to Telegram** — Instantly posts news to specified Telegram channels.
- ✅ **Keyword-Based Emoji Tagging** — Adds emojis based on content topics (e.g., 🇰🇿, 💰, ⚽).
- ✅ **Duplicate Article Detection** — Ensures no duplicate posts are published.

---

## 🛠️ Planned Features

- 📘 **Publish to Facebook** — Expand content distribution to Facebook pages and groups.
- 📸 **Publish to Instagram** — Share articles as posts or stories with optimized visuals.
- 📝 **Log Management** — Store logs in dedicated log files instead of the console for better monitoring.
- ⚠️ **Error Notifications** — Send error alerts directly to an admin via Telegram bot.
- 🌐 **Deployment** — Fully deploy the project for continuous operation on a dedicated server.

---

## 💡 How It Works

1. **Web Scraping** — The parser scans selected websites for new articles.
2. **Content Filtering** — It filters articles based on the current date and relevance.
3. **Image Generation** — Generates shareable images using article titles and photos.
4. **Social Media Posting** — Automatically posts the content to Telegram.
5. **Emoji Tagging** — Assigns emojis based on keywords in the article.

---

## 📂 Technologies Used

- **Python 3.10+** — Core language for the project.
- **Selenium** — Handles dynamic content and JavaScript-rendered pages.
- **BeautifulSoup** — Parses HTML for efficient data extraction.
- **Telegram Bot API** — Publishes articles to Telegram channels.
- **Pillow (PIL)** — For generating custom images for posts.

---

## 💾 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt

3. **Configure .env file**  
   ```bash
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHANNEL_ID=your_telegram_channel_id
   USER_AGENT=your_browser_user_agent

4. **Run the project**  
   ```bash
   python main.py
