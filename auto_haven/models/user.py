from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class User(Document):
    username: str
    password: str
    email: str
    created: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "user"


class Login(BaseModel):
    username: str
    password: str


class CurrentUser(BaseModel):
    id: PydanticObjectId
    username: str
    email: str


class Register(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str
    email: str
