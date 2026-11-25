"""Ánh xạ nhãn tiếng Anh của model AI -> tên vi phạm tiếng Việt.

Quy ước:
- CSDN và logic nội bộ (lọc theo phòng, SESSION_LABELS, truy vấn SQL) luôn dùng nhãn tiếng Anh
  chuẩn (sleeping, phone...). Không đổi dữ liệu đã lưu.
- Chỉ khi HIỂN THỊ (nhật ký, thống kê, biểu đồ, bounding box) mới gọi ``vi_label()``.

Muốn đổi tên hiển thị hay thêm nhãn mới: sửa ``VIOLATION_NAMES_VI`` bên dưới.
"""
from __future__ import annotations

# Nhãn chuẩn -> tên hiển thị (theo bảng 8 sự kiện bắt lỗi tự động).
VIOLATION_NAMES_VI: dict[str, str] = {
    "sleeping": "Ngủ gật",
    "eating": "Ăn uống",
    "leaving_seat": "Rời vị trí",
    "phone": "Sử dụng điện thoại",
    "turning_head": "Quay bài/Trao đổi",
    "standing": "Đứng dậy",
    "reading": "Đọc tài liệu",
    "walking": "Di chuyển",
}

# Nhãn không còn dùng để nhận diện nhưng có thể còn trong log cũ của CSDL.
_LEGACY_NAMES_VI: dict[str, str] = {
    "leaning_down": "Cúi đầu",
}

# Tên tiếng Anh khác của cùng một lỗi (trong log cũ hoặc tên lớp của model) -> nhãn chuẩn.
_ALIASES: dict[str, str] = {
    "leave_seat": "leaving_seat",
    "moving": "walking",
    "use_phone": "phone",
    "using_phone": "phone",
}


def _normalize(label: str) -> str:
    return str(label).strip().lower().replace("-", "_").replace(" ", "_")


def canonical_label(label: str | None) -> str | None:
    """Đưa tên tiếng Anh bất kỳ về nhãn chuẩn (``leave_seat`` -> ``leaving_seat``)."""
    if label is None:
        return None
    key = _normalize(label)
    return _ALIASES.get(key, key)


def vi_label(label: str | None) -> str | None:
    """Tên tiếng Việt của một nhãn. Không biết nhãn thì trả lại nguyên văn (không báo lỗi),
    nên dữ liệu cũ đã là tiếng Việt hoặc giá trị rỗng như "—" vẫn hiển thị bình thường."""
    if not label:
        return label
    key = canonical_label(label)
    return VIOLATION_NAMES_VI.get(key) or _LEGACY_NAMES_VI.get(key) or label
