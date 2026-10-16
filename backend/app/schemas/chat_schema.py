from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    sender_id: int
    content: str
    sent_at: datetime


class ChatHistoryResponse(BaseModel):
    items: list[MessageResponse]
    page: int
    page_size: int
    total: int
