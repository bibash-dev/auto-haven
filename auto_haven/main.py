from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus
from .config import BaseConfig

settings = BaseConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.client = AsyncIOMotorClient(quote_plus(settings.DB_URL))
    app.db = app.client[quote_plus(settings.DB_NAME)]
    try:
        app.client.admin.command("ping")
        print("Pinged your deployment. You have successfully connected to MongoDB!")
        print("Mongo address:", quote_plus(settings.DB_URL))
    except Exception as e:
        print(e)
    yield
    app.client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "ready to go"}
