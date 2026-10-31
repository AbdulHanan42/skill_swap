"""Shared primitives for multipart uploads.

Both chat attachments and interview submissions stream the body so the size cap
holds even when the client lies about its content length.
"""

import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, Request, UploadFile, status

CHUNK = 64 * 1024
SAFE_SUFFIX = re.compile(r"[^a-z0-9]")


def display_name(raw: str | None) -> str:
    name = (raw or "").replace("\\", "/").split("/")[-1].strip() or "file"
    return name[:200]


def stored_name(raw: str | None) -> str:
    suffix = SAFE_SUFFIX.sub("", Path(display_name(raw)).suffix.lower())[:12]
    return f"{uuid4().hex}.{suffix}" if suffix else uuid4().hex


async def read_capped(file: UploadFile, request: Request, limit: int, too_big: str) -> bytes:
    declared = request.headers.get("content-length", "")
    if declared.isdigit() and int(declared) > limit + CHUNK:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, too_big)

    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(CHUNK):
        total += len(chunk)
        if total > limit:
            # The browser may lie about the size, so the cap is checked while reading.
            raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, too_big)
        chunks.append(chunk)
    if total == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That file is empty.")
    return b"".join(chunks)


def save_upload(root: Path, folder: str, original: str | None, data: bytes) -> str:
    """Write the payload under root/folder and return its root-relative path."""
    target = root / folder
    target.mkdir(parents=True, exist_ok=True)
    stored = stored_name(original)
    (target / stored).write_bytes(data)
    return f"{folder}/{stored}"


def resolve_stored(root: Path, relative: str | None) -> Path | None:
    """Return the file only when it really lives inside the upload root."""
    if not relative:
        return None
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return None
    return path
