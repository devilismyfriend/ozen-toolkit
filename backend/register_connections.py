from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from db_config import TORTOISE_ORM

def registry_tortois(app: FastAPI) -> FastAPI:
    register_tortoise(
        app,
        TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )
    return app

def registers(app: FastAPI) -> FastAPI:
    app = registry_tortois(app)
    return app