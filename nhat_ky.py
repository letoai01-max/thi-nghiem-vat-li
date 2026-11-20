"""nhat_ky.py – GHI NHẬT KÝ PHIÊN THỰC HÀNH, đã che thông tin định danh (chạy cục bộ / xưởng Python).

Quy tắc (file Word, II.3): không đưa tên, email, số điện thoại, tên trường/lớp vào log hay prompt.
Học sinh chỉ định danh bằng mã ẩn danh (ví dụ HS07). Lỗi ghi nhật ký chỉ cảnh báo, không làm hỏng việc chính.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=7))
MA_HS_HOP_LE = re.compile(r"^[A-Za-z0-9_-]{2,16}$")

_MAU_CHE = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"(?<!\d)(?:\+?84|0)\d{8,10}(?!\d)"), "[sdt]"),
    (re.compile(r"(?i)\b(?:lớp|lop)\s*\d{1,2}\s*[A-Za-z]?\d*\b"), "[lớp]"),
    (re.compile(r"(?i)\b(?:trường|truong)\s+(?:THPT|THCS|chuyên|chuyen)?\s*[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,4}"), "[trường]"),
    (re.compile(r"(?i)\b(?:tôi tên là|em tên là|mình tên là|tên em là)\s+[\wÀ-ỹ]+(?:\s+[\wÀ-ỹ]+){0,3}"), "[tên]"),
]


def che_thong_tin(van_ban: str) -> str:
    for mau, thay in _MAU_CHE:
        van_ban = mau.sub(thay, van_ban)
    return van_ban


def khong_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


class NhatKy:
    def __init__(self, thu_muc: str | Path = "nhat_ky", bat: bool = True):
        self.thu_muc, self.bat = Path(thu_muc), bat
        self.dong: list[dict] = []

    def ghi(self, ma_hs: str, bai: str, su_kien: str, **chi_tiet) -> None:
        muc = {"luc": datetime.now(TZ).isoformat(timespec="seconds"), "ma_hs": ma_hs, "bai": bai, "su_kien": su_kien,
               "chi_tiet": {k: che_thong_tin(v) if isinstance(v, str) else v for k, v in chi_tiet.items()}}
        self.dong.append(muc)
        if not self.bat:
            return
        try:
            self.thu_muc.mkdir(parents=True, exist_ok=True)
            with open(self.thu_muc / f"{bai}_{ma_hs}.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(muc, ensure_ascii=False) + "\n")
        except OSError as e:
            print(f"[CẢNH BÁO] Không ghi được nhật ký: {e}", flush=True)
