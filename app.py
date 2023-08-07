from fastapi import FastAPI

from stt_v1.routers import router as stt_v1_router

app = FastAPI()
app.include_router(stt_v1_router)
