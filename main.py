from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import MONGO_URI, MONGO_DB_NAME
from database import DatabaseManager
from db_manager import connect_db
from demo_page import demo_page
from routes import flower, health, rover, mobile, admin

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(flower.router)
app.include_router(health.router)
app.include_router(rover.router)
app.include_router(mobile.router)
app.include_router(admin.router)

# DB connection
db_manager = DatabaseManager()

@app.on_event("startup")
async def startup_db():
    # await db_manager.connect_all(MONGO_URI, MONGO_DB_NAME)
    # if db_manager.mongo_manager is None:
    #     raise Exception("IN MAIN Failed to connect to MongoDB")
    # else:
    #     print("IN MAIN Connected to MongoDB")

    await connect_db(MONGO_URI, MONGO_DB_NAME)

@app.on_event("shutdown")
async def shutdown_db():
    await db_manager.close_all()
    print("DB connections closed")


@app.get("/", response_class=HTMLResponse)
async def root():
    return demo_page()