from urllib.parse import urlencode
from pyrogram.types import Message
from .errors import LinkGenerationError, InvalidMediaError


def build_download_link(base_url: str, file_id: str, size: int, name: str, mime: str) -> str:
    """
    Construct a full download URL using base URL and media metadata.

    Parameters:
        base_url (str): The server base URL (including schema, host, port, route).
        file_id (str): Telegram file ID for the media.
        size (int): Size of the file in bytes.
        name (str): Filename for the download.
        mime (str): MIME type of the file.

    Returns:
        str: A fully encoded URL pointing to the downloadable media.

    Raises:
        LinkGenerationError: If URL encoding or parameter building fails.
    """
    try:
        params = {
            "file_id": file_id,
            "size": str(size),
            "name": name,
            "mime": mime
        }
        return f"{base_url}?{urlencode(params)}"
    except Exception as e:
        raise LinkGenerationError(f"Failed to build download link: {e}")


async def generate_link(message: Message, base_url: str) -> str:
    """
    Extract media information from a Pyrogram Message object and generate a direct-download link.

    Parameters:
        message (Message): Pyrogram Message object containing media.
        base_url (str): Base URL of the download server.

    Returns:
        str: Direct download link for the media.

    Raises:
        InvalidMediaError: If the message does not contain any downloadable media.
        LinkGenerationError: If media metadata is missing or invalid.
    """
    # Select the first available media type
    media = message.document or message.video or message.audio or message.photo
    if not media:
        raise InvalidMediaError("Message does not contain any downloadable media")

    # Extract required metadata from the media object
    file_id = media.file_id
    size = getattr(media, "file_size", 0)
    name = getattr(media, "file_name", f"file_{message.id}")
    mime = getattr(media, "mime_type", "application/octet-stream")

    # Validate extracted metadata
    if not file_id or size <= 0:
        raise LinkGenerationError("Invalid media metadata (missing file_id or size)")

    # Build and return the final download link
    return build_download_link(base_url, file_id, size, name, mime)
