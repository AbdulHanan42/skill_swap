from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class AttachmentSummary(BaseModel):
    filename: str
    size: int
    mime_type: str | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    sender_id: int
    content: str
    sent_at: datetime
    read_at: datetime | None = None
    attachment: AttachmentSummary | None = None


class ChatHistoryResponse(BaseModel):
    items: list[MessageResponse]
    page: int
    page_size: int
    total: int


class ChatContact(BaseModel):
    """One row in the chat sidebar — a room exists per accepted match."""

    id: int
    peer_id: int
    name: str
    avatar: str | None
    designation: str | None
    last_message: str | None
    last_message_at: datetime | None
    last_message_mine: bool
    unread_count: int
    online: bool


class ChatUnreadResponse(BaseModel):
    total: int


class ChatReadResponse(BaseModel):
    marked: int
    marked_at: datetime
