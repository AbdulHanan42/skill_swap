from fastapi import APIRouter

from app.api.v1 import ai, auth, chat, interview, matches, profile, progress

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(matches.router)
api_router.include_router(chat.router)
api_router.include_router(ai.router)
api_router.include_router(interview.router)
api_router.include_router(progress.router)
