from pyrogram.types import Message
from urllib.parse import urlencode
import mimetypes

def build_download_link(base_url: str, file_id: str, size: int, name: str, mime: str) -> str:
    params = {"f": file_id, "s": str(size), "n": name, "m": mime}
    return f"{base_url}?{urlencode(params)}"

async def generate_link(message: Message, base_url: str) -> str:
    media = message.document or message.video or message.audio or message.photo

    file_id = media.file_id
    size = getattr(media, "file_size", 0)

    # تعیین اسم فایل واقعی
    if hasattr(media, "file_name") and media.file_name:
        name = media.file_name
    elif hasattr(media, "file_unique_id"):
        ext = mimetypes.guess_extension(getattr(media, "mime_type", ""))
        name = f"{media.file_unique_id}{ext or '.bin'}"
    else:
        name = f"file_{message.id}.bin"

    mime = getattr(media, "mime_type", "application/octet-stream")
    return build_download_link(base_url, file_id, size, name, mime)
