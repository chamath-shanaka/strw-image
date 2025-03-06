from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import MONGO_URI, MONGO_DB_NAME
from demo_page import demo_page
from dependencies import start_scheduler, shutdown_resources, connect_db
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

## routes
app.include_router(flower.router)
app.include_router(health.router)
app.include_router(rover.router)
app.include_router(mobile.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup_db():
    await connect_db(MONGO_URI, MONGO_DB_NAME)
    await start_scheduler()

@app.on_event("shutdown")
async def shutdown_db():
    await shutdown_resources()

@app.get("/", response_class=HTMLResponse)
async def root():
    return demo_page()
