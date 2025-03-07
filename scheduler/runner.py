import asyncio
from typing import Callable

from fastapi import HTTPException


async def run_with_scheduler(controller_func: Callable, *args, dependencies: dict, priority: int = 2):
    """
    Runs a controller function using the scheduler.

    :param controller_func: The controller function to be executed.
    :param args: The arguments to be passed to the controller function.
    :param dependencies: `get_db_and_scheduler` containing db_manager, scheduler, and route_path.
    :param priority: priority of the controller function, lower means higher priority, default is 2.
    """
    db_manager = dependencies["db_manager"]
    scheduler_instance = dependencies["scheduler"]
    route_path = dependencies["route_path"]

    # creating a passable future for the API
    future = asyncio.Future()

    # add the task to the scheduler
    await scheduler_instance.add_task(
        controller_func, *args, db_manager, # the controller functions require db_manager
        priority = priority,
        route_path = route_path,
        task_id = None,
        existing_future = future # pass API's future
    )

    try:
        # await the future & return output
        result = await future
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
