from utils.check_requirements import check_and_install_requirements

check_and_install_requirements()

from flask import Flask, render_template, request, jsonify
import requests

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Cấu hình URL của Scrapyd và tên project
SCRAPYD_URL = "http://localhost:6800"
PROJECT_NAME = "review_crawler" # Thay bằng tên project của bạn

# --- THAY ĐỔI Ở ĐÂY ---
# NEW: Thêm danh sách các brand của Naver
NAVER_BRANDS_DATA = {
    "바자르": "https://brand.naver.com/bazaar/products/",
    "라뽐므": "https://brand.naver.com/lapomme/products/",
    "쁘리엘르": "https://brand.naver.com/prielle/products/",
    "마틸라": "https://brand.naver.com/maatila/products/",
    "그래이불": "https://brand.naver.com/yesbedding/products/",
    "믹스앤매치": "https://brand.naver.com/mixandmatch/products/",
    "누비지오": "https://brand.naver.com/nubizio/products/",
    "데코뷰": "https://brand.naver.com/decoview/products/",
    "깃든": "https://brand.naver.com/gitden/products/",
    "스타일링홈": "https://brand.naver.com/styhome/products/",
    "아망떼": "https://brand.naver.com/amante/products/",
    "호무로": "https://brand.naver.com/homuro/products/",
    "헬로우슬립": "https://brand.naver.com/hellosleep/products/",
    "오넬로이": "https://smartstore.naver.com/oneloi/products/",
    "플로라": "https://brand.naver.com/flora/products/",
    "르올": "https://smartstore.naver.com/mewansungmall/products/",
    "에이트룸": "https://brand.naver.com/8room/products/",
    "베이직톤": "https://brand.naver.com/basictone/products/",
    "아토앤알로": "https://brand.naver.com/beddingnara/products/",
    "바숨": "https://brand.naver.com/busum/products/",
    "올리비아데코": "https://brand.naver.com/oliviadeco/products/",
    "코지네스트": "https://brand.naver.com/cozynest/products/",
    "메종오트몬드": "https://smartstore.naver.com/hautemonde/products/",
    "바운티풀": "https://brand.naver.com/bountiful/products/",
    "도아드림": "https://brand.naver.com/doadream_goose/products/",
    "CROWN GOOSE": "https://brand.naver.com/crowngoose/products/"
}
# Dictionary để ánh xạ lựa chọn từ giao diện sang tên spider thật
SPIDER_MAPPING = {
    'naver': 'Naver_spider',
    'coupang': 'Coupang_spider',
    'ohouse': 'Ohouse_spider',
}

@app.route('/')
def index():
    """Route chính, hiển thị trang web."""
    # --- THAY ĐỔI Ở ĐÂY ---
    # Truyền danh sách brand vào file template
    return render_template('index.html', naver_brands_data=NAVER_BRANDS_DATA)

# --- PHẦN CÒN LẠI CỦA FILE GIỮ NGUYÊN ---
@app.route('/run-spider', methods=['POST'])
def run_spider():
    """API endpoint để nhận yêu cầu chạy spider từ giao diện."""
    try:
        data = request.get_json()
        site = data.get('site')
        brand = data.get('brand')
        product_id = data.get('product_id')

        if not site or not product_id:
            return jsonify({'status': 'error', 'message': 'Site and Product ID are required.'}), 400

        spider_name = SPIDER_MAPPING.get(site)
        if not spider_name:
            return jsonify({'status': 'error', 'message': f'Invalid site selected: {site}'}), 400

        payload = {
            'project': PROJECT_NAME,
            'spider': spider_name,
            'product_id': product_id,
        }

        if site == 'naver':
            if not brand:
                return jsonify({'status': 'error', 'message': 'Brand is required for Naver.'}), 400
            payload['brand_name'] = brand

        schedule_url = f"{SCRAPYD_URL}/schedule.json"

        app.logger.info(f"Sending job to Scrapyd: {payload}")
        response = requests.post(schedule_url, data=payload)
        
        response.raise_for_status()
        scrapyd_response = response.json()

        if scrapyd_response.get('status') == 'ok':
            return jsonify({
                'status': 'success', 
                'message': 'Job scheduled successfully',
                'details': {
                    'project': PROJECT_NAME,
                    'spider': spider_name,
                    'jobid': scrapyd_response.get('jobid')
                }
            })
        else:
            return jsonify({'status': 'error', 'message': scrapyd_response.get('message', 'Unknown error from Scrapyd')})

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Could not connect to Scrapyd: {e}")
        return jsonify({'status': 'error', 'message': f'Could not connect to Scrapyd at {SCRAPYD_URL}. Is it running?'}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/run-sheet-spider', methods=['POST'])
def run_sheet_spider():
    """API endpoint để chạy spider product_list từ Google Sheet URL."""
    try:
        data = request.get_json()
        sheet_url = data.get('sheet_url')

        if not sheet_url:
            return jsonify({'status': 'error', 'message': 'Google Sheet URL is required.'}), 400

        # Payload để gọi spider `product_list`
        payload = {
            'project': PROJECT_NAME,
            'spider': 'product_list', # Tên spider được hard-code
            'sheet_url': sheet_url     # Truyền URL vào spider như một tham số
        }

        schedule_url = f"{SCRAPYD_URL}/schedule.json"
        app.logger.info(f"Sending Google Sheet job to Scrapyd: {payload}")
        
        response = requests.post(schedule_url, data=payload)
        response.raise_for_status()
        scrapyd_response = response.json()

        if scrapyd_response.get('status') == 'ok':
            return jsonify({
                'status': 'success',
                'message': 'Product list spider scheduled successfully from Google Sheet.',
                'details': {
                    'project': PROJECT_NAME,
                    'spider': 'product_list',
                    'jobid': scrapyd_response.get('jobid')
                }
            })
        else:
            return jsonify({'status': 'error', 'message': scrapyd_response.get('message', 'Unknown error from Scrapyd')})

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Could not connect to Scrapyd: {e}")
        return jsonify({'status': 'error', 'message': f'Could not connect to Scrapyd at {SCRAPYD_URL}. Is it running?'}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)