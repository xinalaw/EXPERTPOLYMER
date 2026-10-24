"""Single synthetic SEM scene for prototype demonstrations."""
import base64
from io import BytesIO

from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import get_current_user
from expert_system.sem_generator import generate_yolo_scene

router = APIRouter(prefix="/api", tags=["Image Generation"])


@router.post("/generate", dependencies=[Depends(get_current_user)])
def generate_image():
    image, _, _ = generate_yolo_scene()
    output = BytesIO()
    image.save(output, format="PNG")
    return {"image": base64.b64encode(output.getvalue()).decode("ascii")}
