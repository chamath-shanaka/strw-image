from fastapi import APIRouter, Depends, status
from controllers.mobile import (
    create_user_controller,
    get_user_by_email_controller,
    get_user_by_user_id_controller,
    get_user_by_username_controller,
    # update_rover_ids_controller,
    register_rover_controller,
    update_rover_nickname_controller,
    get_flower_count_in_range_controller
)
from database import DatabaseManager
from db_manager import get_db_manager
from models.schemas import FlowerCountSummary
from models.userSchemas import UserModel
from datetime import datetime

router = APIRouter()



# Create user route
@router.post("/users/", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserModel, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await create_user_controller(user, db_manager)


# Get user by email route
@router.get("/users/email/{email}", response_model=UserModel)
async def get_user_by_email(email: str, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await get_user_by_email_controller(email, db_manager)


# Get user by userId route
@router.get("/users/user-id/{userId}", response_model=UserModel)
async def get_user_by_user_id(userId: int, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await get_user_by_user_id_controller(userId, db_manager)


# Get user by username route
@router.get("/users/username/{username}", response_model=UserModel)
async def get_user_by_username(username: str, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await get_user_by_username_controller(username, db_manager)


# Update roverIds route
# @router.put("/users/{userId}/roverIds", response_model=UserModel)
# async def update_rover_ids(userId: int, roverIds: List[int], db_manager: DatabaseManager = Depends(get_db_manager)):
#     return await update_rover_ids_controller(userId, roverIds, db_manager)


# register rover
@router.put("/users/{userId}/register-rover", response_model=UserModel)
async def register_rover(userId: int, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await register_rover_controller(userId, db_manager)


# update rover nickname
@router.put("/users/{userId}/rovers/{roverId}/update-nickname", response_model=UserModel)
async def update_rover_nickname(
        userId: int,
        roverId: int,
        nickname: str,
        db_manager: DatabaseManager = Depends(get_db_manager),
):
    return await update_rover_nickname_controller(userId, roverId, nickname, db_manager)


# get all pollination count of a user's rovers' in a given time rage
@router.get("/users/{userId}/get-flower-count", response_model=FlowerCountSummary)
async def get_flower_count_in_range(
        userId: int,
        start_date: datetime,
        end_date: datetime,
        db_manager=Depends(get_db_manager)
):
    return await get_flower_count_in_range_controller(userId, start_date, end_date, db_manager)