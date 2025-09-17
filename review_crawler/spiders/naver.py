# Đảm bảo đoạn code sửa lỗi Windows vẫn ở đầu file
import json
import scrapy
from review_crawler.items import ReviewItem
from review_crawler.enums.spider_enum import SpiderName
from review_crawler.utils.constants import NAVER_STORES

class NaverSeleniumSpider(scrapy.Spider):
    name = SpiderName.NAVER_SPIDER.value

    middleware_flags = ["use_selenium"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "review_crawler.middlewares.NaverSeleniumMiddleware": 543,
        }
    }

    def __init__(self, brand_name=None, product_id=None, *args, **kwargs):
        super(NaverSeleniumSpider, self).__init__(*args, **kwargs)
        if not brand_name and product_id:
            raise ValueError("Vui lòng cung cấp brand và mã sản phẩm...")
        
        self.brand_name = brand_name
        self.product_id = product_id
        self.limit_reviews = 100
        self.report_folder_name = "Naver"
    
    def start_requests(self):
        brand_url = NAVER_STORES.get(self.brand_name)
        target_url = f"{brand_url}{self.product_id}"

        yield scrapy.Request(
            url=target_url,
            callback=self.parse,
            meta={
                "use_selenium": True,
                "current_page": 1,
                "collected_reviews_count": 0,
            }
        )
                
    def parse(self, response):
        REVIEW_LIST_SELECTOR = "li[data-shp-area='revlist.review']"
        reviews_in_page = response.css(REVIEW_LIST_SELECTOR)

        collected_reviews_count = response.meta.get("collected_reviews_count")
        current_page = response.meta.get("current_page")

        if not reviews_in_page:
            self.logger.info("No more reviews found. Stopping pagination.")
            return

        for review in reviews_in_page:
            review_date_str = review.css("div > div > div > div strong+span::text").get()
            review_date = None
            if review_date_str:
                review_date = review_date_str.rstrip(".")

            if not review_date:
                continue

            rating = review.css("div > div > div > div > em::text").get()

            full_option_review = review.xpath('string(.//div[strong and span]/following-sibling::*[1])').get()
            item_name = full_option_review.strip().split('\n')[0] if full_option_review else None

            review_item = ReviewItem()
            review_item["date"] = review_date
            review_item["rating"] = rating
            review_item["item_name"] = item_name

            yield review_item
            collected_reviews_count += 1

            if collected_reviews_count >= self.limit_reviews:
                return

        if collected_reviews_count < self.limit_reviews:
            next_page = current_page + 1
            yield scrapy.Request(
                url=response.request.url,
                callback=self.parse,
                meta={
                    "use_selenium":True,
                    "click_next_page": True,
                    "current_page": next_page,
                    "collected_reviews_count": collected_reviews_count
                },
                dont_filter=True
            )




