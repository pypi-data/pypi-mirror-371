from aiohttp import web
from .utils import content_disposition, parse_range

def create_app(pyro_client, route="/dl"):
    app = web.Application()

    async def download_handler(request):
        f = request.query.get("f")
        s = int(request.query.get("s", 0))
        n = request.query.get("n", "file")
        m = request.query.get("m", "application/octet-stream")

        if not f or s <= 0:
            raise web.HTTPBadRequest(text="Invalid parameters")

        byte_range = parse_range(request.headers.get("Range"), s)
        status = 206 if byte_range else 200
        start_byte, end_byte = byte_range if byte_range else (0, s - 1)
        content_length = end_byte - start_byte + 1

        async def stream(resp):
            total_sent = 0
            async for chunk in pyro_client.stream_media(f):
                if byte_range:
                    chunk_start = total_sent
                    chunk_end = total_sent + len(chunk) - 1
                    if chunk_end < start_byte:
                        total_sent += len(chunk)
                        continue
                    if chunk_start > end_byte:
                        break
                    if chunk_start < start_byte:
                        chunk = chunk[start_byte - chunk_start:]
                    if chunk_end > end_byte:
                        chunk = chunk[:end_byte - chunk_start + 1]
                await resp.write(chunk)
                total_sent += len(chunk)
                if total_sent >= content_length:
                    break
            await resp.write_eof()

        headers = {
            "Accept-Ranges": "bytes",
            "Content-Type": m,
            "Content-Disposition": content_disposition(n),
            "Content-Length": str(content_length)
        }
        if status == 206:
            headers["Content-Range"] = f"bytes {start_byte}-{end_byte}/{s}"

        resp = web.StreamResponse(status=status, headers=headers)
        await resp.prepare(request)
        await stream(resp)
        return resp

    app.router.add_get(route, download_handler)
    return app

async def run_server(pyro_client, host="0.0.0.0", port=8080, route="/dl"):
    app = create_app(pyro_client, route=route)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"Server running at http://{host}:{port}{route}")
    return runner, site
