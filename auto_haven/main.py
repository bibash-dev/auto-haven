from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from .config import BaseConfig
from auto_haven.routers.cars import router as cars_router
from auto_haven.routers.users import router as users_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = BaseConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db = app.client[settings.MONGODB_NAME]

    try:
        await app.client.admin.command("ping")
        logger.info(
            "Pinged your deployment. You have successfully connected to MongoDB!"
        )
        logger.info(f"MongoDB address: {settings.MONGODB_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to MongoDB")

    yield

    app.client.close()
    logger.info("MongoDB connection closed.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cars_router, prefix="/api/v1/cars", tags=["cars"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
