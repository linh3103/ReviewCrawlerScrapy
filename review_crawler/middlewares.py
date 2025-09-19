import time
from weakref import WeakKeyDictionary
from scrapy import signals
from scrapy.http import HtmlResponse

# --- THAY ĐỔI QUAN TRỌNG VỀ IMPORT ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# không cần uc nữa

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import shutil
import os

class ReviewCrawlerSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ReviewCrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

class NaverSeleniumMiddleware:

    def __init__(self, timeout=15):
        self.timeout = timeout
        self.drivers = WeakKeyDictionary()

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware
    
    def process_request(self, request, spider):
        if not request.meta.get("use_selenium"):
            return None
        
        driver_info = self.drivers.get(spider)
        if not driver_info:
            spider.logger.error("Could not find a driver for this spider. Make sure to set middleware_flags.")
            return None
        
        driver = driver_info['driver']
        is_initial_setup_done = driver_info['is_initial_setup_done']
        wait = WebDriverWait(driver, self.timeout)

        if not is_initial_setup_done:

            driver.get(request.url)
            self._go_to_review_tab(wait, spider, driver)
            driver_info['is_initial_setup_done'] = True

        elif request.meta.get("click_next_page"):
            page_to_click = request.meta.get("current_page")
            if not self._click_next_page(wait, page_to_click, spider, driver):
                return HtmlResponse(
                    url=driver.current_url,
                    body=b"",
                    encoding="utf-8",
                    request=request
                )

        REVIEW_LIST_SELECTOR = "div#REVIEW li[data-shp-area='revlist.review']"
        
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, REVIEW_LIST_SELECTOR)))
        except (TimeoutException, NoSuchElementException):
            return HtmlResponse(
                url=driver.current_url,
                body=b"",
                encoding="utf-8",
                request=request
            )
        
        # Sử dụng JavaScript để lấy tất cả outerHTML một lần
        body = driver.execute_script("""
            var elements = document.querySelectorAll("div#REVIEW li[data-shp-area='revlist.review']");
            var htmlArray = [];
            for (var i = 0; i < elements.length; i++) {
                htmlArray.push(elements[i].outerHTML);
            }
            return htmlArray.join('\\n');
        """)

        return HtmlResponse(
            url=driver.current_url,
            body=body,
            encoding="utf-8",
            request=request
        )
    
    def _go_to_review_tab(self, wait, spider, driver):
        qna_locator = (By.ID, "QNA")
        self.scroll_and_wait_for_element(driver, qna_locator, wait)

        REVIEW_TAB_SELECTOR = "div#_productFloatingTab ul li a[data-name='REVIEW']"
        review_tab_locator = (By.CSS_SELECTOR, REVIEW_TAB_SELECTOR)
        review_tab = self.scroll_and_wait_for_element(driver, review_tab_locator, wait)
        review_tab.click()

        recent_button_locator = (By.XPATH, "//a[contains(text(), '최신순')]")
        recent_button = self.scroll_and_wait_for_element(driver, recent_button_locator, wait)
        recent_button.click()

    def _click_next_page(self, wait, page, spider, driver):
        NEXT_PAGE_SELECTOR = f"div#REVIEW div[data-shp-area-id='pgn'] a[data-shp-contents-id='{page}']"
        next_page_locator = (By.CSS_SELECTOR, NEXT_PAGE_SELECTOR)
        try:
            next_page_element = self.scroll_and_wait_for_element(driver, next_page_locator, wait)
            next_page_element.click()
            time.sleep(1)
            return True
        except (NoSuchElementException, TimeoutException):
            return False
        
    def scroll_and_wait_for_element(self, driver, locator, wait):
        """Combination of scrolling + WebDriverWait"""
        
        # Custom expected condition
        def element_to_be_found_and_scrolled(locator):
            def _predicate(driver):
                try:
                    element = driver.find_element(*locator)
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    return element
                except:
                    return False
            return _predicate
        
        time.sleep(1)
        return wait.until(element_to_be_found_and_scrolled(locator))

    def _get_chrome_options(self, spider):
        chrome_options = webdriver.ChromeOptions()
        
        # Các tùy chọn chống phát hiện cơ bản
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Các tùy chọn hiệu năng
        chrome_options.add_argument(f'--lang=ko-KR')
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--window-size=1080,768")

        # Đọc và sử dụng hồ sơ người dùng riêng biệt
        user_data_dir = spider.settings.get('SELENIUM_USER_DATA_DIR')
        if user_data_dir:
            spider.logger.info(f"Using custom user data directory: {user_data_dir}")
            chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
            
        return chrome_options

    def spider_opened(self, spider):
        if "use_selenium" in getattr(spider, "middleware_flags", []):
            spider.logger.info(f"Spider {spider.name} requires Selenium. Opening a new browser.")
                  
            driver = self._create_driver(spider)
            
            if driver:
                self.drivers[spider] = {
                    'driver': driver,
                    'is_initial_setup_done': False
                }

    def _create_driver(self, spider):
        """Hàm tạo driver selenium tiêu chuẩn với cấu hình song song."""
        try:
            chrome_options = self._get_chrome_options(spider)
            
            # --- ĐÂY LÀ CHÌA KHÓA ĐỂ CHẠY SONG SONG ---
            # Tạo một Service object. port=0 bảo hệ điều hành tự tìm một port còn trống.
            # Mỗi trình duyệt sẽ có một "đường dây" riêng.
            service = Service(port=0) 
            
            # Khởi tạo driver bằng selenium tiêu chuẩn
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            spider.logger.error(f"Failed to create standard selenium driver: {e}")
            return None

    def spider_closed(self, spider):
        # Hàm này được gọi MỘT LẦN cho MỖI SPIDER khi nó kết thúc.
        if spider in self.drivers:
            spider.logger.info(f"Spider {spider.name} with product ID {spider.product_id} closed. Shutting down its browser.")
            
            # Lấy thông tin driver và đường dẫn hồ sơ
            driver_info = self.drivers.pop(spider)
            driver = driver_info['driver']
            user_data_dir = spider.settings.get('SELENIUM_USER_DATA_DIR')

            # --- BƯỚC 1: ĐÓNG TRÌNH DUYỆT TRƯỚC TIÊN ---
            # Điều này rất quan trọng để giải phóng file khóa trong thư mục hồ sơ.
            try:
                driver.quit()
                spider.logger.info(f"Browser for product {spider.product_id} has been closed.")
            except Exception as e:
                spider.logger.warning(f"Could not quit the driver for product {spider.product_id}: {e}")

            # --- BƯỚC 2: DỌN DẸP THƯ MỤC HỒ SƠ ---
            # Kiểm tra xem đường dẫn có tồn tại không trước khi xóa
            if user_data_dir and os.path.exists(user_data_dir):
                spider.logger.info(f"Cleaning up user data directory: {user_data_dir}")
                try:
                    # shutil.rmtree sẽ xóa toàn bộ thư mục và nội dung bên trong
                    shutil.rmtree(user_data_dir)
                    spider.logger.info(f"Successfully cleaned up directory for product {spider.product_id}.")
                except Exception as e:
                    # Bắt lỗi nếu không xóa được (ví dụ: do quyền truy cập)
                    spider.logger.error(f"Failed to clean up user data directory {user_data_dir}: {e}")
            else:
                spider.logger.warning(f"User data directory not found or not specified, skipping cleanup for product {spider.product_id}.")