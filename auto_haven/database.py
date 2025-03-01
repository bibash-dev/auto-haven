import logging
import motor.motor_asyncio
from beanie import init_beanie
from .config import BaseConfig
from auto_haven.models.car import Car
from auto_haven.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = BaseConfig()


async def initialize_database():
    try:
        if not settings.MONGODB_URL:
            raise ValueError(
                "Database URL is not configured. Please check your settings."
            )

        logger.info("Initializing database connection...")

        # Create a MongoDB client
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)

        # Initialize Beanie with the specified database and document models
        await init_beanie(database=client.info_cars_db, document_models=[User, Car])

        logger.info("Database initialized successfully.")

    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
        raise
    except motor.motor_asyncio.AsyncIOMotorError as me:
        logger.error(f"Database connection error: {me}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        raise
