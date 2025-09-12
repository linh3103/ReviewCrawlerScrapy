from review_crawler.items import ReviewWithOptionItem
from review_crawler.helpers.DateHelper import format_date_str

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

