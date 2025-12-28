# import scrapy
# from posts.items import RedditPostItem

# class HighEngagementSpider(scrapy.Spider):
#     name = "high_engagement"  # Must match exactly!
    
#     def __init__(self, keyword=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.keyword = keyword

#     def start_requests(self):
#         url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=top&t=month"
#         yield scrapy.Request(url, callback=self.parse)

#     def parse(self, response):
#         for post in response.json()["data"]["children"]:
#             p = post["data"]
#             yield RedditPostItem(
#                 keyword=self.keyword,
#                 title=p["title"],
#                 subreddit=p["subreddit"],
#                 author=p["author"],
#                 score=p["score"],
#                 num_comments=p["num_comments"],
#                 created_utc=p["created_utc"],
#                 url=p["url"],
#                 permalink="https://reddit.com" + p["permalink"],
#                 post_type="high_engagement"
#             )


# import scrapy
# from posts.items import RedditPostItem

# class HighEngagementSpider(scrapy.Spider):
#     name = "high_engagement"

#     def __init__(self, keyword=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.keyword = keyword
#         self.count = 0  # Count of posts fetched
#         self.max_posts = 15  # Number of posts you want

#     # def start_requests(self):
#     #     url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=top&t=month&limit=25"
#     #     yield scrapy.Request(url, callback=self.parse)
#     def start_requests(self):
#         url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=new&limit=15"
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                         "AppleWebKit/537.36 (KHTML, like Gecko) "
#                         "Chrome/118.0.0.0 Safari/537.36",
#             "Accept": "application/json",
#             "Accept-Language": "en-US,en;q=0.9",
#         }
#         yield scrapy.Request(url, headers=headers, callback=self.parse)


#     def parse(self, response):
#         data = response.json()
#         posts = data["data"]["children"]
#         after = data["data"].get("after")  # Pagination token

#         for post in posts:
#             if self.count >= self.max_posts:
#                 return  # Stop after reaching max_posts
#             p = post["data"]
#             yield RedditPostItem(
#                 keyword=self.keyword,
#                 title=p["title"],
#                 subreddit=p["subreddit"],
#                 author=p["author"],
#                 score=p["score"],
#                 num_comments=p["num_comments"],
#                 created_utc=p["created_utc"],
#                 url=p["url"],
#                 permalink="https://reddit.com" + p["permalink"],
#                 post_type="high_engagement"
#             )
#             self.count += 1

#         # Continue pagination if we haven't reached 15 posts
#         if after and self.count < self.max_posts:
#             next_url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=top&t=month&limit=25&after={after}"
#             yield scrapy.Request(next_url, callback=self.parse)



# import scrapy
# from endpoint.items import RedditPostItem
# from datetime import datetime
# import os

# class HighEngagementSpider(scrapy.Spider):
#     name = "high_engagement"

#     # --- Custom settings for automatic JSON output ---
#     custom_settings = {
#         "FEEDS": {
#             "posts/spiders/output/%(name)s_%(keyword)s_%(time)s.json": {
#                 "format": "json",
#                 "encoding": "utf8",
#                 "indent": 4,
#             }
#         }
#     }

#     def __init__(self, keyword=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.keyword = keyword
#         self.count = 0
#         self.max_posts = 15

#         # Ensure output folder exists
#         self.output_dir = os.path.join(os.getcwd(), "posts", "spiders", "output")
#         os.makedirs(self.output_dir, exist_ok=True)

#     def start_requests(self):
#         # Fetch more posts initially to filter later
#         url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=new&limit=50"
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                           "AppleWebKit/537.36 (KHTML, like Gecko) "
#                           "Chrome/118.0.0.0 Safari/537.36",
#             "Accept": "application/json",
#             "Accept-Language": "en-US,en;q=0.9",
#         }
#         yield scrapy.Request(url, headers=headers, callback=self.parse)

#     def parse(self, response):
#         data = response.json()
#         posts = data["data"]["children"]
#         after = data["data"].get("after")

#         # Sort posts by both score and number of comments (descending)
#         sorted_posts = sorted(
#             posts,
#             key=lambda x: (x["data"]["score"], x["data"]["num_comments"]),
#             reverse=True
#         )

#         for post in sorted_posts:
#             if self.count >= self.max_posts:
#                 return
#             p = post["data"]

#             # Filter out posts with very low engagement
#             if p["score"] > 80 and p["num_comments"] > 10:  # adjust thresholds if needed
#                 yield RedditPostItem(
#                     keyword=self.keyword,
#                     title=p.get("title"),
#                     body = p.get("selftext") or None,
#                     subreddit=p.get("subreddit"),
#                     author=p.get("author"),
#                     score=p.get("score"),
#                     num_comments=p.get("num_comments"),
#                     created_utc=p.get("created_utc"),
#                     url=p.get("url"),
#                     permalink="https://reddit.com" + p.get("permalink"),
#                     post_type="high_engagement"
#                 )
#                 self.count += 1

#         # Continue pagination if we haven't reached max_posts
#         if after and self.count < self.max_posts:
#             next_url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=new&limit=50&after={after}"
#             yield scrapy.Request(next_url, headers=response.request.headers, callback=self.parse)



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
