# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from ..routers import JobsRouter, DriveRouter, SharedRouter
from .config import settings

# Tạo instance FastAPI
app = FastAPI(title=settings.PROJECT_NAME)

APP_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.dirname(APP_DIR)

# Xây dựng đường dẫn đến thư mục static và templates từ APP_DIR
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Tạo instance FastAPI
app = FastAPI(title=settings.PROJECT_NAME)

# Cấu hình thư mục static và templates bằng đường dẫn tuyệt đối
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Gộp các router vào ứng dụng chính
app.include_router(JobsRouter.router)
app.include_router(DriveRouter.router)
app.include_router(SharedRouter.router)

# Route để phục vụ trang chủ (giao diện)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})