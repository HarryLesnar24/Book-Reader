from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.auth import authRouter
from app.routes.book import bookRouter
from app.routes.reader import readRouter
from app.config import Config

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
)

app.include_router(authRouter, prefix=f"/api/{version}/auth", tags=["authentication"])
app.include_router(bookRouter, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(readRouter, prefix=f"/api/{version}/reader", tags=["reader"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/web", StaticFiles(directory="app/web"), name="web")