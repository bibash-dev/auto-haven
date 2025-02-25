from typing import Optional, Annotated
from pydantic import (
    BaseModel,
    Field,
    BeforeValidator,
)

PyObjectId = Annotated[str, BeforeValidator(str)]


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=15)
    password: str = Field(...)


class Login(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class CurrentUser(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=15)
