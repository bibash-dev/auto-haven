import logging
import math

import cloudinary
from beanie import PydanticObjectId, WriteRules
from cloudinary import uploader
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    status,
    UploadFile,
    BackgroundTasks,
)

from auto_haven.config import BaseConfig
from auto_haven.models.user import User
from auto_haven.models.car import Car, UpdateCar, PaginatedCarCollection
from auto_haven.routers.users import auth_handler
from auto_haven.background_tasks import create_car_description_and_send_email

router = APIRouter()

logger = logging.getLogger(__name__)

CARS_PER_PAGE = 10

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024

settings = BaseConfig()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_SECRET_KEY,
)


async def validate_image(image, image_types, image_size):
    if image.content_type not in image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}.",
        )

    if image.size > image_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image file size must not exceed {MAX_IMAGE_SIZE / 1024 / 1024} MB.",
        )


@router.post(
    "/",
    response_description="Add a new car to the database",
    response_model=Car,
    status_code=status.HTTP_201_CREATED,
)
async def add_car(
    background_tasks: BackgroundTasks,
    brand: str = Form(..., description="Brand or manufacturer of the car."),
    model: str = Form(..., description="Model name of the car."),
    year: int = Form(..., description="Manufacturing year of the car."),
    cm3: int = Form(
        ...,
        description="Engine displacement of the car in cubic centimeters (e.g., 1500).",
    ),
    kw: int = Form(
        ..., description="Power output of the car in kilowatts (e.g., 100)."
    ),
    km: int = Form(..., description="Mileage of the car in kilometers (e.g., 5000)."),
    price: int = Form(
        ..., description="Price of the car in the local currency (e.g., 20000)."
    ),
    image: UploadFile = File(
        ..., description="An image of the car in JPEG or PNG format (max 5 MB)."
    ),
    user_data: str = Depends(auth_handler.authentication_wrapper),
) -> Car:
    # Validate the image
    try:
        await validate_image(image, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    except ValueError as e:
        logger.error(f"Image validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Upload image to Cloudinary
    try:
        logger.info(f"Uploading image for car: {brand} {model}")
        cloudinary_image = cloudinary.uploader.upload(
            image.file, folder="FARM2", crop="fill", width=800
        )
        image_url = cloudinary_image["url"]
        logger.info(f"Image uploaded successfully: {image_url}")
    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}",
        )

    # Fetch the authenticated user
    user = await User.get(user_data["user_id"])
    if not user:
        logger.error(f"User not found: {user_data['user_id']}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # Create and save the new car
    car = Car(
        brand=brand,
        model=model,
        year=year,
        cm3=cm3,
        kw=kw,
        km=km,
        price=price,
        image_url=image_url,
        user_id=user.id,
    )
    background_tasks.add_task(
        create_car_description_and_send_email,
        brand=brand,
        model=model,
        year=year,
        image_url=image_url,
    )
    await car.insert(link_rule=WriteRules.WRITE)

    logger.info(f"Car created successfully: {car.id}")
    return car


@router.get(
    "/",
    response_description="List of all available cars",
    response_model=PaginatedCarCollection,
)
async def list_cars(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of cars per page"),
) -> PaginatedCarCollection:

    try:
        # Fetch paginated cars
        cars = await Car.find_all().skip((page - 1) * limit).limit(limit).to_list()

        # Calculate total number of cars and pages
        total_cars = await Car.find_all().count()
        total_pages = math.ceil(total_cars / limit)
        has_more = page < total_pages

        return PaginatedCarCollection(
            cars=cars,
            page=page,
            total_cars=total_cars,
            total_pages=total_pages,
            has_more=has_more,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching cars: {str(e)}",
        )


@router.get(
    "/{car_id}",
    response_description="Get a single car by ID",
    response_model=Car,
)
async def get_car(car_id: PydanticObjectId) -> Car:
    car = await Car.get(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {car_id} not found",
        )
    return car


@router.put(
    "/{car_id}",
    response_description="Update a car",
    response_model=Car,
)
async def update_car(
    car_id: PydanticObjectId,
    car_update: UpdateCar,
) -> Car:
    # Fetch the car
    car = await Car.get(car_id)
    if not car:
        logger.error(f"Car not found: {car_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {car_id} not found",
        )

    # Prepare the update data
    update_data = {
        field_name: field_value
        for field_name, field_value in car_update.model_dump(exclude_unset=True).items()
        if field_value is not None
    }

    # Update the car
    try:
        logger.info(f"Updating car: {car_id} with data: {update_data}")
        await car.set(update_data)
        logger.info(f"Car updated successfully: {car_id}")
    except Exception as e:
        logger.error(f"Failed to update car: {car_id}. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update car: {str(e)}",
        )

    return car


@router.delete(
    "/{car_id}",
    response_description="Delete a car by its ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_car(car_id: PydanticObjectId) -> None:
    # Fetch the car
    car = await Car.get(car_id)
    if not car:
        logger.error(f"Car not found: {car_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {car_id} not found",
        )

    # Delete the car
    try:
        logger.info(f"Deleting car: {car_id}")
        await car.delete()
        logger.info(f"Car deleted successfully: {car_id}")
    except Exception as e:
        logger.error(f"Failed to delete car: {car_id}. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete car: {str(e)}",
        )

    # Return a 204 No Content response
    return None
