"""
Image compression utilities for Screeny MCP server.

Provides intelligent image compression that tries multiple strategies
to achieve target file sizes while maintaining quality.
"""

import io
from base64 import b64encode
from pathlib import Path
from typing import Tuple
from PIL import Image


def compress_image(image_path: str, target_size_bytes: int) -> Tuple[bytes, str]:
    """
    Compress image to JPEG format for smaller file sizes.

    Args:
        image_path: Path to the image file
        target_size_bytes: Target size in bytes for the compressed image

    Returns:
        Tuple of (compressed image data as bytes, format used)

    Strategy:
        Try JPEG compression with decreasing quality levels until target is met,
        or return the best compression achieved.
    """
    with Image.open(image_path) as img:
        strategies = [
            ("JPEG_HIGH", 1.0, "JPEG", 90),
            ("JPEG_MEDIUM", 1.0, "JPEG", 80),
            ("JPEG_LOW", 1.0, "JPEG", 70),
            ("JPEG_SMALL", 0.9, "JPEG", 85),
        ]

        best_data = None
        best_format = "JPEG"

        for _, scale_factor, format_type, quality in strategies:
            try:
                if scale_factor == 1.0:
                    resized_img = img
                else:
                    new_width = max(1, int(img.width * scale_factor))
                    new_height = max(1, int(img.height * scale_factor))
                    resized_img = img.resize(
                        (new_width, new_height), Image.Resampling.LANCZOS)

                buffer = io.BytesIO()

                # Convert RGBA to RGB for JPEG
                if resized_img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new(
                        'RGB', resized_img.size, (255, 255, 255))
                    if resized_img.mode == 'P':
                        resized_img = resized_img.convert('RGBA')
                    rgb_img.paste(resized_img, mask=resized_img.split(
                    )[-1] if resized_img.mode == 'RGBA' else None)
                    resized_img = rgb_img

                resized_img.save(buffer, format='JPEG',
                                 quality=quality, optimize=True)
                result_data = buffer.getvalue()

                # Use first result that fits, or keep the best one
                if len(result_data) <= target_size_bytes:
                    return result_data, format_type

                if best_data is None or len(result_data) < len(best_data):
                    best_data = result_data
                    best_format = format_type

            except Exception:
                continue

        # Return best attempt or original if all failed
        if best_data is not None:
            return best_data, best_format
        else:
            return Path(image_path).read_bytes(), "PNG"


def get_mime_type(format_name: str) -> str:
    """
    Get MIME type for image format.
    """
    return "image/png" if format_name == "PNG" else "image/jpeg"


def compress_to_base64_cap(image_path: str, base64_max_bytes: int) -> Tuple[str, str, int]:
    """Compress to JPEG targeting a base64 cap using heuristic steps.

    - Convert base64 cap to raw target (~3/4)
    - Try decreasing target thresholds; each run uses internal quality/scale strategies
    - Return first whose base64 fits; else return smallest attempt

    Returns: (base64_data, mime_type, base64_size_bytes)
    """

    target_raw_size = int(base64_max_bytes * 3 / 4)

    best_b64 = None
    best_bytes = None
    best_fmt = "JPEG"

    for factor in (1.0, 0.9, 0.8, 0.7, 0.6):
        candidate_bytes, candidate_format = compress_image(
            image_path, int(target_raw_size * factor)
        )
        candidate_b64 = b64encode(candidate_bytes).decode("utf-8")
        if len(candidate_b64.encode("utf-8")) <= base64_max_bytes:
            return candidate_b64, get_mime_type(candidate_format), len(candidate_b64)

        if best_bytes is None or len(candidate_bytes) < len(best_bytes):
            best_bytes = candidate_bytes
            best_b64 = candidate_b64
            best_fmt = candidate_format

    b64 = best_b64 or ""
    return b64, get_mime_type(best_fmt), len(b64)
