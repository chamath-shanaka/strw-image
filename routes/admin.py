from typing import List

from fastapi import APIRouter, status, Depends

from controllers.admin import create_admin_controller, get_admin_by_email_controller, get_all_admins_controller, \
    delete_admin_controller
from database import DatabaseManager
from db_manager import get_db_manager
from models.userSchemas import AdminModel

router = APIRouter()




# create admin route
@router.post("/admins", response_model=AdminModel, status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminModel, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await create_admin_controller(admin, db_manager)


# get an admin by email
@router.get("/admins/{email}", response_model=AdminModel, status_code=status.HTTP_200_OK)
async def get_admin_by_email(email: str, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await get_admin_by_email_controller(email, db_manager)


# get all admins
@router.get("/admins", response_model=List[AdminModel])
async def get_all_admins(db_manager: DatabaseManager = Depends(get_db_manager)):
    return await get_all_admins_controller(db_manager)


# delete admin
@router.delete("/admins/{email}", status_code=status.HTTP_200_OK)
async def delete_admin(email: str, db_manager: DatabaseManager = Depends(get_db_manager)):
    return await delete_admin_controller(email, db_manager)
