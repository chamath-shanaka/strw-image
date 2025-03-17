import asyncio

from fastapi import APIRouter, Depends, HTTPException

from controllers.flower import find_flower_with_cv_controller, find_flower_with_yolo_controller
from dependencies import get_db_and_scheduler
from models.schemas import ImageRequest

router = APIRouter()


@router.post("/find-flower-cv")
async def find_flower_with_cv(request: ImageRequest):
    return await find_flower_with_cv_controller(request)


@router.post("/find-flower-yolo")
async def find_flower_with_yolo(request: ImageRequest, dependencies: dict = Depends(get_db_and_scheduler)):
    scheduler_instance = dependencies["scheduler"]
    # route_path = dependencies["route_path"]

    future = asyncio.Future()

    await scheduler_instance.add_task(
        find_flower_with_yolo_controller, request,
        priority = 1,
        # route_path = route_path,
        task_id = None,
        existing_future = future
    )

    try:
        response = await future
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
