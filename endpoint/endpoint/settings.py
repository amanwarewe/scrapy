BOT_NAME = "reddit_scraper"

SPIDER_MODULES = ["endpoint.spiders"]
NEWSPIDER_MODULE = "endpoint.spiders"

ROBOTSTXT_OBEY = False

# DOWNLOAD_DELAY = 2

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "reddit-keyword-research-bot/1.0"
}

# posts/settings.py

FEEDS = {
    "posts/spiders/output/%(name)s_%(time)s.json": {
        "format": "json",
        "encoding": "utf8",
        "indent": 4,
    },
}

DOWNLOAD_DELAY = 2
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
