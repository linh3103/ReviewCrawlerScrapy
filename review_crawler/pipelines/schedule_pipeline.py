import requests
import os
import scrapy

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
        brand_name = job_data.get('brand_name')
        if spider_name == 'naver_reviews':
            payload['brand_name'] = brand_name
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
                spider.logger.info(f"  -> Job for {brand_name}-{pid} scheduled. Job ID: {data.get('jobid')}")
            else:
                spider.logger.error(f"  -> Failed to schedule job. Reason: {data.get('message')}")
        except requests.exceptions.RequestException as e:
            spider.logger.error(f"  -> ERROR: Could not connect to Scrapyd at {scrapyd_url}. Details: {e}")