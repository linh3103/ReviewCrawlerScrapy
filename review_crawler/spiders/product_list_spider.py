import scrapy
import json

class ProductListSpider(scrapy.Spider):
    name = "product_list"

    PROJECT_NAME = "review_crawler"
    SCRAPYD_URL = "http://localhost:6800"

    def __init__(self, *args, **kwargs):
        super(ProductListSpider, self).__init__(*args, **kwargs)

        self.brands_products = {
            "Ohou.se": [11246,345755],
            "Coupang": [6287221036,6674000351],
            "도아드림": [6099802980,8279484987]
        }

    def start_requests(self):
        self.logger.info("Dispatcher spider is starting...")
        yield scrapy.Request(url="http://quotes.toscrape.com/page/1/", 
                             callback=self.parse, 
                             dont_filter=True) 

    def parse(self, response):
        for brand_name, product_ids in self.brands_products.items():
            spider_name = self.get_spider_name_by_brand_name(brand_name)
            for product_id in product_ids:
                yield {
                        "action": "schedule_job",
                        "project_name": self.PROJECT_NAME,
                        "scrapyd_url": self.SCRAPYD_URL,
                        "spider_name": spider_name,
                        "brand_name": brand_name,
                        "product_id": product_id
                    }
                    
    def get_spider_name_by_brand_name(self, brand_name):
        match brand_name:
            case "Ohou.se": return "ohouse_reviews"
            case "Coupang": return "coupang_reviews"
            case _:         return "naver_reviews"
