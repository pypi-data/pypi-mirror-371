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
    """Compress to JPEG and return base64 data and size within a byte cap using binary search.

    Strategy:
    - Open source image once
    - For each scale in descending detail (1.0, 0.9, 0.8, 0.7):
      - Resize (if needed)
      - Binary search JPEG quality to find highest quality whose base64 size <= cap
    - Return first scale that fits; otherwise return the smallest attempt overall

    Returns: (base64_data, mime_type, base64_size_bytes)
    """

    def ensure_rgb(image: Image.Image) -> Image.Image:
        if image.mode in ("RGBA", "LA", "P"):
            base = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            base.paste(image, mask=image.split()
                       [-1] if image.mode == "RGBA" else None)
            return base
        if image.mode != "RGB":
            return image.convert("RGB")
        return image

    def encode_jpeg_bytes(image: Image.Image, quality: int) -> bytes:
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()

    best_overall_bytes = None
    best_overall_b64 = None

    with Image.open(image_path) as src:
        src = ensure_rgb(src)

        # Prefer minimal resizes: larger scale first to preserve detail
        for scale in (1.0, 0.9, 0.8, 0.7):
            if scale != 1.0:
                new_w = max(1, int(src.width * scale))
                new_h = max(1, int(src.height * scale))
                img = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
            else:
                img = src

            # Binary search quality between hi and lo
            lo, hi = 50, 95  # practical JPEG range
            best_fit_bytes = None
            best_fit_b64 = None
            while lo <= hi:
                mid = (lo + hi) // 2
                try:
                    data = encode_jpeg_bytes(img, mid)
                except Exception:
                    # If encoding fails at this quality, try lower
                    hi = mid - 1
                    continue

                b64 = b64encode(data).decode("utf-8")
                b64_len = len(b64.encode("utf-8"))
                if b64_len <= base64_max_bytes:
                    # Fits: record and try higher quality
                    best_fit_bytes = data
                    best_fit_b64 = b64
                    lo = mid + 1
                else:
                    # Too big: reduce quality
                    hi = mid - 1

            # If we found a fit at this scale, return it
            if best_fit_b64 is not None:
                return best_fit_b64, "image/jpeg", len(best_fit_b64)

            # Track smallest attempt for fallback
            # Use the smallest between current best_fit_bytes (may be None) and a lower-quality trial
            try:
                trial_bytes = encode_jpeg_bytes(img, 60)
                trial_b64 = b64encode(trial_bytes).decode("utf-8")
            except Exception:
                trial_bytes = None
                trial_b64 = None

            candidate_bytes = best_fit_bytes or trial_bytes
            candidate_b64 = best_fit_b64 or trial_b64
            if candidate_bytes is not None:
                if best_overall_bytes is None or len(candidate_bytes) < len(best_overall_bytes):
                    best_overall_bytes = candidate_bytes
                    best_overall_b64 = candidate_b64

    # Fallback: no fit; return smallest we achieved
    b64 = best_overall_b64 or ""
    return b64, "image/jpeg", len(b64)
