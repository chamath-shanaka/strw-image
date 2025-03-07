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
from dependencies import get_db_and_scheduler
from models.schemas import FlowerCountSummary
from models.userSchemas import UserModel
from datetime import datetime

from scheduler.runner import run_with_scheduler

router = APIRouter()



# Create user route
@router.post("/users/", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserModel, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(create_user_controller, user, dependencies=dependencies)


# Get user by email route
@router.get("/users/email/{email}", response_model=UserModel)
async def get_user_by_email(email: str, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(get_user_by_email_controller, email, dependencies=dependencies)


# Get user by userId route
@router.get("/users/user-id/{userId}", response_model=UserModel)
async def get_user_by_user_id(userId: int, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(get_user_by_user_id_controller, userId, dependencies=dependencies)


# Get user by username route
@router.get("/users/username/{username}", response_model=UserModel)
async def get_user_by_username(username: str, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(get_user_by_username_controller, username, dependencies=dependencies)


# Update roverIds route
# @router.put("/users/{userId}/roverIds", response_model=UserModel)
# async def update_rover_ids(userId: int, roverIds: List[int], db_manager: DatabaseManager = Depends(get_db_manager)):
#     return await update_rover_ids_controller(userId, roverIds, db_manager)


# register rover
@router.put("/users/{userId}/register-rover", response_model=UserModel)
async def register_rover(userId: int, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(register_rover_controller, userId, dependencies=dependencies)


# update rover nickname
@router.put("/users/{userId}/rovers/{roverId}/update-nickname", response_model=UserModel)
async def update_rover_nickname(
        userId: int,
        roverId: int,
        nickname: str,
        dependencies: dict = Depends(get_db_and_scheduler),
):
    return await run_with_scheduler(
        update_rover_nickname_controller, userId, roverId, nickname,
        dependencies=dependencies
    )


# get all pollination count of a user's rovers' in a given time rage
@router.get("/users/{userId}/get-flower-count", response_model=FlowerCountSummary)
async def get_flower_count_in_range(
        userId: int,
        start_date: datetime,
        end_date: datetime,
        dependencies: dict = Depends(get_db_and_scheduler)
):
    return await run_with_scheduler(
        get_flower_count_in_range_controller, userId, start_date, end_date,
        dependencies = dependencies
    )
