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
async def get_admin_by_email(email: str, dependencies: dict = Depends(get_db_and_scheduler), task_id: str = None):
    db_manager = dependencies["db_manager"]
    scheduler_instance = dependencies["scheduler"]
    route_path = dependencies["route_path"]

    async def get_admin_by_email_task(p_email: str, p_db_manager: DatabaseManager, task_id: str):
        from controllers.admin import get_admin_by_email_controller
        try:
            result = await get_admin_by_email_controller(p_email, p_db_manager)
            return result  # Return the actual result from the controller
        except HTTPException as e:  # Catch HTTPExceptions from the controller
            raise e # Re-raise to be handled by FastAPI
        except Exception as e:
            print(f"Task {task_id} failed: {e}")
            raise HTTPException(status_code = 500, detail = f"Internal Server Error: {e}")

    # 1. Create a future (CompletableFuture in Java terms)
    future = asyncio.Future()

    # 2. Add the task to the scheduler, passing the future
    await scheduler_instance.add_task(
        get_admin_by_email_task, email, db_manager,
        priority = 2,
        route_path = route_path,
        task_id = task_id,
        existing_future = future
    )

    # 3. Modify the Task.run() method to set the result on the future
    # (See below - VERY IMPORTANT)

    # 4. Await the future.  This blocks *this specific request handler*
    #    until the task completes, but it does *not* block the entire server.
    try:
        result = await future
        print(f"result after future: {result}")
        return result # return the actual result
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
