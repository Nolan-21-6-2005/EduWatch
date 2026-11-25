"""Vẽ bounding box kèm nhãn TIẾNG VIỆT lên khung hình.

``cv2.putText`` chỉ có font Hershey (ASCII) nên chữ có dấu bị thành "???". Ở đây chữ được
dựng bằng Pillow với font TrueType có tiếng Việt, rồi chỉ ghép đúng vùng nhỏ của nhãn lên
khung hình (không chuyển cả ảnh qua Pillow) để không làm chậm vòng dự đoán.

Font được tìm theo thứ tự: biến môi trường EDUWATCH_FONT -> thư mục view/asset/fonts (đặt file
.ttf vào đây nếu muốn dùng font riêng) -> font hệ thống (Windows: Segoe UI/Arial/Tahoma; Linux:
DejaVu/Liberation; macOS: Arial) -> font đi kèm matplotlib (có sẵn cùng ultralytics).
Font nào thiếu chữ tiếng Việt sẽ bị bỏ qua. Không có font phù hợp (hoặc đặt EDUWATCH_BBOX_ASCII=1)
thì nhãn tự chuyển sang tiếng Việt KHÔNG DẤU ("Ngu gat", "Quay bai/Trao doi"...).
"""
from __future__ import annotations

import os
import unicodedata
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from utils.labels_vi import canonical_label

BASE_DIR = Path(__file__).resolve().parents[2]
FONT_DIR = BASE_DIR / "view" / "asset" / "fonts"

# Màu (BGR) theo nhãn; chữ trắng nên chọn màu đủ đậm.
_PALETTE = [
    (40, 40, 220),    # đỏ
    (0, 120, 235),    # cam
    (200, 80, 30),    # xanh dương
    (150, 50, 160),   # tím
    (60, 140, 40),    # xanh lá
    (30, 150, 190),   # vàng đậm
    (140, 90, 20),    # xanh biển
    (60, 60, 60),     # xám đậm
]
_COLOR_ORDER = ["sleeping", "eating", "leaving_seat", "phone",
                "turning_head", "standing", "reading", "walking"]


def label_color(label: str | None) -> tuple[int, int, int]:
    key = canonical_label(label)
    index = _COLOR_ORDER.index(key) if key in _COLOR_ORDER else len(_COLOR_ORDER) - 1
    return _PALETTE[index % len(_PALETTE)]


def _candidate_fonts():
    env = os.getenv("EDUWATCH_FONT")
    if env:
        yield Path(env)
    if FONT_DIR.is_dir():
        for pattern in ("*.ttf", "*.otf"):
            yield from sorted(FONT_DIR.glob(pattern))
    windir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in ("segoeui.ttf", "arial.ttf", "tahoma.ttf", "calibri.ttf", "verdana.ttf"):
        yield windir / name
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        yield Path(path)
    try:  # matplotlib là phụ thuộc của ultralytics và đi kèm DejaVuSans.ttf (có tiếng Việt)
        import matplotlib

        yield Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf"
    except Exception:
        pass


_VI_TEST_CHARS = "ăâêôơưđắằẵặấầẫậếềễệốồỗộớờỡợứừữựỳỷỹỵ"


def _supports_vietnamese(font) -> bool:
    """Font thiếu glyph sẽ vẽ ký tự thay thế (ô vuông). Kiểm tra bằng cách so ảnh của từng
    chữ có dấu với ảnh của một ký tự chắc chắn không tồn tại trong font."""
    def render(ch: str) -> bytes:
        image = Image.new("L", (64, 64), 0)
        ImageDraw.Draw(image).text((8, 8), ch, font=font, fill=255)
        return image.tobytes()

    try:
        missing = render("\U0010ffff")
        return all(render(ch) != missing for ch in _VI_TEST_CHARS)
    except Exception:
        return False


@lru_cache(maxsize=1)
def _font_path() -> str | None:
    """Font đầu tiên có đủ chữ tiếng Việt; không có thì trả None (nhãn sẽ hiện KHÔNG DẤU)."""
    if os.getenv("EDUWATCH_BBOX_ASCII", "").lower() in ("1", "true", "yes"):
        return None  # ép dùng tiếng Việt không dấu trên bounding box
    for path in _candidate_fonts():
        try:
            if path.is_file() and _supports_vietnamese(ImageFont.truetype(str(path), 24)):
                return str(path)
        except OSError:
            continue
    return None


@lru_cache(maxsize=16)
def _font(size: int):
    path = _font_path()
    return ImageFont.truetype(path, size) if path else None


def _strip_accents(text: str) -> str:
    """Phương án cuối khi máy không có font nào: bỏ dấu để vẫn đọc được thay vì hiện '???'."""
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def draw_label(frame, text: str, x: int, y: int, color=(40, 40, 220), font_size: int | None = None):
    """Vẽ nhãn (nền màu, chữ trắng) ngay trên mép trên bbox tại (x, y); không đủ chỗ thì
    đặt vào bên trong bbox. Sửa trực tiếp ``frame`` (BGR uint8)."""
    if not text:
        return frame
    height, width = frame.shape[:2]
    size = font_size or max(13, min(height, width) // 26)
    font = _font(size)

    if font is None:  # không có font TrueType
        text = _strip_accents(text)
        scale = size / 28
        (tw, th), base = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
        x0 = max(0, min(x, width - tw - 6))
        y0 = y - th - base - 6 if y - th - base - 6 >= 0 else y
        cv2.rectangle(frame, (x0, y0), (x0 + tw + 6, y0 + th + base + 6), color, -1)
        cv2.putText(frame, text, (x0 + 3, y0 + th + 3), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, (255, 255, 255), 1, cv2.LINE_AA)
        return frame

    left, top, right, bottom = font.getbbox(text)
    tw, th = max(1, right - left), max(1, bottom - top)
    pad_x, pad_y = max(3, size // 4), max(2, size // 6)
    box_w, box_h = tw + 2 * pad_x, th + 2 * pad_y

    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).text((-left, -top), text, font=font, fill=255)
    alpha = np.asarray(mask, dtype=np.float32) / 255.0

    x0 = max(0, min(int(x), width - box_w))
    y0 = int(y) - box_h
    if y0 < 0:  # sát mép trên: đặt nhãn xuống dưới mép trên của bbox
        y0 = min(int(y), max(0, height - box_h))
    roi = frame[y0:y0 + box_h, x0:x0 + box_w]
    if roi.size == 0:
        return frame
    roi[:] = color
    region = roi[pad_y:pad_y + th, pad_x:pad_x + tw]
    if region.size:
        a = alpha[: region.shape[0], : region.shape[1], None]
        region[:] = (region * (1.0 - a) + 255.0 * a).astype(np.uint8)
    return frame


def draw_detection(frame, box, text: str, color=(40, 40, 220), thickness: int | None = None):
    """Vẽ một bbox (x1, y1, x2, y2) và nhãn tiếng Việt phía trên nó."""
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    thickness = thickness or max(2, min(frame.shape[:2]) // 240)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    return draw_label(frame, text, x1, y1, color)
