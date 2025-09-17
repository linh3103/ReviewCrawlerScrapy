import scrapy
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from review_crawler.enums import SiteName, SpiderName

class ProductListSpider(scrapy.Spider):
    name = "product_list"

    PROJECT_NAME = "review_crawler"
    SCRAPYD_URL = "http://localhost:6800"

    def __init__(self, sheet_url=None, *args, **kwargs):
        super(ProductListSpider, self).__init__(*args, **kwargs)
        if not sheet_url:
            raise ValueError("Vui lòng cung cấp sheet_url.")
        self.sheet_url = sheet_url

        self.brands_products = self.get_data_from_google_sheet()

    def get_data_from_google_sheet(self):
        try:
            # Xác định phạm vi truy cập (scope)
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ]
            
            # Sử dụng file credentials.json để xác thực
            # Đảm bảo file credentials.json nằm trong thư mục gốc của dự án
            creds = ServiceAccountCredentials.from_json_keyfile_name('google_services_credentials.json', scope)
            
            # Ủy quyền cho gspread
            client = gspread.authorize(creds)
            
            # Mở Google Sheet bằng tên của nó
            # Thay 'Tên Sheet Của Bạn' bằng tên thật của sheet
            self.logger.debug(f"Google sheet: {self.sheet_url}")
            sheet = client.open_by_url(self.sheet_url).sheet1
            
            # Lấy tất cả dữ liệu từ sheet dưới dạng danh sách các dictionary
            # gspread sẽ tự động dùng dòng đầu tiên làm key
            data = sheet.get_all_records()
            self.logger.info(f"Đã đọc thành công {len(data)} dòng từ Google Sheet.")
            return data
            
        except FileNotFoundError:
            self.logger.error("Lỗi: Không tìm thấy file credentials.json. Hãy đảm bảo nó nằm ở thư mục gốc của dự án.")
            return []
        except gspread.exceptions.SpreadsheetNotFound:
            self.logger.error("Lỗi: Không tìm thấy Google Sheet. Hãy kiểm tra lại tên Sheet và quyền chia sẻ.")
            return []
        except Exception as e:
            self.logger.error(f"Đã có lỗi xảy ra khi đọc Google Sheet: {e}")
            return []
        
    def start_requests(self):
        """
        Phương thức này được Scrapy gọi sau __init__.
        Nó sẽ tạo một request giả để kích hoạt hàm parse.
        """
        # Nếu không đọc được dữ liệu từ sheet thì không làm gì cả
        if not self.brands_products:
            self.logger.warning("Không có dữ liệu từ Google Sheet, spider sẽ dừng.")
            return

        # Tạo một request giả. 'data:,' là một URL hợp lệ, trống rỗng và hoàn thành ngay lập tức.
        # dont_filter=True để đảm bảo request này luôn được thực thi.
        yield scrapy.Request(url='data:,', callback=self.parse, dont_filter=True)

    def parse(self, response):
        for brand_product in self.brands_products:
            request = self.get_request_by_brand_product(brand_product)
            
            if not request:
                continue

            yield request
                
    def get_request_by_brand_product(self, brand_product):
        site = brand_product.get("Site", "")
        product_id = brand_product.get("Product id", "")

        if not site or not product_id:
            self.logger.warning(f"Missing required information: Site='{site}', Product id='{product_id}'. Skipping this entry.")
            return False

        spider_name = self.get_spider_name_by_site(site)
        brand_name = brand_product.get("Brand", "")
        request = {
            "action": "schedule_job",
            "project_name": self.PROJECT_NAME,
            "scrapyd_url": self.SCRAPYD_URL,
            "spider_name": spider_name,
            "brand_name": brand_name,
            "product_id": product_id
        }

        return request
    
    def get_spider_name_by_site(self, site):
        match site:
            case SiteName.COUPANG_SITE.value:
                return SpiderName.COUPANG_SPIDER.value
            
            case SiteName.OHOUSE_SITE.value:
                return SpiderName.OHOUSE_SPIDER.value
            
            case SiteName.NAVER_SITE.value:
                return SpiderName.NAVER_SPIDER.value
        
        

        