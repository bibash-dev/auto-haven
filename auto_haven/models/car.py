from datetime import datetime
from typing import Optional, List
from beanie import Document, Link
from pydantic import BaseModel, Field, HttpUrl


# noinspection PyDataclass
class Car(Document, extra="allow"):
    brand: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The brand of the car (e.g., BMW, Toyota).",
    )
    model: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The model of the car (e.g., X5, Corolla).",
    )
    year: int = Field(
        ...,
        ge=1900,
        le=datetime.now().year,
        description="The manufacturing year of the car.",
    )
    cm3: int = Field(
        ..., gt=0, description="The engine displacement in cubic centimeters (cm³)."
    )
    kw: int = Field(
        ..., ge=50, le=1000, description="The engine power in kilowatts (kW)."
    )
    price: float = Field(
        ..., gt=0, description="The price of the car in the local currency."
    )
    description: Optional[str] = Field(
        None, max_length=500, description="A brief description of the car."
    )
    image_url: Optional[HttpUrl] = Field(None, description="A URL to the car's image.")
    pros: List[str] = Field(
        default_factory=list, description="A list of pros or advantages of the car."
    )
    cons: List[str] = Field(
        default_factory=list, description="A list of cons or disadvantages of the car."
    )
    date: datetime = Field(
        default_factory=datetime.now,
        description="The date when the car was added to the database.",
    )
    user: Optional[Link["User"]] = Field(
        None, description="The user who added the car."
    )

    class Settings:
        name = "car"

    class Config:
        json_schema_extra = {
            "example": {
                "brand": "BMW",
                "model": "X5",
                "year": 2021,
                "cm3": 3000,
                "kw": 250,
                "price": 100000,
                "description": "A luxury SUV with advanced features.",
                "image_url": "https://example.com/bmw-x5.jpg",
                "pros": ["Comfortable", "High performance"],
                "cons": ["Expensive", "High maintenance"],
                "date": "2023-10-01T12:00:00",
                "user": None,
            }
        }


class UpdateCar(BaseModel):
    price: Optional[float] = Field(
        None, gt=0, description="The updated price of the car."
    )
    description: Optional[str] = Field(
        None, max_length=500, description="The updated description of the car."
    )
    pros: Optional[List[str]] = Field(
        None, description="The updated list of pros for the car."
    )
    cons: Optional[List[str]] = Field(
        None, description="The updated list of cons for the car."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "price": 95000,
                "description": "A slightly used luxury SUV.",
                "pros": ["Comfortable", "High performance", "Good value"],
                "cons": ["High maintenance"],
            }
        }


class CarCollection(BaseModel):
    cars: List[Car] = Field(..., description="A list of car objects.")

    class Config:
        json_schema_extra = {
            "example": {
                "cars": [
                    {
                        "brand": "BMW",
                        "model": "X5",
                        "year": 2021,
                        "cm3": 3000,
                        "kw": 250,
                        "price": 100000,
                        "description": "A luxury SUV with advanced features.",
                        "image_url": "https://example.com/bmw-x5.jpg",
                        "pros": ["Comfortable", "High performance"],
                        "cons": ["Expensive", "High maintenance"],
                        "date": "2023-10-01T12:00:00",
                        "user": None,
                    },
                    {
                        "brand": "Toyota",
                        "model": "Corolla",
                        "year": 2020,
                        "cm3": 1800,
                        "kw": 132,
                        "price": 25000,
                        "description": "A reliable and fuel-efficient sedan.",
                        "image_url": "https://example.com/toyota-corolla.jpg",
                        "pros": ["Reliable", "Fuel-efficient"],
                        "cons": ["Basic features"],
                        "date": "2023-10-02T12:00:00",
                        "user": None,
                    },
                ]
            }
        }


class PaginatedCarCollection(CarCollection):
    page: int = Field(
        ge=1, default=1, description="The current page number in the paginated results."
    )
    total_cars: int = Field(
        ..., ge=0, description="The total number of cars across all pages."
    )
    total_pages: int = Field(
        ..., ge=1, description="The total number of pages available."
    )
    has_more: bool = Field(
        ..., description="Indicates whether there are more pages available."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "cars": [
                    {
                        "brand": "BMW",
                        "model": "X5",
                        "year": 2021,
                        "cm3": 3000,
                        "kw": 250,
                        "price": 100000,
                        "description": "A luxury SUV with advanced features.",
                        "image_url": "https://example.com/bmw-x5.jpg",
                        "pros": ["Comfortable", "High performance"],
                        "cons": ["Expensive", "High maintenance"],
                        "date": "2023-10-01T12:00:00",
                        "user": None,
                    }
                ],
                "page": 1,
                "total_cars": 50,
                "total_pages": 5,
                "has_more": True,
            }
        }
