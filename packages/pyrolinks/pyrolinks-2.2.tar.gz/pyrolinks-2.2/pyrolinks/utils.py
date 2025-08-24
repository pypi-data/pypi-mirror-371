from typing import Optional, Tuple
from urllib.parse import quote
from .errors import InvalidParameterError, UtilsError


def content_disposition(filename: str) -> str:
    """
    Generate a RFC 5987 / RFC 6266 compatible Content-Disposition header
    for Unicode filenames. Ensures proper encoding for browser downloads.

    Parameters:
        filename (str): Name of the file to be used in Content-Disposition.

    Returns:
        str: Formatted Content-Disposition header.

    Raises:
        InvalidParameterError: If filename is empty or None.
    """
    if not filename:
        raise InvalidParameterError("Empty filename for Content-Disposition")
    return f"attachment; filename*=UTF-8''{quote(filename)}"


def parse_range(range_header: Optional[str], total_size: int) -> Optional[Tuple[int, int]]:
    """
    Parse an HTTP Range header to determine the requested byte range.
    Returns a tuple (start, end) inclusive, or None if no valid range is provided.

    Supports only a single range per request.

    Examples of supported headers:
        Range: bytes=0-499      -> returns (0, 499)
        Range: bytes=500-       -> returns (500, total_size-1)
        Range: bytes=-500       -> returns (total_size-500, total_size-1)

    Parameters:
        range_header (Optional[str]): The value of the 'Range' HTTP header.
        total_size (int): Total size of the file in bytes.

    Returns:
        Optional[Tuple[int, int]]: (start, end) byte positions or None if invalid.

    Raises:
        UtilsError: If any unexpected error occurs while parsing.
    """
    if not range_header:
        return None
    if not range_header.startswith("bytes="):
        return None

    try:
        rng = range_header.split("=", 1)[1].strip()

        # Only a single range is supported; multiple ranges not handled
        if "," in rng:
            return None

        start_str, end_str = rng.split("-", 1)

        if start_str and end_str:
            # Both start and end specified
            start = int(start_str)
            end = int(end_str)
            if start > end:
                return None
        elif start_str and not end_str:
            # Range from start to end of file
            start = int(start_str)
            end = total_size - 1
        elif not start_str and end_str:
            # Suffix range: last N bytes
            length = int(end_str)
            if length <= 0:
                return None
            start = max(total_size - length, 0)
            end = total_size - 1
        else:
            # Invalid format
            return None

        # Validate final range
        if start < 0 or end < start or start >= total_size:
            return None

        # Ensure end does not exceed total file size
        end = min(end, total_size - 1)

        return (start, end)

    except Exception as e:
        raise UtilsError(f"Failed to parse range: {e}") from e
