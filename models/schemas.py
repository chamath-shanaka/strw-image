from datetime import datetime
from typing import List

from pydantic import BaseModel

class ImageRequest(BaseModel):
    image: str
    rover_id: int = None

class Base64ImageInput(BaseModel):
    base64_string: str
    file_extension: str = "png"

class RoverData(BaseModel):
    initial_id: int
    rover_status: int
    user_id: int

class ImageData(BaseModel):
    id: int
    rover_id: int
    random_id: int
    battery_status: float
    temp: float
    humidity: float
    blob_url: str = ''
    image_data: str
    created_at: datetime

class RoverPollinationData(BaseModel):
    rover_id: int
    rover_nickname: str
    flower_count: int

class FlowerCountSummary(BaseModel):
    net_count: int
    by_rover: List[RoverPollinationData]