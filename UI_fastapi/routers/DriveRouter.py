from fastapi import APIRouter, HTTPException
from ..services.DriveService import get_files

router = APIRouter(
    prefix="/api/drive",
    tags=["Drive"]
)

@router.get("/files")
async def load_files_from_drive():
    return get_files()