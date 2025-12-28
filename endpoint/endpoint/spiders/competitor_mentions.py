# import scrapy
# from endpoint.items import RedditPostItem
# import os

# # class CompetitorMentionSpider(scrapy.Spider):
# #     name = "competitor_mentions"

# #     custom_settings = {
# #         "FEEDS": {
# #             "posts/spiders/output/%(name)s_%(keyword)s_%(time)s.json": {
# #                 "format": "json",
# #                 "encoding": "utf8",
# #                 "indent": 4,
# #             }
# #         }
# #     }

# #     def __init__(self, keyword=None, *args, **kwargs):
# #         super().__init__(*args, **kwargs)
# #         if not keyword:
# #             raise ValueError("You must provide a keyword!")
# #         self.keyword = keyword
# #         self.count = 0
# #         self.max_posts = 15
# #         self.output_dir = os.path.join(os.getcwd(), "posts", "spiders", "output")
# #         os.makedirs(self.output_dir, exist_ok=True)

# #     def start_requests(self):
# #         url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=relevance&limit=50"
# #         headers = {
# #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
# #                           "AppleWebKit/537.36 (KHTML, like Gecko) "
# #                           "Chrome/118.0.0.0 Safari/537.36",
# #             "Accept": "application/json",
# #             "Accept-Language": "en-US,en;q=0.9",
# #         }
# #         yield scrapy.Request(url, headers=headers, callback=self.parse)
# class CompetitorMentionSpider(scrapy.Spider):
#     name = "competitor_mentions"

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def start_requests(self):
#         # parse the keyword from the URL query
#         parsed = response.url.split("?")[-1]
#         params = dict(x.split("=") for x in parsed.split("&") if "=" in x)
#         keyword = params.get("q") or params.get("keyword")
#         if not keyword:
#             return

#         url = f"https://www.reddit.com/search.json?q={keyword}&sort=relevance&limit=50"
#         yield scrapy.Request(url, headers=self.headers, callback=self.parse)


#     def parse(self, response):
#         data = response.json()
#         posts = data["data"]["children"]
#         after = data["data"].get("after")

#         for post in posts:
#             if self.count >= self.max_posts:
#                 return
#             p = post["data"]

#             # Only consider posts with score > 500 and num_comments >= 100
#             if p.get("score", 0) > 500 and p.get("num_comments", 0) >= 100:
#                 post_permalink = "https://www.reddit.com" + p.get("permalink") + ".json"
#                 yield scrapy.Request(
#                     post_permalink,
#                     callback=self.parse_comments,
#                     headers=response.request.headers,
#                     cb_kwargs={"post_data": p}
#                 )
#                 self.count += 1

#         if after and self.count < self.max_posts:
#             next_url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=relevance&limit=50&after={after}"
#             yield scrapy.Request(next_url, headers=response.request.headers, callback=self.parse)

#     def parse_comments(self, response, post_data):
#         data = response.json()
#         comments = []

#         # Reddit returns comments in the second element
#         for c in data[1]["data"]["children"]:
#             if c["kind"] != "t1":
#                 continue
#             comment_data = c["data"]
#             body = comment_data.get("body", "")
#             # Only include comments mentioning the keyword
#             if self.keyword.lower() in body.lower():
#                 comments.append({
#                     "author": comment_data.get("author"),
#                     "body": body,
#                     "score": comment_data.get("score")
#                 })

#         # Take top 5 comments by score
#         top_comments = sorted(comments, key=lambda x: x["score"], reverse=True)[:5]

#         yield RedditPostItem(
#             keyword=self.keyword,
#             title=post_data.get("title"),
#             subreddit=post_data.get("subreddit"),
#             author=post_data.get("author"),
#             score=post_data.get("score"),
#             num_comments=post_data.get("num_comments"),
#             created_utc=post_data.get("created_utc"),
#             url=post_data.get("url"),
#             permalink="https://reddit.com" + post_data.get("permalink"),
#             post_type="competitor_post",
#             top_comments=top_comments
#         )



import scrapy
from endpoint.items import RedditPostItem
import os

class CompetitorMentionSpider(scrapy.Spider):
    name = "competitor_mentions"

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
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/118.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.output_dir = os.path.join(os.getcwd(), "posts", "spiders", "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def start_requests(self):
        url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=relevance&limit=50"
        yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        data = response.json()
        posts = data["data"]["children"]
        after = data["data"].get("after")

        for post in posts:
            if self.count >= self.max_posts:
                return
            p = post["data"]

            # Filter high engagement posts if needed
            if p.get("score", 0) > 10 and p.get("num_comments", 0) > 5:
                post_permalink = "https://www.reddit.com" + p.get("permalink") + ".json"
                yield scrapy.Request(
                    post_permalink,
                    callback=self.parse_comments,
                    headers=self.headers,
                    cb_kwargs={"post_data": p}
                )
                self.count += 1

        if after and self.count < self.max_posts:
            next_url = f"https://www.reddit.com/search.json?q={self.keyword}&sort=relevance&limit=50&after={after}"
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse)

    def parse_comments(self, response, post_data):
        data = response.json()
        comments = []

        # Reddit returns comments in the second element of the post JSON
        if len(data) > 1 and "data" in data[1]:
            for c in data[1]["data"]["children"]:
                if c.get("kind") != "t1":
                    continue
                comment_data = c["data"]
                body = comment_data.get("body", "")
                if self.keyword.lower() in body.lower():
                    comments.append({
                        "author": comment_data.get("author"),
                        "body": body,
                        "score": comment_data.get("score")
                    })

        top_comments = sorted(comments, key=lambda x: x["score"], reverse=True)[:5]

        yield RedditPostItem(
            keyword=self.keyword,
            title=post_data.get("title"),
            body=post_data.get("selftext") or "",  # post text included here
            subreddit=post_data.get("subreddit"),
            author=post_data.get("author"),
            score=post_data.get("score"),
            num_comments=post_data.get("num_comments"),
            created_utc=post_data.get("created_utc"),
            url=post_data.get("url"),
            permalink="https://reddit.com" + post_data.get("permalink"),
            post_type="competitor_post",
            top_comments=top_comments
        )
