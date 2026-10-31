from app.models.chat import Message


def message_payload(message: Message) -> dict:
    """Wire shape every socket in a room receives for one message."""
    return {
        "id": message.id,
        "match_id": message.match_id,
        "sender_id": message.sender_id,
        "content": message.content,
        "sent_at": message.sent_at.isoformat(),
        "attachment": message.attachment,
    }
