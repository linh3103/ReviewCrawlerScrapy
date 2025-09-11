import scrapy
import json
from datetime import datetime
from review_crawler.items import ReviewItem
from scrapy.exceptions import CloseSpider

class CoupangReviewsSpider(scrapy.Spider):
    name = 'coupang_reviews'

    # --- KHÔNG CẦN custom_settings CỦA PLAYWRIGHT NỮA ---
    # custom_settings = { ... }
    custom_settings = {
        # --- BƯỚC 1: GHI ĐÈ DOWNLOAD HANDLER ---
        # Ra lệnh cho spider NÀY và CHỈ spider này sử dụng scrapy-requests
        "DOWNLOAD_HANDLERS": {
            "http": "review_crawler.handlers.RequestsDownloadHandler",
            "https": "review_crawler.handlers.RequestsDownloadHandler",
        },
        
        # --- BƯỚC 2: GHI ĐÈ NGƯỢC LẠI REACTOR ---
        # Vì scrapy-requests hoạt động tốt nhất với reactor mặc định (asyncio),
        # chúng ta sẽ ghi đè lại cài đặt "SelectReactor" an toàn trong settings.py.
        # Đặt giá trị là None sẽ bảo Scrapy tự động chọn reactor tốt nhất.
        # Hoặc chỉ định rõ ràng nếu bạn muốn:
        "TWISTED_REACTOR": None,
    }

    # --- SỬ DỤNG BỘ HEADERS ĐÃ ĐƯỢC CHỨNG MINH LÀ HOẠT ĐỘNG ---
    # Đây là "chìa khóa vàng" của bạn
    SUCCESSFUL_HEADERS = {
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

    def __init__(self, product_id=None, limit_reviews=100, *args, **kwargs):
        super(CoupangReviewsSpider, self).__init__(*args, **kwargs)
        if not product_id:
            raise ValueError("Vui lòng cung cấp product_id.")
        
        self.product_id = str(product_id)
        self.base_api_url = f'https://www.coupang.com/next-api/review?productId={self.product_id}&page={{page_num}}&size=20&sortBy=DATE_DESC'
        self.limit_reviews = int(limit_reviews)

    def start_requests(self):
        first_page_url = self.base_api_url.format(page_num=1)
        
        headers = self.SUCCESSFUL_HEADERS.copy()
        headers['Referer'] = f'https://www.coupang.com/vp/products/{self.product_id}'
        
        yield scrapy.Request(
            url=first_page_url,
            headers=headers,
            callback=self.parse,
            meta={
                'page': 1,
                'collected_reviews_count': 0
            }
        )

    def parse(self, response):
        # Lấy trạng thái từ meta
        current_page = response.meta['page']
        collected_reviews_count = response.meta['collected_reviews_count']
        
        self.log(f'Đang xử lý trang số: {current_page}')

        try:
            data = response.json()
        except json.JSONDecodeError:
            self.log(f'Lỗi: Response không phải là JSON hợp lệ trên trang {current_page}.')
            self.log(f"Nội dung response: {response.text[:500]}")
            return
        
        reviews = data.get('rData', {}).get('paging', {}).get('contents', [])
        if not reviews and current_page > 1:
            self.log(f'Không tìm thấy review nào trên trang {current_page}. Dừng lại.')
            return

        for review in reviews:
            if collected_reviews_count >= self.limit_reviews:
                self.log(f"Đã đạt giới hạn {self.limit_reviews} reviews. Dừng lại.")
                return

            review_timestamp_ms = review.get('reviewAt')
            review_date = datetime.fromtimestamp(review_timestamp_ms / 1000).strftime('%Y.%m.%d') if review_timestamp_ms else None

            review_item = ReviewItem()
            review_item['date'] = review_date
            review_item['rating'] = review.get('rating')
            review_item['item_name'] = review.get('itemName')
            
            yield review_item
            collected_reviews_count += 1

        # Logic phân trang
        if collected_reviews_count < self.limit_reviews:
            next_page = current_page + 1
            next_page_url = self.base_api_url.format(page_num=next_page)
            
            headers = self.SUCCESSFUL_HEADERS.copy()
            headers['Referer'] = f'https://www.coupang.com/vp/products/{self.product_id}'
            
            yield scrapy.Request(
                url=next_page_url,
                headers=headers,
                callback=self.parse,
                meta={
                    'page': next_page,
                    'collected_reviews_count': collected_reviews_count
                }
            )