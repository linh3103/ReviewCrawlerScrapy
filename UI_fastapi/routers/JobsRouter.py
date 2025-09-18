# app/routers/jobs.py
from fastapi import APIRouter, HTTPException
from ..schemas import JobResponse, SheetJobRequest, SpecificJobRequest
from ..services.SpecificJobService import schedule_specific_job
from ..services.SheetJobService import schedule_sheet_job

router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)

SPIDER_MAPPING = {
    'naver': 'Naver_spider',
    'coupang': 'Coupang_spider',
    'ohouse': 'Ohouse_spider',
}

@router.post("/specific", response_model=JobResponse)
async def run_specific_job(request: SpecificJobRequest):
    spider_name = SPIDER_MAPPING.get(request.site)
    if not spider_name:
        raise HTTPException(status_code=400, detail="Invalid site selected.")

    params = {"product_id": request.product_id}
    if request.brand:
        params["brand_name"] = request.brand
        
    try:
        result = schedule_specific_job(spider_name, params)
        if result.get("status") == "ok":
            return {
                "status": "success",
                "message": "Job scheduled successfully",
                "details": result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message"))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    

@router.post("/sheet", response_model=JobResponse)
async def run_sheet_job(request: SheetJobRequest):
    sheet_url = request.sheet_url

    try:
        result = schedule_sheet_job(sheet_url)
        if result.get("status") == "ok":
            return {
                "status": "success",
                "message": "Job scheduled successfully",
                "details": result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message"))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
