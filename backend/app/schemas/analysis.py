from datetime import datetime
from pydantic import BaseModel
from app.schemas.ml_result import MLResultDataSchema


class AnalysisResultResponseSchema(BaseModel):
    id: int
    image_path: str
    processed_image_path: str | None = None
    original_filename: str
    result: str
    result_data: MLResultDataSchema | None = None
    confidence: float
    width: int | None = None
    height: int | None = None
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
