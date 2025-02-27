from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from passlib.context import CryptContext

from database import DatabaseManager
from models.userSchemas import AdminModel




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



async def create_admin_controller(admin: AdminModel, db_manager: DatabaseManager):
    if db_manager.mongo_manager.db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB connection is not established"
        )
    print("MongoDB connection is established.")

    # Ensure email uniqueness
    existing_admin = await db_manager.mongo_manager.db['admins'].find_one({'email': admin.email})
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    print("Email uniqueness OK")

    # Hash the password
    if admin.password:
        hashed_password = hash_password(admin.password)
        admin.password = hashed_password

    # Add the created_at and updated_at
    admin.created_at = datetime.now()
    admin.updated_at = admin.created_at

    # insert to db
    admin_dict = admin.model_dump()
    await db_manager.mongo_manager.db['admins'].insert_one(admin_dict)
    return admin



async def get_admin_by_email_controller(email: str, db_manager: DatabaseManager):
    admin = await db_manager.mongo_manager.db['admins'].find_one({'email': email})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    return admin



async def get_all_admins_controller(db_manager: DatabaseManager) -> List[AdminModel]:
    admins_cursor = db_manager.mongo_manager.db['admins'].find()
    admins = await admins_cursor.to_list(length=None) # get all documents
    if not admins:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No admins found")

    # Convert MongoDB documents to AdminModel instances
    admin_models = []
    for admin_data in admins:
        admin_models.append(AdminModel(**admin_data))
    return admin_models