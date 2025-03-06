from fastapi import APIRouter

from controllers.flower import find_flower_with_cv_controller, find_flower_with_yolo_controller
from models.schemas import ImageRequest

router = APIRouter()

@router.post("/find-flower-cv")
async def find_flower_with_cv(request: ImageRequest):
    return await find_flower_with_cv_controller(request)

@router.post("/find-flower-yolo")
async def find_flower_with_yolo(request: ImageRequest):
    return await find_flower_with_yolo_controller(request)
