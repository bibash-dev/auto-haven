from typing import Optional, Annotated, List
from pydantic import BaseModel, ConfigDict, Field, field_validator, BeforeValidator, HttpUrl

PyObjectId = Annotated[str, BeforeValidator(str)]


class Car(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    brand: str = Field(...)
    model: str = Field(...)
    year: int = Field(..., ge=1970, le=2025)
    cm3: int = Field(..., ge=500, le=10000)
    kw: int = Field(..., ge=50, le=1000)
    km: int = Field(..., ge=0, le=100000)
    price: int = Field(..., ge=0, le=100000)
    image_url: Optional[HttpUrl] = None

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
    price: Optional[int] = Field(..., ge=0, le=100 * 000)
    image_url: Optional[HttpUrl] = None


class CarCollection(BaseModel):
    cars: List[Car] = Field(...)
