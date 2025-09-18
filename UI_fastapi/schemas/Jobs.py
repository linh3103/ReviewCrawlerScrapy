from pydantic import BaseModel, Field

class SpecificJobRequest(BaseModel):
    site: str
    brand: str | None = None
    product_id: str

class SheetJobRequest(BaseModel):
    sheet_url: str

class JobResponse(BaseModel):
    status: str
    message: str
    details: dict