from typing import Optional, Annotated, List
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    BeforeValidator,
    HttpUrl,
)

PyObjectId = Annotated[str, BeforeValidator(str)]


class Car(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    brand: str = Field(..., description="brand of a car")
    model: str = Field(..., description="The model of a car")
    year: int = Field(..., ge=1970, le=2025, description="year of production")
    cm3: int = Field(..., ge=500, le=10000, description="engine displacement in cm³")
    kw: int = Field(..., ge=50, le=1000, description="engine power in kW")
    km: int = Field(..., ge=0, le=100000, description="kilometers travelled")
    price: int = Field(..., ge=0, le=100000, description="price of a car")
    image_url: Optional[HttpUrl] = Field(None, description="URL of the car's image")

    @field_validator("brand", "model")
    @classmethod
    def check_case(cls, value: str) -> str:
        return value.title()

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class UpdateCar(BaseModel):
    brand: Optional[str] = Field(...)
    model: Optional[str] = Field(...)
    year: Optional[int] = Field(..., ge=1970, le=2025)
    cm3: Optional[int] = Field(..., ge=500, le=10000)
    kw: Optional[int] = Field(..., ge=50, le=1000)
    km: Optional[int] = Field(..., ge=0, le=100 * 1000)
    price: Optional[int] = Field(..., ge=0, le=100 * 1000)
    image_url: Optional[HttpUrl] = None


class CarCollection(BaseModel):
    cars: List[Car] = Field(...)


class PaginatedCarCollection(CarCollection):
    page: int = Field(ge=1, default=1)
    total_cars: int
    total_pages: int
    has_more: bool
