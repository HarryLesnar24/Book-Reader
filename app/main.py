from typing import Any, Generator, Literal
import logging
import botocore.exceptions
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
import boto3
import botocore
import mimetypes
from typing import cast
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.type_defs import CORSConfigurationTypeDef, CreateBucketConfigurationTypeDef

mimetypes.add_type("application/javascript", ".mjs")
mimetypes.add_type("application/javascript", ".js")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
asynClient = AsyncQdrantClient(host=Config.QDRANT_HOST, port=Config.QDRANT_PORT)
corsConfig = cast(CORSConfigurationTypeDef, {
    'CORSRules': [
        {
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'HEAD'],
            'AllowedOrigins': ['http://localhost:8000', '*'], # Update with your frontend ports
            'ExposeHeaders': [
                'Accept-Ranges', 
                'Content-Range', 
                'Content-Encoding', 
                'Content-Length',
                'Content-Disposition'
            ]
        }
    ]
})

@asynccontextmanager
async def lifespan(app: FastAPI):
    s3 = cast(S3Client, boto3.client(
        service_name="s3",
        endpoint_url=Config.S3_ENDPOINT,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_ACCESS_SECRET_KEY,
        region_name=Config.REGION,
    ))
    try:
        s3.head_bucket(Bucket=Config.S3_BUCKET)
    except botocore.exceptions.ClientError as e:
        code = e.response.get('Error', {}).get('Code')
        if code == '404':
            s3.create_bucket(
                Bucket=Config.S3_BUCKET,
                CreateBucketConfiguration=cast(CreateBucketConfigurationTypeDef, {
                    "LocationConstraint": Config.REGION
                }
            ))
            logging.info(msg=f"Created {Config.S3_BUCKET} Bucket")
    s3.put_bucket_cors(Bucket=Config.S3_BUCKET, CORSConfiguration=corsConfig)
    app.state.s3Client = s3
    if not await asynClient.collection_exists(Config.COLLECTION_NAME):
        await createCollection(
            asynClient,
            payload_m=18,
            m=0,
            vecSize=768,
            dist=models.Distance.DOT,
            name=Config.COLLECTION_NAME,
        )
        logging.info(msg=f"Created {Config.COLLECTION_NAME} Collection")
    yield
    s3.close()
    await asynClient.close()

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
    lifespan=lifespan,
)

app.include_router(authRouter, prefix=f"/api/{version}/auth", tags=["authentication"])
app.include_router(bookRouter, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(readRouter, prefix=f"/api/{version}/reader", tags=["reader"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/web", StaticFiles(directory="app/web"), name="web")
