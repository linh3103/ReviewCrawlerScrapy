# Đảm bảo đoạn code sửa lỗi Windows vẫn ở đầu file
import scrapy
import undetected_chromedriver as uc
from scrapy.selector import Selector
import time
from review_crawler.helpers.ChromeVerHelper import get_chrome_major_version
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class NaverSeleniumSpider(scrapy.Spider):
    name = 'naver_reviews'

    def __init__(self, product_id=None, *args, **kwargs):
        super(NaverSeleniumSpider, self).__init__(*args, **kwargs)
        if not product_id:
            raise ValueError("Vui lòng cung cấp product_id...")
        self.product_id = product_id
        self.start_urls = [f'https://brand.naver.com/styhome/products/{product_id}']
    
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
        
            self.log("Chờ khu vực QNA xuất hiện...")
            qna_tab = wait.until(EC.presence_of_element_located((By.ID, "QNA")))
            
            # 2. Cuộn đến khu vực đó và chờ một chút để ổn định
            self.log("Cuộn đến QNA...")
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'start' });", qna_tab)
            time.sleep(1)

            # 3. Chờ cho đến khi tab REVIEW có thể click được
            self.log("Chờ tab REVIEW có thể click...")
            review_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#_productFloatingTab ul li a[data-name='REVIEW']")))
            review_tab.click()

            # 4. Chờ cho đến khi nút sắp xếp 'Mới nhất' có thể click được
            self.log("Chờ nút 'Mới nhất' có thể click...")
            recent_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '최신순')]")))
            
            # Cuộn để đảm bảo nút nằm giữa màn hình
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", recent_button)
            time.sleep(1)
            recent_button.click()

            review_elements = []
            REVIEW_LIST_SELECTOR = "div#REVIEW li[data-shp-area='revlist.review']"

            review_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, REVIEW_LIST_SELECTOR))
            )

            for review_el in review_elements:
                date_el = review_el.find_element(By.CSS_SELECTOR, "div > div > div > div strong+span")
                date_text = date_el.text.strip() if date_el else None


        except Exception as e:
            self.log(f"Lỗi trong quá trình xử lý của Selenium: {e}")
            if driver:
                driver.save_screenshot('selenium_error.png')
            yield {'status': 'failed'}
        finally:
            if driver:
                driver.quit()
                self.log("Đã đóng trình duyệt.")