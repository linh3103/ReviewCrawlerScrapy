import requests
import json
import time
from requests.exceptions import Timeout, RequestException, HTTPError

def fetch_coupang_reviews():
    """
    Hàm này gọi API review của Coupang cho một sản phẩm cụ thể
    và in ra kết quả trả về với debug info và timeout.
    """
    
    # URL của API, chứa các tham số như productId, page, size,...
    api_url = "https://www.coupang.com/next-api/review?productId=6287221036&page=1&size=10&sortBy=DATE_DESC&ratingSummary=true&ratings=&market="

    # Tạo dictionary chứa các header cần thiết
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6,fr-FR;q=0.5",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Cookie": "x-coupang-target-market=KR; x-coupang-accept-language=ko-KR; PCID=17570571490698272908560; _fbp=fb.1.1757057117426.553913826936583264; sid=35b05bd192a24cf2a37041f3fb6a8f9729813452; bm_ss=ab8e18ef4e; bm_mi=E7C5B3E56839887665B91C9C97397168~YAAQRvkgFxdt6UuZAQAAhgBaXx3Vlw1+7DCO+PQ7Vmhmsg/m4/EzTTJ8aSlE8Q7ejDVk6d1aWmWDR09kpDPm/JmM0yBbKH3BbL3U+6BJZRvdzgBKmofh8h6geSCo8NL+Z3qIUS2j7c+KwWfb74i/9VQD26wrdekW1QwxZQ9uSWHnx6entru7Ometm2b2eWYdXiV4asMXQIER4cwy2EvJtchNvrY/TUOE1Z7ZtGQ0VxU8AjchQ0rUE3U0wasLl40UdvomiJPSQzRFEA1R+e3cj3s+RfqCV58sMQERLWpvOZP/9c7lECPDIrZyW+OKXYA=~1; ak_bmsc=269CC7CDA5738209766BDC7178084CF1~000000000000000000000000000000~YAAQRvkgFz5t6UuZAQAA3wpaXx2B5XeSZ7K0qjPYmI8nvnwVrrF2s80IU5BW1CEOC6BndXWXr0KKI/6DzmcCsKL0o0rPCAuo2mjgbTHiPNJ110bW5RK545AteVkjWQeebswg8n0nO/r09N9l/zJ1NWk2l5be9U1lAau66jOYOmQv7Tnfh9RahAlIzY0woRqXDufsW3YmSrHrp+hfS8dMq6JuQVfXzi6xUJ6z1thjtBnPSjrmavayr3XRwj/LAZ5YE4kqbSolE5E2V7pDPooX/Ie695B5D/CzeiV4MPuFWWMVyqVs3Z8bmZvCMbESFNc+yCVaTLfWZlbsIeXOkD67f3NJfh4YdVCJYQmpN4TAnqmbgxSvmm86kxAAfsmFXdZrXXq2jobpgra0P3FzdTCYjapUUgb+N9t4ZSRarT/nPhNMK+BSiaf8fnzBHxBUTlXFcIF5QkHSVNFxendudGYi6Ia35L2rrHZWix3hc4QJLD2ClQ==; bm_sc=4~1~839782533~YAAQRvkgF1Ft6UuZAQAAvhZaXwWbe9wQlfoYzC1zDLCY7uwESIWRy8sKih96SawVvq+fAj5mMX41lREt7Mzsm+nTR6PXCPN/OyNJjafcB/50YkbO+CeRuoNTndYKdIr9g3DpJSJxkaHejkyuC9yQteCOuaWInAvENF34HwyaB/NExHFPLRqgfdayZKSVOJWXwLB4gMZJBa2JVZ/94fgYJlt7LJ5GW/dUrZnwOzPnArXs1HPM+mZNdfKiU2mKFSycOtQE80kGn7fKCZ1QjE89GCi+nFTuq4DpdMFBtTCyE9NY3boeGNAZXlkR0jth+G42ts8pJQ4DDE85sw7dq79i7UkMOwGnbhuH7REovPe8S6YlFgrTufHoZzXjVuQZnYROqhufqfVpA42OVJTUCTLmu6WZSZJCP28BL6vJl7GGceC0onAKaIA4jqzXtbNue8Sayl8hZAcyY57CClAypXztD71hYqH5JVAosksmYQCZg6CDG7kqErt+kx6Q1zFA1JBL8kzSz680xq5+y1aq/MSJ6lAPtwrKoYTupWgFcGGkicLR9Ph0SfkWurSnYtIcCBAhuBt7FYATeXWUxI3NnbXyB4sdSHIitEE7OnH0gJFpz5SMG/K4c0skTQDJ3HhluUuYIg2Pa0E9V0vKIZUiKvUPgFTb0HesELvi8gfeFSF0dceyQPa+26aRj6U6CWQGaqMhPwZhPEWN+upNaxU1MwJ02x5grGohgp/2ukDSupaygorgBA==; _abck=B49CCEC5A7603A01C6862FA50287ECEA~0~YAAQRvkgF1Rt6UuZAQAA/hZaXw5QW6xun/KvOqhPXSbnjpdxOqPgPU9v636rDIoga4+UhrSHjPknHvIWnXivK1MNoymEDS8ohmsjj6jXbL6VZWZrVULUGKFZQnxrroLIPS+HI2vMxt8zBRgFZhNQNRTQjTE2Gz3EgFKnW3xsVclF2GeMjzZFjIrEaMvGB4sy7DmwFmpnvCHdHS3PclO1I2wGPEfl7+cdZQPvL/eFiQsk+707RwGkO1TfMhdJd0j+Lpq2v6kJsBSISuEA4wJVrprMtfLqXYIltlbxZ2fTXj5cM0S977SFnZAB+Wti7C1QBtdWXZCm3HFArFEKdE7PhoTpdoG807i7kPBTpsmr6xXWurrmAeZsp8msJaRP6o6jKFoO4J8dXfC5FE01GEQOr0/rnhmsrmDsLSyxvTQy43WmP90XlShkGB9LbRlqcJG2tv67wmkWd/cBAmuPihs4TtIoF8LgLqZRn/WSY8nYzy15WCv6eRmIl5fv5hmWm6IRQDVE7AnnO8v38K58zEohC6m9EFaGhrISdRgPkAQUYtZG9me5w16Q4mBVCpWqv6delC3cuZ78cUzXYUX3am0nn6twDq3vjOGWYkoJqEHyROuOSexDzl3vdg==~-1~-1~1758244959~AAQAAAAE%2f%2f%2f%2f%2f0oaut2HJnPVZbZkxnAVJ%2fRzV150uxGXFmrcH1bybwT4QYuLXbg90XnLjYDI6LubNBKQMfdMCUnItoK6UxzhEZ7EH84iB97jzO6a~-1; bm_so=32BB9573F48EA25939CDAAE044F43764DD858B64A09D3A22F17271DF3401F50E~YAAQRvkgF6Rx6UuZAQAAn6BbXwUiezhiuv/kPDn7Btjp6qM4RNM3bvY3RlZyuX74RsGwyZIHvSxl8FK2DwYPsUGlmxk8Lkw4F2ld+W3Zws2R4aVzYEk7vco0I8feJ8t6ESsKodKc2l0isIqriQMTPHKqXh1xrWrxU1r3E9T92G8AT1YkmLs4uS8kPG50/CLNLHOyrUG53tCMoDf+AeWsm9iU9tVonLw7KiVmPw6ZNUzVPHAPJW9L8D/Oeyd89lwxiVLLYe5sJQGADQXYBa0JH5tRrKMnEjrdM15bHXMtYvCUvhhMLfN4FEJWv4SHSgRgai4Nff1Sdesdo9PLqCK9mcj4LWaIiO+S5ijw0k0Ze/3ybr3vvw0R0ye6ek6PLXfyLhO9qsyEppPYPPBgYchcNQKNEbvLPU7Gb1WvNOeAGkqPGhMsni/M3b4jTnludR+dH6IqKhKSAPm/Qt80LW0M; bm_sz=876D59E0212445B84416AD530724A461~YAAQRvkgF6Zx6UuZAQAAn6BbXx2GXGNPWUHLvtChL73LHkYwbhGN5Y88rh+TxkhbyByy5qTHFBB0R5SNFV8xhDxdVugQtmn+roCH+3it4KFxi5DA/9PtlqAwLcQf3oPkpdBsLs5YLI/nnZHsznGfpwI8bY9rsgAcyr6gFGE3tfbZOsWGZAnrpeGBxq+f+Zp1liPkTQH/itfkt0BZPYfv0l4z4Y9XAJAvNpyUXUnDry4x1pDonGF/m6M0J6IIWUcwQ0hTrcFUAeXHRvOHQ6/TAOPIBLsDMOIaruAsSMxW37kXxhYUNs80ZuPUpiC1VPDgxcyGFYDFoWWWoJBXfGzYbZ3xSx51A2625QalaSEOgllnrIwwU9aL6fiOR3ouded/+2GrDHMVS7dpMOgO/SOrYpxtAp2cnKeqT3YDmxgkW2t7onX8uZm+nAaxWCdTL0D4ZgSV6lP3pMpjEbxfpav6IRVIkg==~4536388~3617840; cto_bundle=112BG19pUG5nUHByWjJRVUt3cHA2dCUyRjJ0R3ZPdW1RODVidyUyRm8zcGtRViUyRkVoWTJlSURRMlBBQTJoUlJQa2RyS1dvaEtyckFVcSUyRkxEdXJZcmhGNURpUHdZSmd0eldjMHhGMDZBV1AzdGVxN05ySExBSjE3UTZUd1JWRzdUOEtsNzFjcjlqN3ozZmkzc2Q3NzRJRUMlMkZRUDJUd2ElMkZBczhVSGFNOFA3eHh2NmJ1eGpZUzNmUmlsV1cyc2FTWDlZc3lFTCUyQkxuWFZ5TDRaSHo5T1NQeWtqVlFMMlk2Y3Qwb0pIanNEUzZOOVpqaW1VYjFBc0ZJUlBOc1FxVGtJcnJDdVdTWUJlZzRDVkFGV1F5Y1prcUxodER1emx0TzQ5UnladFJ6RVF4NW9vYWZ3Ym9nR2lSajFPa2NhQmQxaUhhd051bEt3aUlG; bm_lso=32BB9573F48EA25939CDAAE044F43764DD858B64A09D3A22F17271DF3401F50E~YAAQRvkgF6Rx6UuZAQAAn6BbXwUiezhiuv/kPDn7Btjp6qM4RNM3bvY3RlZyuX74RsGwyZIHvSxl8FK2DwYPsUGlmxk8Lkw4F2ld+W3Zws2R4aVzYEk7vco0I8feJ8t6ESsKodKc2l0isIqriQMTPHKqXh1xrWrxU1r3E9T92G8AT1YkmLs4uS8kPG50/CLNLHOyrUG53tCMoDf+AeWsm9iU9tVonLw7KiVmPw6ZNUzVPHAPJW9L8D/Oeyd89lwxiVLLYe5sJQGADQXYBa0JH5tRrKMnEjrdM15bHXMtYvCUvhhMLfN4FEJWv4SHSgRgai4Nff1Sdesdo9PLqCK9mcj4LWaIiO+S5ijw0k0Ze/3ybr3vvw0R0ye6ek6PLXfyLhO9qsyEppPYPPBgYchcNQKNEbvLPU7Gb1WvNOeAGkqPGhMsni/M3b4jTnludR+dH6IqKhKSAPm/Qt80LW0M^1758241402617; bm_s=YAAQRvkgF8tx6UuZAQAAP6hbXwTWijAZC1tk5fXWyFagYCltu19uDO0jmt4dwtk9z6gt6pu5J9L5K3QUYTMOrZRQzwdISAuMWqaV5/5c8QJWXaCRzBeySMItDbvpEOcGDyX7BUK7lfQjd/1ZbRLfMsBYG6uJspotg2F9jtz2ndVTiuqxLrb3BXVuE1c4BZGrEcxLd5EiSPkkRXXv9zBG2V8HIN/bhgBJYtZymfyf6zfeooMTHPisweHdlhYYTvrPB2EMLrQrO5lO0HxpJvYZpj5K6tBig4oUdVIdyBxYg90cKXjAPF7lJaq9TZbsZGJcaJ0eue2zJJP8QUkkL5znGTXdHtWL/1xiq1GmTZsBecy5PDzaUPxx/FogDQF4/JwYPxWPx4uZlR/Jr1tRKP/Pa2PWi6KIIrgkawzXLk3BWiKvAaTt1GMw97LAPetiR0CirvZBGR+2NIf9vkQjimqCyTxSoN445zGHU0TEvpZ88yeRftx83gI7ZpRSEX6SHrdjmX5cYubRONCExyTqfNAlCzOv+tNtWbkLdaPZVLvAs1bllvmXicD9fNDOSovC6+cAEuEdzPbYRA==; bm_sv=DA2A01C245A931A0603C0F0F80978835~YAAQjgqrcTKh3UyZAQAASfFbXx16WPTkCLKH/pHCItQhkqOrVQO6qdWbnfvQKljBboEsseiC2xzfnyQNhLctIY8c1TmsW7+WhxnabXHI0hUJJHj0BxCloSVMWAO4lsBInKSzt1yv+ab2KHpqJb75m2ySh0jEQERkOPgohZZ5TXrJUSmlhUl4ns/Se1ac61V4i0Y1g47tEKd9zbMDC6OiZ7AABQM/innO5cNiCk72fQNA794MB7umg+RXAjbdeNyVEvI=~1",
        "Priority": "u=1, i",
        "Sec-Ch-Ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",               
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Referer": "https://www.coupang.com/vp/products/6287221036"
    }

    print("="*60)
    print("COUPANG REVIEWS FETCHER - DEBUG MODE")
    print("="*60)
    
    print(f"🌐 URL đích: {api_url}")
    print(f"⏰ Timeout: 60 giây")
    print(f"📊 Số headers: {len(headers)}")
    print("\n📋 DANH SÁCH HEADERS:")
    print("-" * 30)
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("BẮT ĐẦU GỬI REQUEST...")
    print("="*60)

    # Ghi lại thời gian bắt đầu
    start_time = time.time()
    
    try:
        print(f"🚀 Bắt đầu request lúc: {time.strftime('%H:%M:%S')}")
        
        # Thực hiện yêu cầu GET với timeout 60 giây
        response = requests.get(
            api_url, 
            headers=headers, 
            timeout=60  # Timeout 60 giây
        )
        
        # Tính toán thời gian phản hồi
        response_time = time.time() - start_time
        
        print(f"✅ Nhận được phản hồi sau: {response_time:.2f} giây")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📦 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Content-Length: {response.headers.get('Content-Length', 'N/A')} bytes")
        print(f"🔒 Server: {response.headers.get('Server', 'N/A')}")
        
        # Debug response headers
        print(f"\n🔍 RESPONSE HEADERS (top 10):")
        print("-" * 30)
        for i, (key, value) in enumerate(response.headers.items()):
            if i < 10:  # Chỉ hiện 10 headers đầu
                print(f"  {key}: {value}")
            else:
                print(f"  ... và {len(response.headers) - 10} headers khác")
                break

        # Kiểm tra status code
        response.raise_for_status()

        # Kiểm tra content type
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            print(f"⚠️  CẢNH BÁO: Response không phải JSON (Content-Type: {content_type})")
        
        print(f"\n📄 Response Text Length: {len(response.text)} ký tự")
        
        # Preview response text (100 ký tự đầu)
        if len(response.text) > 100:
            preview = response.text[:100] + "..."
        else:
            preview = response.text
            
        print(f"👀 Preview Response: {preview}")

        # Thử parse JSON
        print("\n🔄 Đang parse JSON...")
        data = response.json()
        print("✅ Parse JSON thành công!")
        
        # Thông tin về JSON data
        if isinstance(data, dict):
            print(f"📊 JSON Object với {len(data)} keys:")
            for key in list(data.keys())[:5]:  # Hiện 5 keys đầu
                print(f"  - {key}: {type(data[key])}")
            if len(data) > 5:
                print(f"  ... và {len(data) - 5} keys khác")
        elif isinstance(data, list):
            print(f"📊 JSON Array với {len(data)} items")
            
        print("\n" + "="*60)
        print("KẾT QUẢ CUỐI CÙNG:")
        print("="*60)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    except Timeout:
        elapsed_time = time.time() - start_time
        print(f"⏰ TIMEOUT: Request bị hủy sau {elapsed_time:.2f} giây (> 60 giây)")
        print("🔄 Thử lại với timeout nhỏ hơn hoặc kiểm tra kết nối mạng")
        
    except HTTPError as http_err:
        elapsed_time = time.time() - start_time
        print(f"❌ HTTP ERROR sau {elapsed_time:.2f} giây: {http_err}")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        # Cố gắng hiển thị response body để debug
        try:
            print(f"📝 Response Body: {response.text[:500]}...")
        except:
            print("📝 Không thể đọc response body")
            
    except RequestException as req_err:
        elapsed_time = time.time() - start_time
        print(f"🌐 CONNECTION ERROR sau {elapsed_time:.2f} giây: {req_err}")
        print("🔧 Kiểm tra:")
        print("  - Kết nối internet")
        print("  - Firewall/proxy settings") 
        print("  - DNS resolution")
        
    except json.JSONDecodeError as json_err:
        elapsed_time = time.time() - start_time
        print(f"📄 JSON DECODE ERROR sau {elapsed_time:.2f} giây: {json_err}")
        print("🔍 Response không phải JSON hợp lệ")
        
        # Hiển thị một phần response để debug
        try:
            if len(response.text) > 200:
                print(f"📝 Response Preview: {response.text[:200]}...")
            else:
                print(f"📝 Full Response: {response.text}")
        except:
            print("📝 Không thể đọc response text")
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"💥 UNEXPECTED ERROR sau {elapsed_time:.2f} giây: {type(e).__name__}: {e}")
        
    finally:
        total_time = time.time() - start_time
        print(f"\n⏱️  Tổng thời gian thực thi: {total_time:.2f} giây")
        print(f"🏁 Kết thúc lúc: {time.strftime('%H:%M:%S')}")
        print("="*60)


# Chạy hàm chính khi file được thực thi
if __name__ == "__main__":
    fetch_coupang_reviews()