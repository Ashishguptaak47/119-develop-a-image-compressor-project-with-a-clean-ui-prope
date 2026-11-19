import os
import io
import time
from dataclasses import dataclass
from typing import Optional, Tuple
from PIL import Image, ImageOps

@dataclass
class CompressionResult:
    original_path: str
    output_path: str
    original_bytes: int
    compressed_bytes: int
    duration_ms: float
    saved_percent: float
    success: bool
    error_message: Optional[str] = None

class ImageCompressor:
    @staticmethod
    def get_supported_extensions() -> Tuple[str, ...]:
        return (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")

    @staticmethod
    def _prepare_image_mode(img: Image.Image, target_format: str) -> Image.Image:
        target_format = target_format.upper()
        if target_format in ("JPEG", "JPG"):
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                alpha = img.convert("RGBA").split()[-1]
                bg.paste(img, mask=alpha)
                return bg
            elif img.mode != "RGB":
                return img.convert("RGB")
        elif target_format == "PNG":
            if img.mode not in ("RGB", "RGBA", "P"):
                return img.convert("RGBA")
        elif target_format == "WEBP":
            if img.mode not in ("RGB", "RGBA"):
                return img.convert("RGBA" if "transparency" in img.info or img.mode in ("RGBA", "LA") else "RGB")
        return img

    @staticmethod
    def _resize_if_needed(img: Image.Image, max_dim: Optional[int]) -> Image.Image:
        if not max_dim or max_dim <= 0:
            return img
        width, height = img.size
        longest = max(width, height)
        if longest <= max_dim:
            return img
        scale = max_dim / float(longest)
        new_w = max(1, int(width * scale))
        new_h = max(1, int(height * scale))
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    def compress_single(
        self,
        input_path: str,
        output_path: str,
        quality: int = 80,
        max_dimension: Optional[int] = None,
        target_format: Optional[str] = None,
        target_kb: Optional[int] = None
    ) -> CompressionResult:
        start_time = time.perf_counter()
        orig_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0

        try:
            with Image.open(input_path) as raw_img:
                img = ImageOps.exif_transpose(raw_img)
                fmt = (target_format or raw_img.format or "JPEG").upper()
                if fmt == "JPG":
                    fmt = "JPEG"

                img = self._resize_if_needed(img, max_dimension)
                img = self._prepare_image_mode(img, fmt)

                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                if target_kb and target_kb > 0 and fmt in ("JPEG", "WEBP"):
                    final_bytes = self._binary_search_quality(img, fmt, target_kb * 1024)
                    with open(output_path, "wb") as f:
                        f.write(final_bytes)
                else:
                    save_kwargs = {"optimize": True}
                    if fmt in ("JPEG", "WEBP"):
                        save_kwargs["quality"] = max(1, min(100, quality))
                    elif fmt == "PNG":
                        save_kwargs["compress_level"] = 9
                        if quality < 85:
                            img = img.quantize(colors=max(16, int(256 * (quality / 100.0))))
                    img.save(output_path, format=fmt, **save_kwargs)

            comp_size = os.path.getsize(output_path)
            saved = max(0.0, ((orig_size - comp_size) / orig_size) * 100.0) if orig_size > 0 else 0.0
            duration = (time.perf_counter() - start_time) * 1000
            return CompressionResult(
                original_path=input_path,
                output_path=output_path,
                original_bytes=orig_size,
                compressed_bytes=comp_size,
                duration_ms=round(duration, 2),
                saved_percent=round(saved, 2),
                success=True
            )
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000
            return CompressionResult(
                original_path=input_path,
                output_path=output_path,
                original_bytes=orig_size,
                compressed_bytes=0,
                duration_ms=round(duration, 2),
                saved_percent=0.0,
                success=False,
                error_message=str(exc)
            )

    def _binary_search_quality(self, img: Image.Image, fmt: str, target_bytes: int) -> bytes:
        low, high = 15, 95
        best_data = None
        while low <= high:
            mid = (low + high) // 2
            buf = io.BytesIO()
            img.save(buf, format=fmt, quality=mid, optimize=True)
            data = buf.getvalue()
            if len(data) <= target_bytes:
                best_data = data
                low = mid + 1
            else:
                high = mid - 1
        if best_data is None:
            buf = io.BytesIO()
            img.save(buf, format=fmt, quality=10, optimize=True)
            best_data = buf.getvalue()
        return best_data
