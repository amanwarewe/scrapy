import scrapy

class RedditPostItem(scrapy.Item):
    keyword = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    subreddit = scrapy.Field()
    author = scrapy.Field()
    score = scrapy.Field()
    num_comments = scrapy.Field()
    created_utc = scrapy.Field()
    url = scrapy.Field()
    permalink = scrapy.Field()
    post_type = scrapy.Field()
    top_comments = scrapy.Field()
