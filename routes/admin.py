import asyncio
from typing import List

from fastapi import APIRouter, status, Depends, HTTPException

from controllers.admin import create_admin_controller, get_admin_by_email_controller, get_all_admins_controller, \
    delete_admin_controller
from database import DatabaseManager
from db_manager import get_db_manager
from dependencies import get_db_and_scheduler
from models.userSchemas import AdminModel

router = APIRouter()




# create admin route
@router.post("/admins", response_model=AdminModel, status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminModel, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await create_admin_controller(admin, db_manager)


# get an admin by email
@router.get("/admins/{email}", response_model=AdminModel, status_code=status.HTTP_200_OK)
async def get_admin_by_email(email: str, dependencies: dict = Depends(get_db_and_scheduler)):
    db_manager = dependencies["db_manager"]
    scheduler_instance = dependencies["scheduler"]
    route_path = dependencies["route_path"]

    # create a compatible future for the API
    future = asyncio.Future()

    # add the task to the scheduler, pass API's future
    await scheduler_instance.add_task(
        get_admin_by_email_controller, email, db_manager,
        priority = 2,
        route_path = route_path,
        task_id = None,
        existing_future = future
    )

    # await for the future
    try:
        result = await future
        return result # return the result of controller
    except HTTPException as e:
        raise e #re raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get all admins
@router.get("/admins", response_model=List[AdminModel])
async def get_all_admins(db_manager: DatabaseManager = Depends(get_db_manager)):
    return await get_all_admins_controller(db_manager)


# delete admin
@router.delete("/admins/{email}", status_code=status.HTTP_200_OK)
async def delete_admin(email: str, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await delete_admin_controller(email, db_manager)
