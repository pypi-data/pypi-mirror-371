import re
from typing import Iterable

def slugify(text: str) -> str:
    """Chuyển chuỗi thành slug: chữ thường, gạch nối, bỏ ký tự đặc biệt."""
    text = text.lower().strip()
    # thay thế ký tự không phải chữ/số bằng dấu cách
    text = re.sub(r"[^a-z0-9]+", " ", text)
    # gộp khoảng trắng thành dấu gạch
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")

def flatten(nested: Iterable[Iterable]) -> list:
    """Làm phẳng một iterable 2 chiều thành list 1 chiều."""
    out = []
    for it in nested:
        out.extend(it)
    return out