"""mo_phong/bai_11.py – MÔ HÌNH Bài 11 "Đo gia tốc rơi tự do" (chạy cục bộ / xưởng Python).

Thế giới mô phỏng: trụ thép (hoặc viên bi) rơi tự do từ nam châm điện qua cổng quang đặt cách s.
  t_that = sqrt(2 s_that / g) + delta        (delta = độ trễ nhả của nam châm, ẩn, hệ thống)
  s_doc  = s_that + lech_thuoc               (lệch điểm 0 khi đo bằng thước, ẩn, hệ thống)
Hệ quả có chủ đích: đồ thị s–t² không đi qua gốc hoàn hảo; g đo được lệch nhẹ; học sinh phải biện luận.
Viên bi thép: nhiễu lớn hơn nhiều và có lần không chắn cổng (SGK câu hỏi 2, mục IV).
Giả định mô hình (đối chiếu bộ thật của trường): g_that, độ trễ nam châm, lệch thước -> bai_11.json.
"""
from __future__ import annotations

import math

from .chung import dinh_dang, doc_so, doc_theo_mode, luong_tu_hoa, tao_rng

THI_NGHIEM = ("roi_tu_do",)


class MoPhong:
    def __init__(self, bai: dict, ma_hs: str):
        self.bai, self.ma_hs = bai, ma_hs
        tp = bai["tham_so_that"]
        r = tao_rng(bai["ma_bai"], ma_hs, "tham_so_that")
        self.g = tp["g_that_m_s2"]
        self.delta = r.uniform(*tp["do_tre_nam_cham_s"])
        self.lech = r.uniform(*tp["lech_thuoc_m"])
        self.L = tp["chieu_dai_mang_m"]
        self.l_vat = tp["chieu_dai_tru_m"]
        self.sigma_dat = tp["sai_so_dat_cong_m"]
        self.dc = bai["dung_cu"]

    def kiem_tra(self, thi_nghiem: str, ch: dict) -> tuple[list[str], list[str]]:
        chan, cb = [], []
        if thi_nghiem not in THI_NGHIEM:
            return [f"Thí nghiệm '{thi_nghiem}' không có trong bài này."], cb
        dh = ch.get("dong_ho", "mc964")
        if dh not in self.dc or self.dc[dh]["loai"] != "do_thoi_gian":
            return [f"'{dh}' không phải dụng cụ đo thời gian trong bộ thí nghiệm."], cb
        if ch.get("thang_do") not in (None, *self.dc[dh]["thang_do"]):
            chan.append("Đồng hồ này không có thang đo em chọn.")
        if dh == "dong_ho_bam_tay":
            chan.append("Trụ thép rơi cỡ vài phần mười giây; đồng hồ bấm tay không thể đồng bộ với lúc nam châm nhả.")
        if ch.get("vat", "tru_thep") not in ("tru_thep", "vien_bi"):
            chan.append("Vật rơi chọn không có trong bộ thí nghiệm.")
        s = ch.get("s_dat_m")
        if s is None:
            chan.append("Chưa đặt vị trí cổng quang (khoảng cách s từ nam châm).")
        elif s < 0.05 or s > self.L:
            chan.append(f"Cổng quang phải nằm trong máng: 0,05 m đến {self.L:.2f} m tính từ nam châm.")
        elif s < 0.15:
            cb.append("Quãng rơi ngắn: thời gian rơi rất nhỏ nên sai số tương đối lớn.")
        return chan, cb

    def _s_that(self, s_dat: float) -> float:
        r = tao_rng(self.bai["ma_bai"], self.ma_hs, "dat_cong", round(s_dat, 4))
        return s_dat + r.gauss(0, self.sigma_dat)

    def do_thoi_gian(self, thi_nghiem: str, ch: dict, lan: int) -> dict:
        chan, cb = self.kiem_tra(thi_nghiem, ch)
        if chan:
            return {"hop_le": False, "hien_thi": None, "gia_tri": None, "don_vi": "s", "chan": chan, "canh_bao": cb}
        dh = self.dc[ch.get("dong_ho", "mc964")]
        tdo = dh["thang_do"][ch.get("thang_do") or next(iter(dh["thang_do"]))]
        res = tdo["do_chia_s"]
        vat = ch.get("vat", "tru_thep")
        he_so = self.bai["tham_so_that"]["he_so_nhieu_vien_bi"] if vat == "vien_bi" else 1.0
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "roi", vat, round(ch["s_dat_m"], 4), lan)
        if vat == "vien_bi" and rng.random() < self.bai["tham_so_that"]["xac_suat_truot_cong_vien_bi"]:
            return {"hop_le": True, "hien_thi": "----", "gia_tri": None, "don_vi": "s", "chan": [],
                    "canh_bao": cb + ["Vật không chắn cổng quang đúng cách nên đồng hồ không dừng. Hãy quan sát lại cách vật rơi."]}
        s = self._s_that(ch["s_dat_m"])
        g_i = self.g * (1 + rng.gauss(0, 0.0015 * he_so))
        t_ab = math.sqrt(2 * s / g_i) + self.delta + rng.gauss(0, dh["sigma_s"] * he_so)
        v_cuoi = g_i * (t_ab - self.delta)
        t_b = self.l_vat / max(v_cuoi, 1e-6)          # thời gian vật chắn cổng quang
        mode = ch.get("mode", "A->B")
        loi = False
        base = doc_theo_mode(mode, t_ab, 0.0, t_b)    # nam châm không chắn cổng: t_a = 0
        if base is None:
            return {"hop_le": True, "hien_thi": "----", "gia_tri": None, "don_vi": "s", "chan": [], "loi_thao_tac": True,
                    "canh_bao": cb + ["Đồng hồ không hiển thị số có nghĩa ở chế độ MODE này."]}
        gia = luong_tu_hoa(base, res)
        if mode != "A->B":
            loi = True
            cb = cb + ["Giá trị hiển thị không giống một thời gian rơi từ lúc nam châm nhả. "
                       "Hãy kiểm tra lại chế độ MODE và cách nối dây."]
        if lan > 1 and not ch.get("da_reset", True):
            rng2 = tao_rng(self.bai["ma_bai"], self.ma_hs, "roi", vat, round(ch["s_dat_m"], 4), lan - 1)
            g2 = self.g * (1 + rng2.gauss(0, 0.0015 * he_so))
            tp = math.sqrt(2 * self._s_that(ch["s_dat_m"]) / g2) + self.delta
            gia = luong_tu_hoa(gia + (tp if mode == "A->B" else 0.0), res)
            loi = True
            cb = cb + ["Số chỉ lần này lớn hơn rõ rệt lần trước dù điều kiện không đổi. Hãy xem lại các thao tác trước mỗi lần đo."]
        if gia > tdo["toi_da_s"]:
            return {"hop_le": True, "hien_thi": "OvEr", "gia_tri": None, "don_vi": "s", "chan": [],
                    "canh_bao": cb + ["Giá trị vượt thang đo đã chọn."]}
        if gia > 0 and res / 2 / gia > 0.01:
            cb = cb + [f"Độ chia của thang đo đáng kể so với thời gian rơi (sai số dụng cụ cỡ {res / 2 / gia * 100:.1f}%)."]
        return {"hop_le": True, "hien_thi": dinh_dang(gia, res), "gia_tri": gia, "don_vi": "s", "chan": [], "canh_bao": cb, "loi_thao_tac": loi}

    def do_chieu_dai(self, muc: str, ch: dict, lan: int, dung_cu: str) -> dict:
        if dung_cu not in self.dc or self.dc[dung_cu]["loai"] != "do_chieu_dai":
            return {"hop_le": False, "gia_tri": None, "chan": [f"'{dung_cu}' không phải dụng cụ đo độ dài."], "canh_bao": []}
        if muc != "quang_duong" or ch.get("s_dat_m") is None:
            return {"hop_le": False, "gia_tri": None, "chan": ["Chưa có đối tượng hợp lệ để đo."], "canh_bao": []}
        d_c = self.dc[dung_cu]
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "do_dai", dung_cu, round(ch["s_dat_m"], 4), lan)
        that = self._s_that(ch["s_dat_m"]) + self.lech
        gia = doc_so(that, d_c["do_chia_m"], d_c["sigma_m"], rng)
        cb = []
        if d_c["do_chia_m"] / 2 / gia > 0.02:
            cb.append(f"Độ chia của dụng cụ lớn so với đại lượng đo (sai số dụng cụ cỡ {d_c['do_chia_m'] / 2 / gia * 100:.1f}%).")
        return {"hop_le": True, "hien_thi": dinh_dang(gia, d_c["do_chia_m"]), "gia_tri": gia,
                "don_vi": "m", "chan": [], "canh_bao": cb}

    def gia_tri_ly_thuyet(self, thi_nghiem: str, ch: dict) -> float:
        return self.g
