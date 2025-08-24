import asyncio
import ssl
import contextlib
from typing import Optional, Tuple
from aiohttp import web, ClientConnectionError
from pyrogram.errors import OffsetInvalid
from .utils import content_disposition, parse_range
from .errors import InvalidParameterError, FileStreamError, ServerError


def create_ssl_context(cert_path: Optional[str], key_path: Optional[str]) -> Optional[ssl.SSLContext]:
    """
    Create an SSL context if both certificate and key are provided.
    Return None if neither is provided, or raise error if only one is missing.
    """
    if not cert_path and not key_path:
        return None
    if not cert_path or not key_path:
        raise ServerError("Both ssl_cert and ssl_key must be provided for HTTPS")
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)
    return ctx


def create_app(pyro_client, route: str = "/dl") -> web.Application:
    """
    Create aiohttp application with a GET endpoint to stream Telegram files.
    Handles HTTP Range requests safely by always starting from offset 0 and skipping bytes locally.
    """
    app = web.Application()

    async def download_handler(request: web.Request) -> web.StreamResponse:
        """
        Handle HTTP GET requests to stream Telegram files.
        Implements safe resume simulation to prevent OFFSET_INVALID errors.
        """
        file_id = request.query.get("file_id")
        size_str = request.query.get("size")
        name = request.query.get("name", "file")
        mime = request.query.get("mime", "application/octet-stream")

        # Validate required query parameters
        try:
            if not file_id or not size_str:
                raise InvalidParameterError("Missing required query params: file_id and size")
            total_size = int(size_str)
            if total_size <= 0:
                raise InvalidParameterError("Invalid 'size' parameter")
        except ValueError:
            raise InvalidParameterError("Invalid 'size' parameter (not an integer)")

        # Parse Range header if present
        byte_range = parse_range(request.headers.get("Range"), total_size)
        if byte_range:
            start_byte, end_byte = byte_range
            status_code = 206
            content_length = end_byte - start_byte + 1
        else:
            start_byte, end_byte = 0, total_size - 1
            status_code = 200
            content_length = total_size

        # Return 416 if requested range is beyond file size
        if start_byte >= total_size:
            return web.Response(
                status=416,
                headers={"Content-Range": f"bytes */{total_size}", "Accept-Ranges": "bytes"}
            )

        # Prepare HTTP response headers
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Type": mime,
            "Content-Disposition": content_disposition(name),
            "Content-Length": str(content_length),
        }
        if status_code == 206:
            headers["Content-Range"] = f"bytes {start_byte}-{end_byte}/{total_size}"

        resp = web.StreamResponse(status=status_code, headers=headers)
        await resp.prepare(request)

        # Stream Telegram media starting from offset 0 and skip bytes until start_byte
        bytes_remaining = content_length
        bytes_skipped = 0

        try:
            async for chunk in pyro_client.stream_media(file_id, offset=0):
                if not chunk:
                    break

                # Skip bytes until the requested start position
                if bytes_skipped + len(chunk) <= start_byte:
                    bytes_skipped += len(chunk)
                    continue

                if bytes_skipped < start_byte:
                    chunk = chunk[start_byte - bytes_skipped :]
                    bytes_skipped = start_byte

                # Trim chunk if it exceeds the remaining content length
                if len(chunk) > bytes_remaining:
                    chunk = chunk[:bytes_remaining]

                await resp.write(chunk)
                bytes_remaining -= len(chunk)

                if bytes_remaining <= 0:
                    break

            return resp

        except (ClientConnectionError, ConnectionResetError, asyncio.CancelledError, RuntimeError):
            # Client disconnected safely
            return resp
        except Exception as e:
            # Any other streaming error
            with contextlib.suppress(Exception):
                if resp.prepared:
                    await resp.write_eof()
            raise FileStreamError(f"Streaming error: {e}") from e

    app.router.add_get(route, download_handler)
    return app


async def run_server(
    pyro_client,
    host: str = "0.0.0.0",
    port: int = 8080,
    route: str = "/dl",
    ssl_cert: Optional[str] = None,
    ssl_key: Optional[str] = None
):
    """
    Run the aiohttp server with the provided Pyrogram client.
    Supports optional HTTPS if SSL cert and key are provided.
    """
    try:
        app = create_app(pyro_client, route=route)
        runner = web.AppRunner(app)
        await runner.setup()

        ssl_ctx = create_ssl_context(ssl_cert, ssl_key)
        site = web.TCPSite(runner, host=host, port=port, ssl_context=ssl_ctx)
        await site.start()
        return runner, site
    except Exception as e:
        raise ServerError(f"Failed to start HTTP server: {e}") from e
