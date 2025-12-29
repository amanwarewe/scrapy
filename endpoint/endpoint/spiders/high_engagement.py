

import scrapy
from endpoint.items import RedditPostItem
import os


class HighEngagementSpider(scrapy.Spider):
    name = "high_engagement"

    custom_settings = {
        "FEEDS": {
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
        self.count = 0
        self.max_posts = 15

        self.output_dir = os.path.join(os.getcwd(), "posts", "spiders", "output")
        os.makedirs(self.output_dir, exist_ok=True)

    # -----------------------------
    # Helper: extract rich text
    # -----------------------------
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

    # -----------------------------
    # Requests
    # -----------------------------
    def start_requests(self):
        url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=new&limit=50"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        yield scrapy.Request(url, headers=headers, callback=self.parse)

    # -----------------------------
    # Parse search results
    # -----------------------------
    def parse(self, response):
        data = response.json()
        posts = data["data"]["children"]
        after = data["data"].get("after")

        sorted_posts = sorted(
            posts,
            key=lambda x: (x["data"]["score"], x["data"]["num_comments"]),
            reverse=True
        )

        for post in sorted_posts:
            if self.count >= self.max_posts:
                return

            p = post["data"]

            if p.get("score", 0) > 80 and p.get("num_comments", 0) > 10:

                # -----------------------------
                # Extract post text correctly
                # -----------------------------
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
                    post_type="high_engagement"
                )

                self.count += 1

        if after and self.count < self.max_posts:
            next_url = (
                f"https://www.reddit.com/search.json?"
                f"q={self.keyword}&sort=new&limit=50&after={after}"
            )
            yield scrapy.Request(
                next_url,
                headers=response.request.headers,
                callback=self.parse
            )
