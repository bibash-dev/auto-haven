import cloudinary
from cloudinary import uploader
from bson import ObjectId
from pydantic import HttpUrl
from fastapi import (
    APIRouter,
    Body,
    Request,
    status,
    HTTPException,
    Depends,
    File,
    UploadFile,
    Form,
)
from fastapi.responses import Response
from pymongo import ReturnDocument
from auto_haven.config import BaseConfig
from auto_haven.models.car import Car, UpdateCar, PaginatedCarCollection
from auto_haven.routers.users import auth_handler

router = APIRouter()

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
    response_model_by_alias=False,
)
async def add_car_with_image(
    request: Request,
    brand: str = Form(
        ..., description="brand or manufacturer of the car (e.g., Toyota, Ford)."
    ),
    model: str = Form(
        ..., description="model name of the car (e.g., Corolla, Mustang)."
    ),
    year: int = Form(..., description="manufacturing year of the car (e.g., 2020)."),
    cm3: int = Form(
        ...,
        description="engine displacement of the car in cubic centimeters (e.g., 1500).",
    ),
    kw: int = Form(
        ..., description="power output of the car in kilowatts (e.g., 100)."
    ),
    km: int = Form(..., description="mileage of the car in kilometers (e.g., 5000)."),
    price: int = Form(
        ..., description="price of the car in the local currency (e.g., 20000)."
    ),
    image: UploadFile = File(
        ..., description="an image of the car in JPEG or PNG format (max 5 MB)."
    ),
    user: str = Depends(auth_handler.authentication_wrapper),
) -> Car:
    """
    Add a new car to the database.

    - **car**: Car data to be added (JSON body).
    - **returns**: The newly added car object.
    """
    # validate the image before proceeding to upload
    await validate_image(image, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)

    # Upload image to Cloudinary
    try:
        cloudinary_image = cloudinary.uploader.upload(
            image.file, folder="FARM2", crop="fill", width=800
        )
        image_url = cloudinary_image["url"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}",
        )

    car = Car(
        brand=brand,
        model=model,
        year=year,
        cm3=cm3,
        kw=kw,
        km=km,
        price=price,
        user_id=user["user_id"],
        image_url=image_url,
    )

    # Insert car into the database
    cars_collection = request.app.db["cars"]
    car_data = car.model_dump(by_alias=True, exclude=["id"])

    # Convert HttpUrl fields to strings
    if "image_url" in car_data and isinstance(car_data["image_url"], HttpUrl):
        car_data["image_url"] = str(car_data["image_url"])

    insert_result = await cars_collection.insert_one(car_data)
    new_car = await cars_collection.find_one({"_id": insert_result.inserted_id})

    return new_car


@router.get(
    "/",
    response_description="Retrieve a paginated list of all available cars",
    response_model=PaginatedCarCollection,
    response_model_by_alias=False,
)
async def list_cars(
    request: Request, page: int = 1, limit: int = 10
) -> PaginatedCarCollection:
    """
    Retrieve a paginated list of all cars from the database.

    - page: The page number to retrieve (default: 1).
    - limit: The number of cars per page (default: 10).
    - **returns**: A paginated collection of cars.
    """
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400, detail="Page and limit must be greater than 0."
        )

    cars_collection = request.app.db["cars"]
    results = []

    try:
        cursor = (
            cars_collection.find().sort("brand").limit(limit).skip((page - 1) * limit)
        )
        total_documents = await cars_collection.count_documents({})
        total_pages = (total_documents + limit - 1) // limit
        has_more = total_documents > page * limit

        async for document in cursor:
            results.append(Car(**document))  # Validate documents against the Car model

        return PaginatedCarCollection(
            cars=results,
            page=page,
            total_cars=total_documents,
            total_pages=total_pages,
            has_more=has_more,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get(
    "/{id}",
    response_description="Get a single car by ID",
    response_model=Car,
    response_model_by_alias=False,
)
async def car_detail(id: str, request: Request):
    """
    Retrieve a single car by its ID.

    - id: The ID of the car to retrieve.
    - **returns**: The car object if found, otherwise raises a 404 error.
    """
    cars_collection = request.app.db["cars"]
    # validate and convert the id to ObjectId
    try:
        car_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid car ID: {id}"
        )

    if (car := await cars_collection.find_one({"_id": car_id})) is not None:
        return car
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Car with ID {id} not found"
    )


@router.put(
    "/{id}",
    response_description="Update a car",
    response_model=Car,
    response_model_by_alias=False,
)
async def update_car(
    id: str,
    request: Request,
    car: UpdateCar = Body(...),
):
    """
    Update individual fields of an existing car record.

    - id: The ID to get the car from.
    - **car**: The car data to update (JSON body).
    - **returns**: The updated car object if found, otherwise raises a 404 error.
    """
    cars_collection = request.app.db["cars"]
    try:
        car_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Car {id} not found"
        )

    # Convert the Pydantic model to a dictionary and exclude None values
    car_data = {
        field_name: field_value
        for field_name, field_value in car.model_dump(by_alias=True).items()
        if field_value is not None and field_name != "_id"
    }

    # Convert HttpUrl fields to strings
    for field_name, field_value in car_data.items():
        if isinstance(field_value, HttpUrl):
            car_data[field_name] = str(field_value)

    # If there are fields to update, perform the update
    if len(car_data) >= 1:
        update_result = await cars_collection.find_one_and_update(
            {"_id": car_id},
            {"$set": car_data},
            return_document=ReturnDocument.AFTER,
        )

        if update_result is not None:
            return update_result
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Car {id} not found"
            )

    # If no fields are provided for update, return the existing car
    existing_car = await cars_collection.find_one({"_id": car_id})
    if existing_car is not None:
        return existing_car

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Car {id} not found"
    )


@router.delete("/{id}", response_description="Delete a car")
async def delete_car(id: str, request: Request):
    """
    Delete a car by its ID.

    - id: The ID of the car to delete.
    - returns: HTTP 204 No Content if successful, otherwise raises a 404 error.
    """
    try:
        car_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Car {id} not found"
        )

    cars_collection = request.app.db["cars"]
    delete_result = await cars_collection.delete_one({"_id": car_id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Car with {id} not found"
    )
