from contextlib import asynccontextmanager
from typing import Union

from app.config import settings
from app.models.users import User
from app.routes import user_routes
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient


async def init_db():
    client = AsyncIOMotorClient(settings.database_url)
    await init_beanie(
        database=client[settings.database_name],
        document_models=[User],  # Add all your document models here
    )
    return client


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = await init_db()
    print(f"Connected to MongoDB. Database '{settings.database_name}' is ready.")
    yield
    client.close()
    print("Closed MongoDB connection")


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
)

app.include_router(user_routes.router, prefix="/api")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
