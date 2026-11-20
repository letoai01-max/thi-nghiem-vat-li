"""mo_phong/chung.py – HÀM DÙNG CHUNG của engine mô phỏng (chạy cục bộ / xưởng Python).

Việc: sinh số ngẫu nhiên TẤT ĐỊNH theo (bài, mã học sinh, cấu hình, lần đo) để
số liệu nhất quán nội tại: cùng thao tác -> cùng số, học sinh không "xin lại cho đẹp".
Không cần biến môi trường. Không gọi mạng.
"""
from __future__ import annotations

import json
import random
from decimal import Decimal, ROUND_HALF_UP


def tao_rng(*khoa) -> random.Random:
    """Bộ sinh ngẫu nhiên tất định từ chuỗi khoá (random.Random(str) ổn định giữa các lần chạy)."""
    return random.Random("|".join(str(k) for k in khoa))


def chuan_cau_hinh(cau_hinh: dict) -> str:
    return json.dumps(cau_hinh, sort_keys=True, ensure_ascii=False)


def luong_tu_hoa(gia_tri: float, do_chia: float) -> float:
    """Làm tròn về bội nguyên của độ chia nhỏ nhất (half-up, đúng quy tắc SGK Bài 3)."""
    n = (Decimal(str(gia_tri)) / Decimal(str(do_chia))).to_integral_value(ROUND_HALF_UP)
    return float(n * Decimal(str(do_chia)))


def so_chu_so_thap_phan(do_chia: float) -> int:
    return max(0, -Decimal(str(do_chia)).as_tuple().exponent)


def dinh_dang(gia_tri: float, do_chia: float) -> str:
    """Chuỗi hiển thị đúng số chữ số thập phân của dụng cụ (dấu chấm; giao diện tự đổi sang phẩy)."""
    return f"{gia_tri:.{so_chu_so_thap_phan(do_chia)}f}"


def doc_so(gia_tri_that: float, do_chia: float, sigma: float, rng: random.Random) -> float:
    """Số đọc được = giá trị thật + nhiễu ngẫu nhiên, rồi lượng tử hoá theo độ chia."""
    return luong_tu_hoa(gia_tri_that + rng.gauss(0.0, sigma), do_chia)


def doc_theo_mode(mode: str, t_ab: float, t_a: float, t_b: float):
    """Đồng hồ MC964 hiển thị gì theo MODE (SGK Bài 6, mục II.1). None = không có số có nghĩa."""
    return {"A": t_a, "B": t_b, "A+B": t_a + t_b, "A->B": t_ab}.get(mode)
