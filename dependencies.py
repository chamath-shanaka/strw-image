from fastapi import Request, Depends
from database import DatabaseManager
from scheduler import CustomScheduler

# create single instances here
db_manager = DatabaseManager()
scheduler = CustomScheduler()


# function to initialize and connect the database manager
async def connect_db(MONGO_URI: str, MONGO_DB_NAME: str):
    await db_manager.connect_all(MONGO_URI, MONGO_DB_NAME)
    if db_manager.mongo_manager is None:
        raise Exception("Failed to connect to MongoDB")
    else:
        print("Connected to MongoDB")


# Dependency function to get the db_manager instance
def get_db_manager():
    return db_manager


# Dependency to get both db_manager and scheduler
async def get_db_and_scheduler(request: Request):
    """Dependency to get DB manager, scheduler, and route path."""
    return {
        "db_manager": db_manager,
        "scheduler": scheduler,
        "route_path": request.url.path,
    }


# For shutdown
async def shutdown_resources():
    await scheduler.stop()
    await db_manager.close_all()
    print("🛑 DB connections closed\n")


# Start scheduler
async def start_scheduler():
    await scheduler.start()

    # Set custom priority paths
    scheduler.set_custom_priority_paths({
        "/users/{userId}/get-flower-count": 1
    })