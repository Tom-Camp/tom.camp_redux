from beanie import Document
from pydantic import BaseModel, EmailStr


class User(Document):
    username: str
    email: str
    hashed_password: str

    class Settings:
        name = "users"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
