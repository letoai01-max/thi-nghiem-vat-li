"""mo_phong/sai_so.py – TÍNH SAI SỐ theo SGK Vật lí 10 KNTT, Bài 3, công thức (3.1)–(3.3) (chạy cục bộ).

Dùng để (1) chấm kết quả học sinh nộp, (2) kiểm thử "tính ngược" engine.
Làm tròn half-up; ΔA ghi đến chữ số thập phân của độ chia nhỏ nhất (ĐCNN); sai số dụng cụ = ĐCNN/2.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from .chung import so_chu_so_thap_phan


def trung_binh(ds: list[float]) -> float:
    return sum(ds) / len(ds)


def sai_so_ngau_nhien_tb(ds: list[float]) -> float:
    """(3.1)+(3.2): trung bình các |Ā - A_i|."""
    tb = trung_binh(ds)
    return sum(abs(tb - x) for x in ds) / len(ds)


def sai_so_tuyet_doi(ds: list[float], dcnn: float) -> float:
    """ΔA = ΔA' + ΔA_dụng cụ, với ΔA_dc = ĐCNN/2."""
    return sai_so_ngau_nhien_tb(ds) + dcnn / 2


def sai_so_ti_doi(d_a: float, a_tb: float) -> float:
    """(3.3): δA = ΔA / Ā · 100 (%)."""
    return d_a / a_tb * 100


def sai_so_ti_doi_tich_thuong(*ti_doi: float) -> float:
    """Tích/thương: tổng các sai số tỉ đối (SGK Bài 3, mục II.3)."""
    return sum(ti_doi)


def lam_tron(x: float, so_thap_phan: int) -> float:
    q = Decimal(1).scaleb(-so_thap_phan)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def ket_qua_ghi(ds: list[float], dcnn: float) -> dict:
    """A = Ā ± ΔA, cả hai viết đến chữ số thập phân của ĐCNN."""
    nd = so_chu_so_thap_phan(dcnn)
    a_tb = trung_binh(ds)
    d_a = sai_so_tuyet_doi(ds, dcnn)
    return {
        "a_tb": lam_tron(a_tb, nd),
        "d_a": lam_tron(d_a, nd),
        "chuoi": f"{lam_tron(a_tb, nd):.{nd}f} ± {lam_tron(d_a, nd):.{nd}f}",
        "sai_so_ti_doi_phan_tram": sai_so_ti_doi(d_a, a_tb),
    }
