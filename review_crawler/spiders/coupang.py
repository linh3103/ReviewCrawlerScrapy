import scrapy
import json
from datetime import datetime
from review_crawler.items import ReviewItem
from review_crawler.enums import SpiderName
from scrapy.exceptions import CloseSpider

class CoupangReviewsSpider(scrapy.Spider):
    name = SpiderName.COUPANG_SPIDER.value

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "review_crawler.handlers.RequestsDownloadHandler",
            "https": "review_crawler.handlers.RequestsDownloadHandler",
        },
        "DOWNLOAD_TIMEOUT": 30.0,  # 30 giây timeout
        "TWISTED_REACTOR": None,
        "CONCURRENT_REQUESTS": 2,  # Giảm concurrent requests để tránh overload
        "DOWNLOAD_DELAY": 2,       # Delay 2 giây giữa các request
        "RANDOMIZE_DOWNLOAD_DELAY": 0.5,  # Random delay 0.5 * 2 = 1 giây
    }

    SUCCESSFUL_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6,fr-FR;q=0.5",
        "Cache-Control": "no-cache",
        "Cookie": "x-coupang-target-market=KR; x-coupang-accept-language=ko-KR; PCID=17570571490698272908560; _fbp=fb.1.1757057117426.553913826936583264; sid=35b05bd192a24cf2a37041f3fb6a8f9729813452; bm_mi=E7C5B3E56839887665B91C9C97397168~YAAQRvkgFxdt6UuZAQAAhgBaXx3Vlw1+7DCO+PQ7Vmhmsg/m4/EzTTJ8aSlE8Q7ejDVk6d1aWmWDR09kpDPm/JmM0yBbKH3BbL3U+6BJZRvdzgBKmofh8h6geSCo8NL+Z3qIUS2j7c+KwWfb74i/9VQD26wrdekW1QwxZQ9uSWHnx6entru7Ometm2b2eWYdXiV4asMXQIER4cwy2EvJtchNvrY/TUOE1Z7ZtGQ0VxU8AjchQ0rUE3U0wasLl40UdvomiJPSQzRFEA1R+e3cj3s+RfqCV58sMQERLWpvOZP/9c7lECPDIrZyW+OKXYA=~1; ak_bmsc=269CC7CDA5738209766BDC7178084CF1~000000000000000000000000000000~YAAQRvkgFz5t6UuZAQAA3wpaXx2B5XeSZ7K0qjPYmI8nvnwVrrF2s80IU5BW1CEOC6BndXWXr0KKI/6DzmcCsKL0o0rPCAuo2mjgbTHiPNJ110bW5RK545AteVkjWQeebswg8n0nO/r09N9l/zJ1NWk2l5be9U1lAau66jOYOmQv7Tnfh9RahAlIzY0woRqXDufsW3YmSrHrp+hfS8dMq6JuQVfXzi6xUJ6z1thjtBnPSjrmavayr3XRwj/LAZ5YE4kqbSolE5E2V7pDPooX/Ie695B5D/CzeiV4MPuFWWMVyqVs3Z8bmZvCMbESFNc+yCVaTLfWZlbsIeXOkD67f3NJfh4YdVCJYQmpN4TAnqmbgxSvmm86kxAAfsmFXdZrXXq2jobpgra0P3FzdTCYjapUUgb+N9t4ZSRarT/nPhNMK+BSiaf8fnzBHxBUTlXFcIF5QkHSVNFxendudGYi6Ia35L2rrHZWix3hc4QJLD2ClQ==; bm_ss=ab8e18ef4e; bm_so=9E7CAD5BA65F219AA803E28913B14F4069E38220D0EEFB717EEB67D1EC0C1DFD~YAAQBvkgF2yhZDWZAQAAdqWbXwVuGVWhJfShBBS9NW31ewgrfx+AuRri6r+yl2gyVgB0tTR1xmRoh631H9Zo68bMitwt3l1Budpx2hwPsQ8r4W0oqkE7pUJsY23uuqYkjnNwyzOLDmWS68z8OfnaOvPJuk35Q2f2ZuVfZ2/FgZzKwDjn+IHHUAZLObgeblvqr8tZjnre3A6cC8mve05rFBU17n15j+AgDBk71C1lJaxFFBIpkRfFbTM6vbTSmTBjd5sLAuk6CqHD+bHQwvwJ/8epdHGrRBYJDyvGfbbjkVnjmLhMjEmmuvW4G3hxLP61lY/LxS5xyWDdD+hAoeaeVfO2HmMbZYCLsYytQe+/tcS9mswqo3vQqWTACvE964YaL59FRj3JgSQKSTNUELhXPpNUR7byZkRtKvrkjqLaO5NLWRN13b9I5ZwS8bXljkRCfyH9QwAfjntTL3z8vDDm; bm_lso=9E7CAD5BA65F219AA803E28913B14F4069E38220D0EEFB717EEB67D1EC0C1DFD~YAAQBvkgF2yhZDWZAQAAdqWbXwVuGVWhJfShBBS9NW31ewgrfx+AuRri6r+yl2gyVgB0tTR1xmRoh631H9Zo68bMitwt3l1Budpx2hwPsQ8r4W0oqkE7pUJsY23uuqYkjnNwyzOLDmWS68z8OfnaOvPJuk35Q2f2ZuVfZ2/FgZzKwDjn+IHHUAZLObgeblvqr8tZjnre3A6cC8mve05rFBU17n15j+AgDBk71C1lJaxFFBIpkRfFbTM6vbTSmTBjd5sLAuk6CqHD+bHQwvwJ/8epdHGrRBYJDyvGfbbjkVnjmLhMjEmmuvW4G3hxLP61lY/LxS5xyWDdD+hAoeaeVfO2HmMbZYCLsYytQe+/tcS9mswqo3vQqWTACvE964YaL59FRj3JgSQKSTNUELhXPpNUR7byZkRtKvrkjqLaO5NLWRN13b9I5ZwS8bXljkRCfyH9QwAfjntTL3z8vDDm^1758245596881; bm_sc=4~1~827744836~YAAQBvkgF/OhZDWZAQAA6KybXwVfGUd2Bk9DuO/0poQlTF1Ti0yP++A/7D35p3YdY3oRBTXquGMkJ5MUW5hCXRNk4pos/W8QzCfYYtlP1aqQp0BFIIGTKn1Gfk6hCi2jB9PLLeQ7fi5gPoAj5OHQZMrF7sMRjFX1yS4aZICAJn8pFhqxHFlBofrDc2oAGZ8Z05xZmOI+BgbXyBtyu7bQUXyXOW9FPqzNVEphc1HtfTZaAhiJ0heOVeMAEfHv5f93GgQp0f10DgQgvW4dfTONCvR/ztYbxxtiUH9jrAgWrGO4ptz4u34ZQpYHy4HgqDA33Cyx7VEY0NIlxhbigR/FlfiU9X7neex7sfFPZ7EPFasnXvuG1OSGEvHLItm4LcJSmL61pfieU+yIPY9bsJBPswpgt+XZW8uQbDxLC41OSl4WGC7PrlpmyE+5akyxGgY=; bm_sz=876D59E0212445B84416AD530724A461~YAAQBvkgF/WhZDWZAQAA6KybXx2m7HPCAVRXde3Jpwefx0ob2Xwda59XUZbKzJVTm+/oEzCEEtqe248XauGwc+G/AYZt/W+50oabBWwwS3IlW7SsEXDitXdZAWu2jmFcbsnVBTm1+rnfmmIdH/slRwGXilQzUOaE+W54U5Imo4/XAQbkeFPXFMCo9hDisV7VmlU+gdXqOQFdfReBiJHugtCif87SvgQDDDDXN70gdXerGmDMW6PtibEZWaOuWgLEVTSvduyj+upFRIINDUOVgf0VA/5R8JhDdrxrYaqgvBUSJya1jlU+Et6VSYKs7E68w+xgK2XZarPAYViXaHiFOzvo/DFpCXik0mLvLJ+5G23LJgyI6lWgYw8ZfoDOs7cLgr9RoK+496RAXM4bdM/82G2Hmi86cAaEQ1AbnaWKJa3OBih3hvPV/VdkPUKTXjsLdZW0EfCB6KA419tXU0l75hQFekTT8lMEYXV5rMi/DDgrO+1klKjEcOUI3jCuPF0=~4536388~3617840; _abck=B49CCEC5A7603A01C6862FA50287ECEA~0~YAAQBvkgF/yhZDWZAQAAN62bXw5vuMw/S9X4g+dwgqaExmAOkyCDAkTZqydCtzv4xTCBG3XNfzdnEl1uJeQpFbwwOFcxPBdj4OXPMFSg9T/zcevzw4r3nvWRxebtpWTFlpiyj0RADnrsjGnW/jMRbE4IMjkX4ZxqyLEeJGMIy97G6f65V69YdXyLuIcdD1zKBD/99WgU6v3NQ1xTeJHWVXK/OOdOn5MyCIn4KIT8NyXyzZ1+2j3pFRexwLHoEV9ntINhcfQRkp07m7c7MnmDDsHgiEtYSpbLyYLalBFZa85q/r7NXtIP/tA5EbS7Cl2PcxW4DpVpcJnu9tbmw2zJjqaa3OwwBBBBOzMpMOlBp2f7QTYuTRQJyhOt+G8Zi2EQ7hJ57lZ50cAz80zdLkaGyKywAZJljpOaa/VZ4rPXJExoV3qQPrnSl4pjB4+EwbKjhE1ux4oxAL4BkCYhjTk34rqrC7O9o7kzTAMTj7Vx8ay0OOxOh8rhcO9dMIzqrl4PTpUM/YvMLmcKLF5dNk/DiFNUtT51sUcC/StdvfaOHeNQfJxSIT/+ZUc8sCSMgY/6Y/YfHQfgH+9ZlxUteD+lfdPaZftyoHPcmdfMh1d3VNYGgtRrRLwvSqcsGfVDkR3l09htFxH8hynpK9KBj8fxQMvd~-1~-1~1758248624~AAQAAAAE%2f%2f%2f%2f%2fzPzSDpFLx8RscX0mrNVZyVQzlvW9QJWMjdLtjI8filnCZxt3lT6PKcRU2VgkVUdemMSPhsGfX7PPV3zsFwzLb%2fiKKPp1fYgOiV16P7%2fHbB9F64mNb48TFi9x9uWW3xDu8i9RuM%3d~-1; bm_s=YAAQBvkgF3OiZDWZAQAAIbKbXwRTAvdU8L5wewrx4uhiHgFX5yBof0xGusBMRy1SC+9ODtdDUCEzetBfc5dEuQhFsA9HDfzmCJkbrJbYWu0pEYYHuTiTnhVs2k2MQ2gP1M54e4KlHUrdQWpC2GXeAJ1pI5ZQ9EZn7N7sLQISomPfX1dkp+k/t++qhcuGroAt7V+3IRZ9YbxKaJII5QrsqCVTbtKDrGbJisOSi01ehp3qEh4cgBI7MniAtnE+sgFse66d3eZ1BWNYOWvAuQm4xmtQYP456rlvqJZiLHbbnxgk2jjmhlt34QvqynMPPnfTmMkYCGF9rnGIh1nezoz86hqd8XPfVVAiX3uEP9EgDiRWxD9q9fRj0XThhTu5GWLUHN+Ib+TfoS6keTkL+dbogr23JTcf47/mZ9jCShbsSDQH9JHatv/x2ZlOks/WWKmmTb1Nu9FENKwKsyC1eNNUVWfSgtdz+5pt20Tdn9X2ZajKatt8Do83Enq5hF1ojSR/i3HYbh5DnK/bb/NtJMzSKAJYxVJnjBh70lrjR2Nv/a5Izag2GXeWQzSUKhdo/Gqvi4phlsHGkQ==; bm_sv=DA2A01C245A931A0603C0F0F80978835~YAAQBvkgF3SiZDWZAQAAIbKbXx1pM0ssQ97ow+7HFWVLw4lxJOuHXq8Jas47DaN/c4P70txhuQ4MLozu2O6ZNraPRgxi+B+yZznnRth+3zXAM+rXvNRagziZU7UVdRkS1kQmVbfYg8jrijUblBi+twhi96m/Rik2coEtUfg9V1v8vsTFb9pxatdbtb6mdU4H8q/UtkHmtyiim8T20UAAxhdAe3wcGrUYCBhTXt0xRFieU25Piiskj95CV7k5IJkTMwI=~1; __cf_bm=yulpOkBiE.HI.DmB9Gf0dcuFjQsAbFOFUteRyOvAAcE-1758245663-1.0.1.1-OiRGd3fPwB8Bi0hd3y7w4p4c.K6ix0zBCat23DmbzB6qvxTOeoFO8mDu8tywO1om7k2D6IqYvnDPobe00S4H82whodlKXUluX.FaDkstgVU; cto_bundle=83otWV9pUG5nUHByWjJRVUt3cHA2dCUyRjJ0R2p1R21ES1NYcnRJQkRhaEd0SXBkZU9lSGZCSEZ2Y3o5bXlQZ0h1QmM0V0QzN1p0SFNKbk5kUWlJRHNRMEpQY1FSZElaMDh3YzBFWHByY3NnSG81ZjIzVVk1NFE2REtlRzdhcHM3b0tqVnRVblFoeUlCMDdkbVRIcGI1RWN2YXY5ODZ3ZnQlMkJ5OHhuQkNqa0thbyUyQkRFZDVJVUxheGw3ZG5iODZTWm5UbkpGWXlDdkQ0cHYlMkJyTSUyQloyalNpTjdpaEZsVEpEUnpaNVlOZmJVOGpkSVZZTUZ0NG5oUCUyRnpVYmZhRHNoTTAlMkJDJTJCTVZQTHJEN1c3V3V1QmtDciUyRk8lMkJYYncwWnhKV3ZqV0pUR1FDTzFzakxYdXBkTzhvRUxCQnNobjNhU2RYY05nQmlKUTFF",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Sec-Ch-Ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }

    def __init__(self, product_id=None, limit_reviews=100, *args, **kwargs):
        super(CoupangReviewsSpider, self).__init__(*args, **kwargs)
        if not product_id:
            raise ValueError("Vui lòng cung cấp product_id.")
        
        self.product_id = str(product_id)
        self.base_api_url = f'https://www.coupang.com/next-api/review?productId={self.product_id}&page={{page_num}}&size=20&sortBy=DATE_DESC'
        self.limit_reviews = int(limit_reviews)
        self.report_folder_name = "Coupang"
        
        # Timeout tracking
        self.timeout_occurred = False
        self.start_time = datetime.now()

    def start_requests(self):
        first_page_url = self.base_api_url.format(page_num=1)
        
        headers = self.SUCCESSFUL_HEADERS.copy()
        headers['Referer'] = f'https://www.coupang.com/vp/products/{self.product_id}'
        
        self.logger.info(f"Starting crawl for product {self.product_id} with timeout 30s")
        
        yield scrapy.Request(
            url=first_page_url,
            headers=headers,
            callback=self.parse,
            meta={
                'page': 1,
                'collected_reviews_count': 0
            },
            errback=self.handle_error
        )

    def parse(self, response):
        # Check if timeout occurred
        if self.timeout_occurred:
            self.logger.warning("Timeout detected, stopping crawl")
            raise CloseSpider("Timeout occurred")
            
        current_page = response.meta['page']
        collected_reviews_count = response.meta['collected_reviews_count']
        
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f'Đang xử lý trang số: {current_page} (Elapsed: {elapsed_time:.1f}s)')

        # Check for timeout manually as well
        if elapsed_time > 30:
            self.logger.error("Manual timeout check: 30 seconds exceeded")
            raise CloseSpider("Manual timeout: exceeded 30 seconds")

        try:
            data = response.json()
        except json.JSONDecodeError:
            self.logger.error(f'Lỗi: Response không phải là JSON hợp lệ trên trang {current_page}.')
            self.logger.error(f"Status Code: {response.status}")
            self.logger.error(f"Response headers: {dict(response.headers)}")
            self.logger.error(f"Nội dung response: {response.text[:500]}")
            
            # Close spider if JSON decode fails (likely blocked)
            raise CloseSpider(f"JSON decode failed on page {current_page} - possibly blocked")
        
        reviews = data.get('rData', {}).get('paging', {}).get('contents', [])
        if not reviews and current_page > 1:
            self.logger.info(f'Không tìm thấy review nào trên trang {current_page}. Dừng lại.')
            return

        processed_in_page = 0
        for review in reviews:
            if collected_reviews_count >= self.limit_reviews:
                self.logger.info(f"Đã đạt giới hạn {self.limit_reviews} reviews. Dừng lại.")
                return

            review_timestamp_ms = review.get('reviewAt')
            review_date = datetime.fromtimestamp(review_timestamp_ms / 1000).strftime('%Y.%m.%d') if review_timestamp_ms else None

            review_item = ReviewItem()
            review_item['date'] = review_date
            review_item['rating'] = review.get('rating')
            review_item['item_name'] = review.get('itemName')
            
            yield review_item
            collected_reviews_count += 1
            processed_in_page += 1

        self.logger.info(f"Processed {processed_in_page} reviews on page {current_page}")

        # Logic phân trang với timeout check
        if collected_reviews_count < self.limit_reviews:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            if elapsed_time > 25:  # Stop before timeout
                self.logger.warning(f"Approaching timeout ({elapsed_time:.1f}s), stopping pagination")
                return
                
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
                },
                errback=self.handle_error
            )

    def handle_error(self, failure):
        """Handle request errors including timeout"""
        self.logger.error(f"Request failed: {failure}")
        
        if "timeout" in str(failure).lower():
            self.timeout_occurred = True
            self.logger.error("Timeout detected in error handler")
            raise CloseSpider("Request timeout occurred")
        else:
            self.logger.error(f"Other error: {failure}")
            raise CloseSpider(f"Request failed: {failure}")

    def closed(self, reason):
        """Called when spider closes"""
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f"Spider closed. Reason: {reason}. Total time: {elapsed_time:.1f}s")
        
        if "timeout" in reason.lower():
            self.logger.warning("Spider was closed due to timeout")
        elif elapsed_time > 30:
            self.logger.warning(f"Spider took {elapsed_time:.1f}s (>30s)")
        else:
            self.logger.info("Spider completed normally")