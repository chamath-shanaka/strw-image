from typing import List

from fastapi import APIRouter, HTTPException, status, Depends

from controllers.mobile import get_rover_image_data_controller
from db_manager import get_db_manager
from dependencies import get_db_and_scheduler
from scheduler.runner import run_with_scheduler
from upload_image import upload_base64_image
from models.schemas import RoverData, ImageData
from database import DatabaseManager
from db_con import get_db_connection

router = APIRouter()


@router.post("/rovers/")
def add_rover(data: RoverData):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO rovers (initial_id, rover_status, user_id)
        VALUES (%s, %s, %s)
        RETURNING rover_id, created_at;
        """

        cursor.execute(insert_query, (data.initial_id, data.rover_status, data.user_id))
        result = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return {"rover_id": result[0], "created_at": result[1]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add rover: {str(e)}")


@router.post("/rover/trigger/")
async def run_trigger(db_manager: DatabaseManager = Depends(get_db_manager)):
    try:
        # Get database connection
        connection = get_db_connection()  # Ensure this supports async if necessary
        cursor = connection.cursor()

        # SQL query to get the count of operations
        get_count_query = "SELECT COUNT(*) FROM operations;"
        cursor.execute(get_count_query)
        result1 = cursor.fetchone()

        if result1 is None or result1[0] <= 0:
            return {"message": "No operations found."}

        count = result1[0]
        for _ in range(count):
            # SQL query to fetch the oldest operation
            get_data_query = """
            SELECT id, rover_id, random_id, battery_status, temp, humidity, 
                   result_image, image_data, created_at
            FROM operations
            ORDER BY created_at ASC
            LIMIT 1;
            """
            cursor.execute(get_data_query)
            result2 = cursor.fetchone()

            if result2 is None:
                break

            # Map query result to ImageData model
            data = ImageData(
                id=result2[0],
                rover_id=result2[1],
                random_id=result2[2],
                battery_status=result2[3],
                temp=result2[4],
                humidity=result2[5],
                result_image=result2[6],
                image_data=result2[7],
                created_at=result2[8],
            )

            # Remove "data:image/png;base64," from result_image string
            updated_result_image = data.result_image.replace("data:image/png;base64,", "")
            blob_url = upload_base64_image(updated_result_image, "jpeg")

            # Add data to MongoDB using db_manager
            mongo_data = {
                "id": data.id,
                "rover_id": data.rover_id,
                "random_id": data.random_id,
                "battery_status": data.battery_status,
                "temp": data.temp,
                "humidity": data.humidity,
                "blob_url": blob_url,
                "image_data": data.image_data,
                "created_at": data.created_at,
            }

            await db_manager.add_to_mongo(mongo_data)

            # Delete the record from Postgres
            delete_data_query = "DELETE FROM operations WHERE id = %s;"
            cursor.execute(delete_data_query, (data.id,))

        # Commit the transaction and close the SQL connection
        connection.commit()
        cursor.close()
        connection.close()

        return {"message": "Trigger executed and data added to MongoDB successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run trigger: {str(e)}")



# get recoded image ddata from mongo
@router.get("/rovers/flower-images/{rover_id}", response_model=List[ImageData])
async def get_rover_image_data_original_route(rover_id: int, dependencies: dict = Depends(get_db_and_scheduler)):
    return await run_with_scheduler(get_rover_image_data_controller, rover_id, dependencies=dependencies)
