# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReviewItem(scrapy.Item):
    date = scrapy.Field()
    rating = scrapy.Field()
    item_name = scrapy.Field()

class OhouseReviewItem(scrapy.Item):
    date = scrapy.Field()
    rating = scrapy.Field()
    item_name = scrapy.Field()
    is_purchased = scrapy.Field()

class ReviewWithOptionItem(scrapy.Item):
    date = scrapy.Field()
    rating = scrapy.Field()
    options = scrapy.Field()