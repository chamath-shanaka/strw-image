from typing import List

from fastapi import APIRouter, status, Depends

from controllers.admin import create_admin_controller, get_admin_by_email_controller, get_all_admins_controller, \
    delete_admin_controller
from dependencies import get_db_and_scheduler
from models.userSchemas import AdminModel
from scheduler.runner import run_with_scheduler

router = APIRouter()




# create admin route
@router.post("/admins", response_model=AdminModel, status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminModel, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(create_admin_controller, admin, dependencies = dependencies)


# get an admin by email
@router.get("/admins/{email}", response_model=AdminModel, status_code=status.HTTP_200_OK)
async def get_admin_by_email(email: str, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(get_admin_by_email_controller, email, dependencies = dependencies)


# get all admins
@router.get("/admins", response_model=List[AdminModel])
async def get_all_admins(dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(get_all_admins_controller, dependencies = dependencies)


# delete admin
@router.delete("/admins/{email}", status_code=status.HTTP_200_OK)
async def delete_admin(email: str, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(delete_admin_controller, email, dependencies=dependencies)
