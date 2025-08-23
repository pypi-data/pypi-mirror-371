from urllib.parse import quote

def content_disposition(filename: str) -> str:
    return f"attachment; filename*=UTF-8''{quote(filename)}"

def parse_range(range_header: str, total_size: int):
    if not range_header or not range_header.startswith("bytes="):
        return None
    try:
        rng = range_header.split("=", 1)[1]
        start_str, end_str = rng.split("-", 1)
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else total_size - 1
        if start < 0 or end < start or end >= total_size:
            return None
        return (start, end)
    except Exception:
        return None
