import requests
import json

def fetch_coupang_reviews():
    """
    Hàm này gọi API review của Coupang cho một sản phẩm cụ thể
    và in ra kết quả trả về.
    """
    
    # URL của API, chứa các tham số như productId, page, size,...
    api_url = "https://www.coupang.com/next-api/review?productId=6287221036&page=1&size=10&sortBy=DATE_DESC&ratingSummary=true&ratings=&market="

    # Tạo dictionary chứa các header cần thiết
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Sec-Ch-Ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        # Thêm Referer một cách chính xác
        "Referer": "https://www.coupang.com/vp/products/6287221036"
    }

    print(f"Đang gửi yêu cầu GET tới: {api_url}")
    print("Sử dụng headers:")
    # In ra các header để kiểm tra
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print("-" * 30)

    try:
        # Thực hiện yêu cầu GET với URL và headers đã định nghĩa
        response = requests.get(api_url, headers=headers)

        # Kiểm tra nếu request không thành công (status code không phải 2xx)
        # Sẽ tự động ném ra một exception nếu có lỗi HTTP (ví dụ: 403, 404, 500)
        response.raise_for_status()

        # Nếu request thành công, chuyển đổi kết quả từ text sang dictionary Python (JSON)
        data = response.json()

        # In kết quả ra màn hình với định dạng đẹp mắt (indent=2)
        # ensure_ascii=False để hiển thị đúng các ký tự tiếng Hàn
        print("Yêu cầu thành công! Dữ liệu trả về:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

    except requests.exceptions.HTTPError as http_err:
        print(f"Lỗi HTTP xảy ra: {http_err}")
        print(f"Nội dung phản hồi (nếu có): {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"Lỗi kết nối xảy ra: {err}")
    except json.JSONDecodeError:
        print("Không thể giải mã JSON từ phản hồi. Phản hồi không phải là JSON hợp lệ.")
        print(f"Nội dung phản hồi: {response.text}")


# Chạy hàm chính khi file được thực thi
if __name__ == "__main__":
    fetch_coupang_reviews()