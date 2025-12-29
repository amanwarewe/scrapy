


import scrapy
from endpoint.items import RedditPostItem
import os

class GoogleRankedSpider(scrapy.Spider):
    name = "google_ranked"

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
        if not keyword:
            raise ValueError("You must provide a keyword!")
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
    # Start requests
    # -----------------------------
    def start_requests(self):
        url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=relevance&limit=50"
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

        for post in posts:
            if self.count >= self.max_posts:
                return

            p = post["data"]

            if p.get("score", 0) > 1000 and p.get("num_comments", 0) >= 250:
                # Extract post text (body)
                body = p.get("selftext")
                if not body:
                    body = self.extract_richtext(p.get("richtext_json"))

                post_permalink = "https://www.reddit.com" + p.get("permalink") + ".json"

                # Fetch comments for this post
                yield scrapy.Request(
                    post_permalink,
                    callback=self.parse_comments,
                    headers=response.request.headers,
                    cb_kwargs={"post_data": p, "body": body}
                )
                self.count += 1

        if after and self.count < self.max_posts:
            next_url = (
                f"https://www.reddit.com/search.json?"
                f"q={self.keyword}&sort=relevance&limit=50&after={after}"
            )
            yield scrapy.Request(next_url, headers=response.request.headers, callback=self.parse)

    # -----------------------------
    # Parse comments
    # -----------------------------
    def parse_comments(self, response, post_data, body):
        data = response.json()
        comments = []

        # Reddit returns comments in the second element
        for c in data[1]["data"]["children"]:
            if c["kind"] != "t1":  # Ensure it's a comment
                continue
            comment_data = c["data"]
            comments.append({
                "author": comment_data.get("author"),
                "body": comment_data.get("body"),
                "score": comment_data.get("score")
            })

        # Sort comments by score descending and take top 10
        top_comments = sorted(comments, key=lambda x: x["score"], reverse=True)[:10]

        yield RedditPostItem(
            keyword=self.keyword,
            title=post_data.get("title"),
            body=body,
            subreddit=post_data.get("subreddit"),
            author=post_data.get("author"),
            score=post_data.get("score"),
            num_comments=post_data.get("num_comments"),
            created_utc=post_data.get("created_utc"),
            url=post_data.get("url"),
            permalink="https://reddit.com" + post_data.get("permalink"),
            post_type="google_ranked",
            top_comments=top_comments
        )

