# Đảm bảo đoạn code sửa lỗi Windows vẫn ở đầu file
import json
import scrapy
from review_crawler.items import ReviewItem

class NaverSeleniumSpider(scrapy.Spider):
    name = 'naver_reviews'
    middleware_flags = ["use_selenium"]


    NAVER_STORES = {
        "바자르": "https://brand.naver.com/bazaar/products/",
        "라뽐므": "https://brand.naver.com/lapomme/products/",
        "쁘리엘르": "https://brand.naver.com/prielle/products/",
        "마틸라": "https://brand.naver.com/maatila/products/",
        "그래이불": "https://brand.naver.com/yesbedding/products/",
        "믹스앤매치": "https://brand.naver.com/mixandmatch/products/",
        "누비지오": "https://brand.naver.com/nubizio/products/",
        "데코뷰": "https://brand.naver.com/decoview/products/",
        "깃든": "https://brand.naver.com/gitden/products/",
        "스타일링홈": "https://brand.naver.com/styhome/products/",
        "아망떼": "https://brand.naver.com/amante/products/",
        "호무로": "https://brand.naver.com/homuro/products/",
        "헬로우슬립": "https://brand.naver.com/hellosleep/products/",
        "오넬로이": "https://smartstore.naver.com/oneloi/products/",
        "플로라": "https://brand.naver.com/flora/products/",
        "르올": "https://smartstore.naver.com/mewansungmall/products/",
        "에이트룸": "https://brand.naver.com/8room/products/",
        "베이직톤": "https://brand.naver.com/basictone/products/",
        "아토앤알로": "https://brand.naver.com/beddingnara/products/",
        "바숨": "https://brand.naver.com/busum/products/",
        "올리비아데코": "https://brand.naver.com/oliviadeco/products/",
        "코지네스트": "https://brand.naver.com/cozynest/products/",
        "메종오트몬드": "https://smartstore.naver.com/hautemonde/products/",
        "바운티풀": "https://brand.naver.com/bountiful/products/",
        "도아드림": "https://brand.naver.com/doadream_goose/products/",
        "CROWN GOOSE": "https://brand.naver.com/crowngoose/products/"
    }

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "review_crawler.middlewares.NaverSeleniumMiddleware": 543,
        }
    }

    def __init__(self, brands_products=None, *args, **kwargs):
        super(NaverSeleniumSpider, self).__init__(*args, **kwargs)
        # if not brands_products:
        #     raise ValueError("Vui lòng cung cấp product_id...")
        
        json_str = '{"아토앤알로": [226613999,2007829417]}'
        self.brands_products = json.loads(json_str)
        self.limit_reviews = 100
    
    def start_requests(self):
        for brand_name, product_ids in self.brands_products.items():
            brand_url = self.NAVER_STORES.get(brand_name)
            if not brand_url:
                continue

            for product_id in product_ids:
                self.product_id = product_id
                target_url = f"{brand_url}{product_id}"

                yield scrapy.Request(
                    url=target_url,
                    callback=self.parse,
                    meta={
                        "use_selenium": True,
                        "current_page": 1,
                        "collected_reviews_count": 0,
                        "brand_name": brand_name,
                        "product_id": product_id
                    }
                )
        
    def parse(self, response):
        REVIEW_LIST_SELECTOR = "li[data-shp-area='revlist.review']"
        reviews_in_page = response.css(REVIEW_LIST_SELECTOR)

        collected_reviews_count = response.meta.get("collected_reviews_count")
        current_page = response.meta.get("current_page")
        brand_name = response.meta.get("brand_name")
        product_id = response.meta.get("product_id")

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
                break

        if  collected_reviews_count < self.limit_reviews:
            next_page = current_page + 1
            yield scrapy.Request(
                url=response.request.url,
                callback=self.parse,
                meta={
                    "use_selenium":True,
                    "click_next_page": True,
                    "current_page": next_page,
                    "collected_reviews_count": collected_reviews_count,
                    "brand_name": brand_name,
                    "product_id": product_id
                },
                dont_filter=True
            )




