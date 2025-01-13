from datetime import datetime
from typing import List

from app.models.users import User
from beanie import Document, Link
from pydantic import BaseModel


class Entry(BaseModel):
    title: str
    date: datetime
    location: str
    body: str
    images: List[str]


class Journal(Document):
    title: str
    author: Link[User]
    created_date: datetime
    updated_date: datetime
    entries: List[Entry]

    class Settings:
        name = "journals"
