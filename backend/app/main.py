from fastapi import Depends, FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Document, PatientDocumentData, User
from app.routes.documents import router as document_router

from fastapi.middleware.cors import CORSMiddleware

from app.routes.admin import router as admin_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Patient Document Management API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",    
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router)
app.include_router(admin_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description=app.description,
    )

    schemas = openapi_schema.get("components", {}).get("schemas", {})

    for schema in schemas.values():
        properties = schema.get("properties", {})

        for property_schema in properties.values():
            items = property_schema.get("items")

            if not items:
                continue

            if items.get("contentMediaType") == "application/octet-stream":
                items["format"] = "binary"

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def root():
    return {"message": "Patient Document Management API is running"}


@app.get("/database-test")
def database_test(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "result": result.scalar(),
    }
