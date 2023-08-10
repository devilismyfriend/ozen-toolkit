from fastapi import FastAPI

from stt.routers import router as stt_router
from register_connections import registers

app = FastAPI()
app = registers(app)

app.include_router(stt_router)
