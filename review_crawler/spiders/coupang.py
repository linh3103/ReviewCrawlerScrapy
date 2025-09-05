import scrapy
import json
from datetime import datetime
from review_crawler.items import ReviewItem
from scrapy.exceptions import CloseSpider

class CoupangReviewsSpider(scrapy.Spider):
    name = 'coupang_reviews'

    chrome_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Ch-Ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
    }

    def __init__(self, product_id=None, *args, **kwargs):
        super(CoupangReviewsSpider, self).__init__(*args, **kwargs)

        if not product_id:
            raise ValueError("Bạn phải cung cấp product_id bằng cờ -a. Ví dụ: -a product_id=123456")
        
        self.product_id = product_id
        self.base_api_url = f'https://www.coupang.com/next-api/review?productId={self.product_id}&page={{page_num}}&size=10&sortBy=DATE_DESC'
        self.chrome_headers['Referer'] = f'https://www.coupang.com/vp/products/{self.product_id}'
        self.total_reviews = 0
        self.limit_reviews = 50

    def start_requests(self):
        first_page_url = self.base_api_url.format(page_num=1)
        
        yield scrapy.Request(
            url=first_page_url,
            headers=self.chrome_headers,
            callback=self.parse,
            meta={
                'playwright': True,
                'current_page': 1
            }
        )

    def parse(self, response):
        current_page = response.meta['current_page']
        self.log(f'Đang xử lý trang số: {current_page}')

        try:
            json_string = response.css('pre::text').get()

            if not json_string:
                self.log(f"Lỗi: Không tìm thấy thẻ <pre> chứa JSON trên trang {current_page}.")
                self.log(f"Nội dung response: {response.text[:500]}") # In ra một đoạn để debug
                return

            data = json.loads(json_string)

        except json.JSONDecodeError:
            self.log(f'Lỗi: Nội dung bên trong thẻ <pre> không phải là JSON hợp lệ trên trang {current_page}.')
            return
        
        reviews = data.get('rData', {}).get('paging', {}).get('contents', [])

        if not reviews:
            self.log(f'Không tìm thấy review nào trên trang {current_page}.')
            return

        for review in reviews:

            if self.total_reviews >= self.limit_reviews:
                raise CloseSpider('Đã đạt đến giới hạn số review cần crawl.')

            review_timestamp_ms = review.get('reviewAt')
            review_date = None
            if review_timestamp_ms:
                review_date = datetime.fromtimestamp(review_timestamp_ms / 1000).strftime('%Y.%m.%d')

            review_item = ReviewItem()
            review_item['date'] = review_date
            review_item['rating'] = review.get('rating')
            review_item['item_name'] = review.get('itemName')

            yield review_item
            self.total_reviews += 1

        paging_info = data.get('rData', {}).get('paging', {})
        total_page = paging_info.get('totalPage')
        current_page = response.meta['current_page']

        if self.total_reviews < self.limit_reviews:
            next_page = current_page + 1
            self.log(f'Đang chuẩn bị crawl trang tiếp theo: {next_page}')
            
            next_page_url = self.base_api_url.format(page_num=next_page)
            
            yield scrapy.Request(
                url=next_page_url,
                headers=self.chrome_headers,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'current_page': next_page
                }
            )
        else:
            self.log('Đã crawl đến trang cuối cùng theo dữ liệu từ API.')