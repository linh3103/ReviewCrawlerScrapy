from dateutil.relativedelta import relativedelta
from wcwidth import wcswidth
import pandas as pd
import os

class ExcelExportPipeline:
    def __init__(self):
        self.reviews = []
        # Giả sử hàm ProcessExcel là một phương thức của class này hoặc được import
        # self.ProcessExcel = ProcessExcel 

    def open_spider(self, spider):
        self.reviews = []

    def process_item(self, item, spider):
        # Chuyển item Scrapy thành dict để dễ xử lý
        self.reviews.append(dict(item))
        return item

    def close_spider(self, spider):
        if not self.reviews:
            return

        # Bước 1: Thu thập tất cả các key tùy chọn duy nhất
        option_keys = set()
        for item in self.reviews:
            if 'options' in item and isinstance(item['options'], dict):
                option_keys.update(item['options'].keys())

        # Chuyển set thành list để có thể sắp xếp
        sorted_option_keys = list(option_keys)

        # YÊU CẦU 2: Nếu spider là coupang_reviews, sắp xếp các cột option
        if spider.name == 'coupang_reviews':
            # Hàm key để trích xuất số từ 'option_1', 'option_2',...
            # Điều này đảm bảo 'option_10' đứng sau 'option_9'
            def sort_key(key):
                if key.startswith('option_') and key.split('_')[1].isdigit():
                    return int(key.split('_')[1])
                # Trả về một giá trị lớn để các key không khớp mẫu bị đẩy xuống cuối
                return float('inf') 
            
            sorted_option_keys.sort(key=sort_key)

        # Bước 2: Khởi tạo data_dict với các cột cố định và các cột option đã được sắp xếp
        data_dict = {'Date': [], 'Rating': []}
        for key in sorted_option_keys:
            data_dict[key] = []

        # Bước 3: Điền dữ liệu vào data_dict
        for item in self.reviews:
            data_dict['Date'].append(item.get('date'))
            data_dict['Rating'].append(item.get('rating'))
            
            current_options = item.get('options', {}) if isinstance(item.get('options'), dict) else {}
            
            for key in sorted_option_keys:
                data_dict[key].append(current_options.get(key, None))

        df = pd.DataFrame(data_dict)

        # YÊU CẦU 1: Đảm bảo cột "Single options" luôn ở cuối cùng nếu tồn tại
        if 'Single options' in df.columns:
            # Lấy danh sách tất cả các cột
            cols = list(df.columns)
            # Xóa cột 'Single options' khỏi vị trí hiện tại
            cols.remove('Single options')
            # Thêm nó lại vào cuối danh sách
            new_order = cols + ['Single options']
            # Sắp xếp lại DataFrame theo thứ tự mới
            df = df[new_order]

        # Chuyển đổi kiểu dữ liệu và xử lý file
        df['Date'] = pd.to_datetime(df['Date'], format="%Y.%m.%d", errors='coerce')
        df["Rating"] = pd.to_numeric(df['Rating'], errors='coerce')

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        base_dir = os.path.join(desktop, "Product ratings", spider.name)
        os.makedirs(base_dir, exist_ok=True)
        
        # Lấy product_id từ spider nếu có
        product_id = getattr(spider, 'product_id', 'unknown_product')
        fileName = os.path.join(base_dir, f"{spider.name}_code_{product_id}.xlsx")
        
        self.ProcessExcel(df, fileName)

    def ProcessExcel(self, df: pd.DataFrame, file_name: str):
        pivot = {}

        # --- 1. Tính toán ---

        first_date = df['Date'].min()
        last_date = df['Date'].max()

        # Date range
        date_range = f"{first_date.strftime('%Y.%m.%d')} - {last_date.strftime('%Y.%m.%d')}"
        pivot["Date range"] = date_range

        # Số review trung bình 1 ngày
        days = (last_date - first_date).days + 1
        avg_review_count_per_day = round(len(df) / days, 2) if days > 0 else len(df)
        pivot["Average review count"] = avg_review_count_per_day

        # Điểm đánh giá trung bình
        avg_rating = round(df["Rating"].mean(), 2)
        pivot["Average review rating"] = avg_rating

        # Đếm số review trong vòng 1 tháng trở lại đây
        one_month_ago = last_date - relativedelta(months=1)
        past_month_reviews = df[df['Date'] >= one_month_ago]
        pivot[f"Total review in past month ({one_month_ago.strftime('%Y.%m.%d')}-{last_date.strftime('%Y.%m.%d')})"] = len(past_month_reviews)
        
        # --- 2. Ghi và định dạng Excel ---
        df['Date'] = df['Date'].dt.strftime('%Y.%m.%d')
        with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:

            # Tạo sheet chính - Ratings
            df.to_excel(writer, sheet_name="Ratings", index=False)
            workbook = writer.book
            worksheet_ratings = writer.sheets["Ratings"]
            
            # --- 3. Tạo Formats ---
            border_format = workbook.add_format({'border': 1})
            header_base = {'bold': True, 'valign': 'vcenter'}
            header_left_format = workbook.add_format({**header_base, 'align': 'left'})
            header_center_format = workbook.add_format({**header_base, 'align': 'center'})
            cell_base = {'valign': 'vcenter'}
            cell_left_format = workbook.add_format({**cell_base, 'align': 'left'})
            cell_center_format = workbook.add_format({**cell_base, 'align': 'center'})

            # --- 4. Định dạng Sheet "Product ratings" ---
            column_width_overrides = {
                'Review Body': 50
            }

            auto_widths = self.get_col_widths(df)
            for col_num, col_name in enumerate(df.columns):
                width = auto_widths[col_name]
                if col_name in column_width_overrides:
                    width = max(width, column_width_overrides[col_name])

                header_format = header_center_format if col_name == "Rating" else header_left_format
                cell_format = cell_center_format if col_name == "Rating" else cell_left_format
                
                worksheet_ratings.write(0, col_num, col_name, header_format)
                worksheet_ratings.set_column(col_num, col_num, width, cell_format)

            start_row = 0
            start_col = 0

            # Xác định vùng chứa dữ liệu
            end_row = len(df)
            end_col = len(df.columns) - 1

            worksheet_ratings.conditional_format(start_row, start_col, end_row, end_col, {
                'type': 'no_blanks',
                'format': border_format
            })
            worksheet_ratings.conditional_format(start_row, start_col, end_row, end_col, {
                'type': 'blanks',
                'format': border_format
            })

            # --- 5. Định dạng Sheet "Pivot" ---
            worksheet_pivot = workbook.add_worksheet("Pivot")
            pivot_df = pd.DataFrame(pivot.items(), columns=["Metric", "Value"])
            pivot_header_format = workbook.add_format({**header_base, 'align': 'left', 'border': 1})
            pivot_cell_format = workbook.add_format({**cell_base, 'align': 'left', 'border': 1})
            
            for row_num, row_data in pivot_df.iterrows():
                worksheet_pivot.write(row_num, 0, row_data["Metric"], pivot_header_format)
                worksheet_pivot.write(row_num, 1, row_data["Value"], pivot_cell_format)

            pivot_widths = self.get_col_widths(pivot_df)
            worksheet_pivot.set_column(0, 0, pivot_widths["Metric"])
            worksheet_pivot.set_column(1, 1, pivot_widths["Value"])

            start_col = 3
            for col in df.columns:
                if col in ["Date", "Rating"]:
                    continue
                counts = df[col].value_counts().reset_index()
                counts.columns = ["Value", "Count"]
                
                worksheet_pivot.merge_range(0, start_col, 0, start_col + 1, col, header_center_format)
                worksheet_pivot.write(1, start_col, "Value", header_left_format)
                worksheet_pivot.write(1, start_col + 1, "Count", header_left_format)
                
                for i, r in enumerate(counts.itertuples(index=False), start=2):
                    worksheet_pivot.write(i, start_col, r.Value)
                    worksheet_pivot.write(i, start_col + 1, r.Count)
                
                worksheet_pivot.conditional_format(0, start_col, len(counts) + 1, start_col + 1, {'type': 'no_blanks', 'format': border_format})
                
                counts_widths = self.get_col_widths(counts)
                worksheet_pivot.set_column(start_col, start_col, counts_widths["Value"])
                worksheet_pivot.set_column(start_col + 1, start_col + 1, counts_widths["Count"])
                
                start_col += 3

    def get_col_widths(self, dataframe: pd.DataFrame) -> dict:
        widths = {}
        for col in dataframe.columns:
            header_len = wcswidth(str(col))
            
            # Xử lý trường hợp cột trống để tránh lỗi
            if dataframe[col].empty:
                max_data_len = 0
            else:
                max_data_len = dataframe[col].astype(str).map(wcswidth).max()
            
            if pd.isna(max_data_len):
                max_data_len = 0
                
            width = max(max_data_len, header_len) + 8
        
            widths[col] = min(width, 255)
        return widths