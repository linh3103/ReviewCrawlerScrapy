# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.http import HtmlResponse
import time
from weakref import WeakKeyDictionary

# ===== imports used for naver spider ===============================================
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from review_crawler.helpers.ChromeVerHelper import get_chrome_major_version
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# ===== imports used for naver spider ===============================================

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
            page_to_click = request.meta.get("page_to_click")
            if not self._click_next_page(wait, page_to_click, spider, driver):
                return HtmlResponse(
                    url=driver.current_url,
                    body=b"",
                    encoding="utf-8",
                    request=request
                )

        REVIEW_LIST_SELECTOR = "div#REVIEW li[data-shp-area='revlist.review']"
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, REVIEW_LIST_SELECTOR)))
        
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
        qna_tab = wait.until(EC.presence_of_element_located((By.ID, "QNA")))
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'start' });", qna_tab)

        time.sleep(1)

        REVIEW_TAB_SELECTOR = "div#_productFloatingTab ul li a[data-name='REVIEW']"
        review_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, REVIEW_TAB_SELECTOR)))
        review_tab.click()

        recent_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '최신순')]")))
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", recent_button)
        recent_button.click()
        time.sleep(1)

        PAGINATION_SELECTOR = "div[data-shp-area='revlist.pgn']"
        pagination_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PAGINATION_SELECTOR)))
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", pagination_element)
        time.sleep(1)

    def _click_next_page(self, wait, page, spider, driver):
        NEXT_PAGE_SELECTOR = f"div#REVIEW div[data-shp-area-id='pgn'] a[data-shp-contents-id='{page}']"
        try:
            next_page_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, NEXT_PAGE_SELECTOR)))
            next_page_element.click()
            time.sleep(1)
            return True
        except (NoSuchElementException, TimeoutException):
            return False

    def _get_chrome_options(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f'--lang=ko-KR')
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        return chrome_options

    def spider_opened(self, spider):
        # Hàm này được gọi MỘT LẦN cho MỖI SPIDER khi nó bắt đầu.
        # Chỉ hành động nếu spider cần Selenium.
        if "use_selenium" in getattr(spider, "middleware_flags", []):
            spider.logger.info(f"Spider {spider.name} requires Selenium. Opening a new browser.")
            
            # Khởi tạo driver và LƯU NÓ VÀO DICTIONARY với key là spider object
            chrome_options = self._get_chrome_options()
            driver = uc.Chrome(options=chrome_options)
            self.drivers[spider] = {
                'driver': driver,
                'is_initial_setup_done': False # Mỗi spider có cờ trạng thái riêng
            }

    def spider_closed(self, spider):
        # Hàm này được gọi MỘT LẦN cho MỖI SPIDER khi nó kết thúc.
        if spider in self.drivers:
            spider.logger.info(f"Spider {spider.name} closed. Shutting down its browser.")
            driver_info = self.drivers.pop(spider)
            driver_info['driver'].quit()