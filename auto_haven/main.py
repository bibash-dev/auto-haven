from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from .config import BaseConfig
from auto_haven.routers.cars import router as cars_router

settings = BaseConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db = app.client[settings.MONGODB_NAME]

    try:
        # Ping the MongoDB server to check the connection
        await app.client.admin.command("ping")
        print("Pinged your deployment. You have successfully connected to MongoDB!")
        print("Mongo address:", settings.MONGODB_URL)
    except Exception as e:
        print("Failed to connect to MongoDB:", e)

    yield

    # Close the connection when the app shuts down
    app.client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(cars_router)
