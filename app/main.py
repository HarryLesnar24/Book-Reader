from typing import Any, Generator
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.auth import authRouter
from app.routes.book import bookRouter
from app.routes.reader import readRouter
from contextlib import asynccontextmanager
from app.config import Config
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client import models
from typing import AsyncGenerator
from core_db.vector.db import createCollection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
asynClient = AsyncQdrantClient(host=Config.QDRANT_HOST, port=Config.QDRANT_PORT)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await asynClient.collection_exists(Config.COLLECTION_NAME):
        await createCollection(asynClient, payload_m=18, m=0, vecSize=768, dist=models.Distance.DOT, name=Config.COLLECTION_NAME)
        logging.info(msg=f"Created {Config.COLLECTION_NAME} Collection")
    yield


version = Config.API_VERSION


app = FastAPI(
    title="Collaborative Book Reading Application API",
    description="A Rest API for Application",
    version=version,
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    openapi_url=f"/api/{version}/openapi.json",
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Hariprasath B",
        "url": "https://github.com/harrylesnar24",
        "email": "bhariprasath24@gmail.com",
    },
    terms_of_service="https://example.com/tos",
    debug=True,
    lifespan=lifespan
)

app.include_router(authRouter, prefix=f"/api/{version}/auth", tags=["authentication"])
app.include_router(bookRouter, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(readRouter, prefix=f"/api/{version}/reader", tags=["reader"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/web", StaticFiles(directory="app/web"), name="web")
