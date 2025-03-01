import logging

from contextlib import asynccontextmanager
from fastapi_cors import CORS
from fastapi import FastAPI, HTTPException

from .database import initialize_database
from .config import BaseConfig

from auto_haven.routers.cars import router as cars_router
from auto_haven.routers.users import router as users_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = BaseConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing database...")
        await initialize_database()
        logger.info("Database initialized successfully.")

        # Yield control back to FastAPI
        yield

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize database. Please check the logs for more details.",
        )

    finally:
        logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan)


CORS(app)

# Include routers
app.include_router(cars_router, prefix="/api/v1/cars", tags=["cars"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
