# db_manager.py
from fastapi import Depends, Request

# Function to initialize and connect the database manager
async def connect_db(db_manager, MONGO_URI: str, MONGO_DB_NAME: str):
    await db_manager.connect_all(MONGO_URI, MONGO_DB_NAME)
    if db_manager.mongo_manager is None:
        raise Exception("Failed to connect to MongoDB")
    else:
        print("Connected to MongoDB")

# Dependency function to get the db_manager instance
def get_db_manager(db_manager):
    def dependency():
        return db_manager
    return dependency

# Function to create the get_db_and_scheduler dependency
def create_db_scheduler_dependency(db_manager, scheduler):
    async def get_db_and_scheduler(request: Request):
        """Dependency to get DB manager, scheduler, and route path."""
        return {
            "db_manager": db_manager,
            "scheduler": scheduler,
            "route_path": request.url.path,
        }
    return get_db_and_scheduler