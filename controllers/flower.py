from fastapi import HTTPException

from models.schemas import ImageRequest
from openCV_method import find_flower_cv
from yolo_method import find_flower_yolo


async def find_flower_with_cv_controller(request: ImageRequest):
    try:
        if "," in request.image:
            b64img = request.image.split(",")[1]
        else:
            b64img = request.image

        result_base64 = find_flower_cv(b64img)
        return {"image": f"data:image/png;base64,{result_base64}"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image with cv: {str(e)}")


async def find_flower_with_yolo_controller(request: ImageRequest):
    try:
        if "," in request.image:
            b64img = request.image.split(",")[1]
        else:
            b64img = request.image

        response = find_flower_yolo(b64img)
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image with YOLO: {str(e)}")
