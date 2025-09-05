import pandas as pd
from review_crawler.items import ReviewWithOptionItem

class ProcessReviewOptionPipeline:
    def process_item(self, item, spider):
        if spider.name == 'coupang_reviews':
            return self.process_coupang_option(item)
        
        elif spider.name == 'ohouse_reviews':
            return self.process_ohouse_option(item)
        return item

    def process_coupang_option(self, item):
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
    
    def process_ohouse_option(self, item):
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

        # Bây giờ, tất cả các list trong data_dict chắc chắn có cùng độ dài
        df = pd.DataFrame(data_dict)

        fileName = f"{spider.name}_code_{spider.product_id}.xlsx"
        df.to_excel(fileName, index=False)