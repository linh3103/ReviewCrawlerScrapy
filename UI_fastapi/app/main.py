# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from ..routers import JobsRouter, DriveRouter
from .config import settings

# Tạo instance FastAPI
app = FastAPI(title=settings.PROJECT_NAME)


templates = Jinja2Templates(directory="templates")

# Gộp các router vào ứng dụng chính
app.include_router(JobsRouter.router)
app.include_router(DriveRouter.router)

# Route để phục vụ trang chủ (giao diện)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Bạn có thể truyền dữ liệu vào template ở đây nếu cần
    # Ví dụ: naver_brands_data
    return templates.TemplateResponse("index.html", {"request": request})