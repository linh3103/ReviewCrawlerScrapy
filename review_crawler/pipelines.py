import pandas as pd
from review_crawler.items import ReviewWithOptionItem
from review_crawler.helpers.DateHelper import format_date_str
import requests
import os
import scrapy

class ProcessReviewOptionPipeline:
    def process_item(self, item, spider):
        if spider.name == 'coupang_reviews':
            return self.process_coupang_item(item)
        
        elif spider.name == 'ohouse_reviews':
            return self.process_ohouse_item(item)
        
        elif spider.name == 'naver_reviews':
            return self.process_naver_item(item)
        
        return item

    def process_coupang_item(self, item):
        item_name = item.get('item_name', '')
        optionItem = ReviewWithOptionItem()
        optionItem['date'] = item.get('date')
        optionItem['rating'] = item.get('rating')
        option_list = item_name.split(',')
        options_dict = {}
        for i, option in enumerate(option_list[1:], start=1):
            option = option.strip()
            options_dict[f"option_{i}"] = option
        optionItem['options'] = options_dict
        return optionItem
    
    def process_ohouse_item(self, item):
        optionItem = ReviewWithOptionItem()
        optionItem['date'] = item.get('date')
        optionItem['rating'] = item.get('rating')

        options_dict = {}
        item_name = item.get('item_name', '')

        if not item_name:
            is_purchased = item.get('isPurchased')
            if is_purchased:
                options_dict['Single options'] = 'No options'
            else:
                options_dict['Single options'] = 'Not purchased'

        else:
            option_parts = item_name.split(' / ')
        
            for option in option_parts:
                    option = option.strip()
                    if ':' in option:
                        key, value = option.split(':', 1)
                        options_dict[key.strip()] = value.strip()

            if not options_dict:
                options_dict['Single options'] = item_name

        optionItem['options'] = options_dict

        return optionItem

    def process_naver_item(self, item):
        optionItem = ReviewWithOptionItem()
        optionItem['date'] = format_date_str(item.get('date'))
        optionItem['rating'] = item.get('rating')

        option_parts= item.get('item_name').split(' / ')
        options_dict = {}

        for part in option_parts:
            option = part.strip()
            if ':' in option:
                key, value = option.split(':', 1)
                options_dict[key.strip()] = value.strip()

        optionItem['options'] = options_dict

        return optionItem

class ExcelExportPipeline:
    def __init__(self):
        self.reviews = []

    def open_spider(self, spider):
        self.reviews = []

    def process_item(self, item, spider):
        self.reviews.append(item)
        return item

    def close_spider(self, spider):
        if not self.reviews: # Xử lý trường hợp không có review nào
            return

        # Bước 1: Thu thập tất cả các key tùy chọn duy nhất
        option_keys = set()
        for item in self.reviews:
            if 'options' in item and isinstance(item['options'], dict):
                for key in item['options'].keys():
                    option_keys.add(key)

        # Bước 2: Khởi tạo data_dict với tất cả các cột
        data_dict = {
            'Date': [],
            'Rating': []
        }
        for key in option_keys:
            data_dict[key] = []

        # Bước 3: Lặp lại và điền dữ liệu một cách an toàn
        for item in self.reviews:
            data_dict['Date'].append(item.get('date'))
            data_dict['Rating'].append(item.get('rating'))
            
            # Lấy options của item hiện tại
            current_options = item.get('options', {}) if isinstance(item.get('options'), dict) else {}

            # Điền giá trị cho các cột tùy chọn
            for key in option_keys:
                # Nếu key có trong options của item này, thêm value. Nếu không, thêm None.
                value = current_options.get(key, None)
                data_dict[key].append(value)

        df = pd.DataFrame(data_dict)

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        base_dir = os.path.join(desktop, "Product ratings", spider.name)

        os.makedirs(base_dir, exist_ok=True)

        fileName = os.path.join(base_dir, f"{spider.name}_code_{spider.product_id}.xlsx")
        df.to_excel(fileName, index=False)

class ScrapydSchedulerPipeline:
    def process_item(self, item, spider):
        # `spider` ở đây là một đối tượng Spider hợp lệ.
        # `item` là dict mà spider đã yield.
        if item.get('action') == 'schedule_job':
            # Gọi hàm schedule_job nhưng không dùng `self.`
            self.schedule_job(item, spider) 
            raise scrapy.exceptions.DropItem(f"Scheduled job for {item.get('product_id')}")
        
        return item

    def schedule_job(self, job_data, spider):
        """
        Gửi một yêu cầu công việc tới Scrapyd.
        `spider` ở đây là spider ĐIỀU PHỐI (ProductListSpider),
        chúng ta dùng logger của nó.
        """
        
        # --- LẤY URL TỪ SETTINGS MỘT CÁCH AN TOÀN ---
        # Đây là cách tốt nhất, không cần truyền qua item.
        # spider.settings luôn tồn tại.
        scrapyd_url = spider.settings.get('SCRAPYD_URL', 'http://localhost:6800')
        
        pid = job_data.get('product_id')

        profile_path = os.path.abspath(os.path.join('profiles', f'user_{pid}'))
        
        payload = {
            'project': job_data.get('project_name'),
            'spider': job_data.get('spider_name'),
            'product_id': pid
        }

        spider_name = job_data.get('spider_name')
        if spider_name == 'naver_reviews':
            payload['brand_name'] = brand = job_data.get('brand_name')
            payload['setting'] = f'SELENIUM_USER_DATA_DIR={profile_path}'

        schedule_url = f"{scrapyd_url}/schedule.json"
        
        try:
            # --- SỬA LỖI Ở ĐÂY ---
            # Dùng logger của spider được truyền vào
            spider.logger.info(f"Sending schedule request to {schedule_url} with payload: {payload}")
            response = requests.post(schedule_url, data=payload)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == 'ok':
                spider.logger.info(f"  -> Job for {brand}-{pid} scheduled. Job ID: {data.get('jobid')}")
            else:
                spider.logger.error(f"  -> Failed to schedule job. Reason: {data.get('message')}")
        except requests.exceptions.RequestException as e:
            spider.logger.error(f"  -> ERROR: Could not connect to Scrapyd at {scrapyd_url}. Details: {e}")