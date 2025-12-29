


import scrapy
from endpoint.items import RedditPostItem
from datetime import datetime
import os

class RecentPostsSpider(scrapy.Spider):
    name = "recent_posts"

    # --- Custom settings for automatic JSON output ---
    custom_settings = {
        "FEEDS": {
            # This path will save each JSON with keyword and timestamp
            "posts/spiders/output/%(name)s_%(keyword)s_%(time)s.json": {
                "format": "json",
                "encoding": "utf8",
                "indent": 4,
            }
        }
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword
        self.count = 0            # Number of posts fetched
        self.max_posts = 15       # Fetch 15 posts

        # Make sure output folder exists
        self.output_dir = os.path.join(os.getcwd(), "posts", "spiders", "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_richtext(self, richtext):
        if not richtext:
            return None

        text_parts = []

        for block in richtext.get("document", []):
            # New Reddit format
            if "c" in block:
                for elem in block["c"]:
                    if elem.get("e") == "text":
                        text_parts.append(elem.get("t"))

            # Old Reddit format fallback
            if block.get("e") == "text":
                text_parts.append(block.get("t"))

        text = "\n".join(text_parts).strip()
        return text if text else None


    def start_requests(self):
        url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=new&limit=15"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/118.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        data = response.json()
        posts = data["data"]["children"]
        after = data["data"].get("after")  # Pagination token

        for post in posts:
            if self.count >= self.max_posts:
                return  # Stop after 15 posts
            p = post["data"]
            body = p.get("selftext")

            if not body:
                body = self.extract_richtext(p.get("richtext_json"))
            yield RedditPostItem(
                keyword=self.keyword,
                title=p.get("title"),
                body=body,
                subreddit=p.get("subreddit"),
                author=p.get("author"),
                score=p.get("score"),
                num_comments=p.get("num_comments"),
                created_utc=p.get("created_utc"),
                url=p.get("url"),
                permalink="https://reddit.com" + p.get("permalink"),
                post_type="recent"
            )
            self.count += 1

        # Continue pagination if needed
        if after and self.count < self.max_posts:
            next_url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=new&limit=25&after={after}"
            yield scrapy.Request(
                next_url, 
                callback=self.parse,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            )
