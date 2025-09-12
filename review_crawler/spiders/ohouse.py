import scrapy
from review_crawler.items import OhouseReviewItem
from scrapy.exceptions import CloseSpider

class OhouseSpider(scrapy.Spider):
    name = "ohouse_reviews"

    chrome_headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Sec-Ch-Ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    def __init__(self, product_id = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if product_id:

            self.total_reviews = 0
            self.limit_reviews = 100

            self.product_id = product_id
            self.base_url = f"https://ohou.se/production_reviews.json?production_id={self.product_id}&page={{page}}&order=recent"
            self.chrome_headers['Referer'] = f"https://ohou.se/productions/{self.product_id}/selling?affect_id=1&affect_type=StoreSearchResult"

        else:
            raise ValueError("Please provide product_id using -a flag, e.g., -a product_id=123456")

    def start_requests(self):
        yield scrapy.Request(
                url=self.base_url.format(page=1),
                headers=self.chrome_headers,
                callback=self.parse_reviews,
                meta={'current_page': 1}
            )
            
    def parse_reviews(self, response):

        current_page = response.meta['current_page']

        data = response.json()
        reviews = data.get("reviews", [])
        for review in reviews:

            if self.total_reviews >= self.limit_reviews:
                raise CloseSpider('Reached the limit of reviews to scrape.')

            review_item = OhouseReviewItem()
            review_item['date'] = review.get("created_at")

            review_info = review.get('review', {})
            review_item['rating'] = review_info.get('star_avg')

            product_info = review.get('production_information', {})
            review_item['item_name'] = product_info.get('explain')
            review_item['is_purchased'] = product_info.get('is_purchased', True)

            yield review_item
            self.total_reviews += 1

        if self.total_reviews < self.limit_reviews:
            next_page = current_page + 1
            next_page_url = self.base_url.format(page=next_page)
            yield scrapy.Request(
                url=next_page_url,
                headers=self.chrome_headers,
                callback=self.parse_reviews,
                meta={'current_page': next_page}
            )

        
