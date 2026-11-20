"""mo_phong/bai_06.py – MÔ HÌNH Bài 6 "Đo tốc độ của vật chuyển động" (chạy cục bộ / xưởng Python).

Thế giới mô phỏng: viên bi thép lăn từ nghỉ trên máng nghiêng, gia tốc thật a (ẩn, khác nhau theo học sinh).
  - Thí nghiệm 1 "toc_do_trung_binh": hai cổng quang E, F; đồng hồ MC964 MODE A->B đo t_EF.
  - Thí nghiệm 2 "toc_do_tuc_thoi": một cổng quang; đồng hồ đo thời gian bi chắn cổng (t = d / v).
Có chủ đích: sai số đặt cổng, nhiễu đồng hồ, lượng tử hoá theo thang đo, quên RESET, sai MODE,
đồng hồ bấm tay (sai số phản xạ), thước kém chính xác.
Giả định mô hình (cần đối chiếu bộ thật của trường): chiều dài máng, miền gia tốc, đường kính bi -> bai_06.json.
"""
from __future__ import annotations

import math

from .chung import (chuan_cau_hinh, dinh_dang, doc_so, doc_theo_mode, luong_tu_hoa,
                    tao_rng)

THI_NGHIEM = ("toc_do_trung_binh", "toc_do_tuc_thoi")


class MoPhong:
    def __init__(self, bai: dict, ma_hs: str):
        self.bai, self.ma_hs = bai, ma_hs
        tp = bai["tham_so_that"]
        r = tao_rng(bai["ma_bai"], ma_hs, "tham_so_that")
        self.a = r.uniform(*tp["gia_toc_m_s2"])
        self.d = r.uniform(*tp["duong_kinh_bi_m"])
        self.L = tp["chieu_dai_mang_m"]
        self.sigma_dat = tp["sai_so_dat_cong_m"]
        self.dc = bai["dung_cu"]

    # ---------- kiểm tra hợp lệ ----------
    def kiem_tra(self, thi_nghiem: str, ch: dict) -> tuple[list[str], list[str]]:
        chan, cb = [], []
        if thi_nghiem not in THI_NGHIEM:
            return [f"Thí nghiệm '{thi_nghiem}' không có trong bài này."], cb
        dh = ch.get("dong_ho", "mc964")
        if dh not in self.dc or self.dc[dh]["loai"] != "do_thoi_gian":
            return [f"'{dh}' không phải dụng cụ đo thời gian trong bộ thí nghiệm."], cb
        if ch.get("thang_do") not in (None, *self.dc[dh]["thang_do"]):
            chan.append("Đồng hồ này không có thang đo em chọn.")
        if thi_nghiem == "toc_do_tuc_thoi" and dh == "dong_ho_bam_tay":
            chan.append("Bi chắn cổng quang chỉ trong một khoảng thời gian rất ngắn; "
                        "đồng hồ bấm tay không thể bắt được khoảng thời gian đó.")
        if thi_nghiem == "toc_do_trung_binh":
            xe, xf = ch.get("vi_tri_e_m"), ch.get("vi_tri_f_m")
            if xe is None or xf is None:
                chan.append("Chưa đặt vị trí cổng quang E và F.")
            else:
                if xe < 0.02:
                    chan.append("Cổng E quá sát nam châm: bi chưa kịp lăn đã qua cổng.")
                if xf <= xe:
                    chan.append("Cổng F phải nằm sau cổng E theo chiều chuyển động của bi.")
                if xf > self.L:
                    chan.append(f"Máng chỉ dài {self.L:.2f} m tính từ vị trí thả; cổng F vượt quá máng.")
                if not chan and xf - xe < 0.15:
                    cb.append("Khoảng EF ngắn: sai số tương đối của s và t sẽ lớn.")
        else:
            x = ch.get("vi_tri_cong_m")
            if x is None:
                chan.append("Chưa đặt vị trí cổng quang.")
            elif x < 0.05 or x > self.L:
                chan.append(f"Vị trí cổng phải nằm trong máng (0,05 m đến {self.L:.2f} m tính từ vị trí thả).")
        return chan, cb

    # ---------- vật lí ----------
    def _chan_cong(self, x: float, a: float) -> float:
        """Thời gian bi (đường kính d) chắn cổng đặt ở x: chính xác theo chuyển động nhanh dần đều."""
        h = self.d / 2
        return (math.sqrt(2 * a * (x + h)) - math.sqrt(2 * a * (x - h))) / a

    def _vi_tri_that(self, ch: dict, thi_nghiem: str) -> tuple:
        if thi_nghiem == "toc_do_trung_binh":
            r = tao_rng(self.bai["ma_bai"], self.ma_hs, "dat_cong", round(ch["vi_tri_e_m"], 4), round(ch["vi_tri_f_m"], 4))
            return (ch["vi_tri_e_m"] + r.gauss(0, self.sigma_dat), ch["vi_tri_f_m"] + r.gauss(0, self.sigma_dat))
        r = tao_rng(self.bai["ma_bai"], self.ma_hs, "dat_cong", round(ch["vi_tri_cong_m"], 4))
        return (ch["vi_tri_cong_m"] + r.gauss(0, self.sigma_dat),)

    def _khoa_vat_ly(self, ch: dict, thi_nghiem: str):
        keys = ("vi_tri_e_m", "vi_tri_f_m") if thi_nghiem == "toc_do_trung_binh" else ("vi_tri_cong_m",)
        return tuple(round(ch[k], 4) for k in keys)

    def _co_so(self, thi_nghiem: str, ch: dict, lan: int) -> tuple[float, float, float]:
        """(t_ab, t_a, t_b) thật của lần chạy thứ `lan` (gia tốc dao động nhẹ giữa các lần)."""
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, thi_nghiem, self._khoa_vat_ly(ch, thi_nghiem), lan)
        a_i = self.a * (1 + rng.gauss(0, 0.006))
        pos = self._vi_tri_that(ch, thi_nghiem)
        if thi_nghiem == "toc_do_trung_binh":
            xe, xf = pos
            t_ab = math.sqrt(2 * xf / a_i) - math.sqrt(2 * xe / a_i)
            return t_ab, self._chan_cong(xe, a_i), self._chan_cong(xf, a_i)
        t = self._chan_cong(pos[0], a_i)
        return 0.0, (t if ch.get("o_cam_cong", "A") == "A" else 0.0), (t if ch.get("o_cam_cong", "A") == "B" else 0.0)

    # ---------- phép đo ----------
    def do_thoi_gian(self, thi_nghiem: str, ch: dict, lan: int) -> dict:
        chan, cb = self.kiem_tra(thi_nghiem, ch)
        if chan:
            return {"hop_le": False, "hien_thi": None, "gia_tri": None, "don_vi": "s", "chan": chan, "canh_bao": cb}
        dh = self.dc[ch.get("dong_ho", "mc964")]
        tdo = dh["thang_do"][ch.get("thang_do") or next(iter(dh["thang_do"]))]
        res, sigma = tdo["do_chia_s"], dh["sigma_s"]
        t_ab, t_a, t_b = self._co_so(thi_nghiem, ch, lan)
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "dong_ho", thi_nghiem, self._khoa_vat_ly(ch, thi_nghiem), lan)
        if dh["loai_do"] == "tay":           # đồng hồ bấm tay: chỉ có giá trị t_ab (đo "từ E đến F")
            gia = doc_so(t_ab, res, sigma, rng)
            return self._goi(max(gia, 0.0), res, tdo["toi_da_s"], cb)
        mode = ch.get("mode", "A->B")
        loi = False
        base = doc_theo_mode(mode, t_ab, t_a, t_b)
        if base is None:
            return {"hop_le": True, "hien_thi": "----", "gia_tri": None, "don_vi": "s", "chan": [], "loi_thao_tac": True,
                    "canh_bao": cb + ["Đồng hồ không hiển thị số có nghĩa ở chế độ MODE này."]}
        gia = doc_so(base, res, sigma, rng)
        if thi_nghiem == "toc_do_trung_binh" and mode != "A->B":
            loi = True
            cb = cb + ["Giá trị hiển thị nhỏ bất thường so với quãng đường EF em đã đặt. "
                       "Hãy kiểm tra lại chế độ MODE có phù hợp với đại lượng cần đo."]
        if thi_nghiem == "toc_do_tuc_thoi" and mode not in ("A", "B"):
            loi = True
            cb = cb + ["Chế độ MODE hiện tại có thể không đo đúng khoảng thời gian bi chắn cổng quang."]
        if thi_nghiem == "toc_do_tuc_thoi" and mode in ("A", "B") and mode != ch.get("o_cam_cong", "A"):
            return {"hop_le": True, "hien_thi": dinh_dang(0.0, res), "gia_tri": 0.0, "don_vi": "s", "chan": [], "loi_thao_tac": True,
                    "canh_bao": cb + ["Đồng hồ không nhận được tín hiệu. Hãy kiểm tra ổ cắm của cổng quang và MODE."]}
        if lan > 1 and not ch.get("da_reset", True):
            t_ab2, t_a2, t_b2 = self._co_so(thi_nghiem, ch, lan - 1)
            truoc = doc_theo_mode(mode, t_ab2, t_a2, t_b2) or 0.0
            gia = luong_tu_hoa(gia + truoc, res)
            loi = True
            cb = cb + ["Số chỉ lần này lớn hơn rõ rệt lần trước dù điều kiện không đổi. "
                       "Hãy xem lại các thao tác trước mỗi lần đo."]
        return self._goi(gia, res, tdo["toi_da_s"], cb, loi=loi)

    def _goi(self, gia: float, res: float, toi_da: float, cb: list[str], loi: bool = False) -> dict:
        if gia > toi_da:
            return {"hop_le": True, "hien_thi": "OvEr", "gia_tri": None, "don_vi": "s", "chan": [],
                    "canh_bao": cb + ["Giá trị vượt thang đo đã chọn."]}
        if gia > 0 and res / 2 / gia > 0.03:
            cb = cb + [f"Độ chia của thang đo lớn so với giá trị cần đo (sai số dụng cụ cỡ {res / 2 / gia * 100:.0f}%)."]
        return {"hop_le": True, "hien_thi": dinh_dang(gia, res), "gia_tri": gia, "don_vi": "s",
                "chan": [], "canh_bao": cb, "loi_thao_tac": loi}

    def do_chieu_dai(self, muc: str, ch: dict, lan: int, dung_cu: str) -> dict:
        if dung_cu not in self.dc or self.dc[dung_cu]["loai"] != "do_chieu_dai":
            return {"hop_le": False, "gia_tri": None, "chan": [f"'{dung_cu}' không phải dụng cụ đo độ dài."], "canh_bao": []}
        d_c = self.dc[dung_cu]
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "do_dai", muc, dung_cu, self._khoa_vat_ly(ch, "toc_do_trung_binh") if muc == "quang_duong" else "d", lan)
        if muc == "duong_kinh":
            that, cb = self.d, []
        elif muc == "quang_duong" and "vi_tri_e_m" in ch and "vi_tri_f_m" in ch:
            xe, xf = self._vi_tri_that(ch, "toc_do_trung_binh")
            that, cb = xf - xe, []
        else:
            return {"hop_le": False, "gia_tri": None, "chan": ["Chưa có đối tượng hợp lệ để đo."], "canh_bao": []}
        if that > d_c["toi_da_m"]:
            return {"hop_le": False, "gia_tri": None, "chan": [f"Vượt giới hạn đo của {dung_cu}."], "canh_bao": []}
        gia = doc_so(that, d_c["do_chia_m"], d_c["sigma_m"], rng)
        if d_c["do_chia_m"] / 2 / gia > 0.02:
            cb.append(f"Độ chia của dụng cụ lớn so với đại lượng đo (sai số dụng cụ cỡ {d_c['do_chia_m'] / 2 / gia * 100:.1f}%).")
        return {"hop_le": True, "hien_thi": dinh_dang(gia, d_c["do_chia_m"]), "gia_tri": gia,
                "don_vi": "m", "chan": [], "canh_bao": cb}

    # ---------- đối chiếu ẩn (chỉ dùng cho test/chấm, KHÔNG gửi cho học sinh) ----------
    def gia_tri_ly_thuyet(self, thi_nghiem: str, ch: dict) -> float:
        if thi_nghiem == "toc_do_trung_binh":
            xe, xf = self._vi_tri_that(ch, thi_nghiem)
            return (xf - xe) / (math.sqrt(2 * xf / self.a) - math.sqrt(2 * xe / self.a))
        return math.sqrt(2 * self.a * self._vi_tri_that(ch, thi_nghiem)[0])
