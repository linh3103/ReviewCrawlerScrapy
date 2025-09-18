# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Review Crawler UI"
    SCRAPYD_URL: str = "http://localhost:6800"
    SCRAPYD_PROJECT: str = "review_crawler"
    DRIVE_FOLDER_ID: str = "YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE"
    
    # Đường dẫn đến file credentials, tương đối với thư mục gốc dự án
    SERVICE_ACCOUNT_FILE: str = "credentials.json"
    GOOGLE_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    GOOGLE_SERVICES_CREDENTIALS: str = "google_services_credentials.json"

# Tạo một instance để các module khác có thể import và sử dụng
settings = Settings()