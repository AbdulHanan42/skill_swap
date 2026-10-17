from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.websockets.chat_ws import router as chat_ws_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_ws_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "success", "message": "Skill Swap Backend is running!"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
