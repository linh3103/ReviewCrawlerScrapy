# Đảm bảo đoạn code sửa lỗi Windows vẫn ở đầu file
from asyncio import wait
import scrapy
import undetected_chromedriver as uc
from scrapy.selector import Selector
import time
from review_crawler.helpers.ChromeVerHelper import get_chrome_major_version
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from review_crawler.items import ReviewItem

class NaverSeleniumSpider(scrapy.Spider):
    name = 'naver_reviews'

    def __init__(self, product_id=None, *args, **kwargs):
        super(NaverSeleniumSpider, self).__init__(*args, **kwargs)
        if not product_id:
            raise ValueError("Vui lòng cung cấp product_id...")
        self.product_id = product_id
        self.start_urls = [f'https://brand.naver.com/8room/products/{product_id}']
        self.total_reviews = 0
        self.limit_reviews = 300
    
    def parse(self, response):
        target_url = response.url
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument(f'--lang=ko-KR')
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = None
        try:
            chrome_version = get_chrome_major_version()
            if not chrome_version:
                raise ValueError("Không thể xác định phiên bản Chrome hiện tại trên hệ thống.")

            driver = uc.Chrome(
                options=options, 
                use_subprocess=True,
                version_main=chrome_version
            )
            
            driver.get(target_url)
            wait = WebDriverWait(driver, 15)
        
            qna_tab = wait.until(EC.presence_of_element_located((By.ID, "QNA")))
            
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'start' });", qna_tab)
            time.sleep(1)

            review_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#_productFloatingTab ul li a[data-name='REVIEW']")))
            review_tab.click()

            recent_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '최신순')]")))
            
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", recent_button)
            time.sleep(1)
            recent_button.click()

            PAGINATION_SELECTOR = "div[data-shp-area='revlist.pgn']"
            pagination_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PAGINATION_SELECTOR)))
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", pagination_element)
            time.sleep(1)

            page = 1
            should_stop = False
            while self.total_reviews < self.limit_reviews and not should_stop:
                REVIEW_LIST_SELECTOR = "div#REVIEW li[data-shp-area='revlist.review']"
                review_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, REVIEW_LIST_SELECTOR)))

                if review_elements:
                    for review in review_elements:
                        date = review.find_element(By.CSS_SELECTOR, "div > div > div > div strong+span").text.rstrip(".")

                        rating = review.find_element(By.CSS_SELECTOR, "div > div > div > div > em").text.strip()

                        prev_element_options = review.find_element(
                            By.CSS_SELECTOR, "div > div > div > div strong+span"
                        ).find_element(By.XPATH, "..")

                        full_option_review = prev_element_options.find_element(
                            By.XPATH, "following-sibling::*[1]"
                        ).text

                        item_name = full_option_review.split('\n')[0].strip()

                        item = ReviewItem()
                        item['date'] = date
                        item['rating'] = rating
                        item['item_name'] = item_name

                        yield(item)
                        self.total_reviews += 1
                        if self.total_reviews >= self.limit_reviews:
                            should_stop = True
                            break

                page += 1
                next_page_selector = f"div#REVIEW div[data-shp-area-id='pgn'] a[data-shp-contents-id='{page}']"
                next_page_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_selector)))
                next_page_element.click()
                time.sleep(1)

        except Exception as e:
            self.log(f"Lỗi trong quá trình xử lý của Selenium: {e}")
            if driver:
                driver.save_screenshot('selenium_error.png')
            yield {'status': 'failed'}
        finally:
            if driver:
                driver.quit()
                self.log("Đã đóng trình duyệt.")