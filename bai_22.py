"""mo_phong/bai_22.py – MÔ HÌNH Bài 22 "Thực hành tổng hợp lực" (chạy cục bộ / xưởng Python).

TN1 (đồng quy): dây cao su kéo dãn tới điểm O cố định, hợp lực của hai lực kế có độ lớn F_that (hướng ngược lực căng dây).
  Học sinh đặt hai góc α₁, α₂ (mỗi lực lệch so với phương hợp lực). Khi đó
  F₁ = F·sinα₂ / sin(α₁+α₂),  F₂ = F·sinα₁ / sin(α₁+α₂);  góc giữa hai lực θ = α₁+α₂.
  Sai số có chủ đích: lệch số 0 của lực kế (hệ thống), lệch thước đo góc (hệ thống), nhiễu đọc, ĐCNN 0,1 N, lực kế 5 N bị quá tải khi θ lớn.
TN2 (song song cùng chiều): thanh nhẹ AB, chùm n₁ quả nặng tại C, n₂ quả nặng tại D (mỗi quả 50 g). Một chùm (n₁+n₂) quả nặng treo tại O
  cho hai lò xo dãn như cũ: x_O = (F₁·x_C + F₂·x_D)/(F₁+F₂); khi đó F₁/F₂ = d₂/d₁ với d₁ = CO, d₂ = OD.
"""
from __future__ import annotations

import math

from .chung import chuan_cau_hinh, dinh_dang, doc_so, tao_rng

THI_NGHIEM = ("hop_luc_dong_quy", "hop_luc_song_song")
KHOA_CAU_HINH = ("goc1_do", "goc2_do", "n1", "n2", "vi_tri_c_m", "vi_tri_d_m")
MUC_LOAI = {"F1": "do_luc", "F2": "do_luc", "F_tn": "do_luc", "alpha1": "do_goc", "alpha2": "do_goc", "d1": "do_chieu_dai", "d2": "do_chieu_dai"}
DON_VI = {"do_luc": "N", "do_goc": "độ", "do_chieu_dai": "m"}


class MoPhong:
    KHOA_CAU_HINH = KHOA_CAU_HINH
    def __init__(self, bai: dict, ma_hs: str):
        self.bai, self.ma_hs = bai, ma_hs
        tp = bai["tham_so_that"]
        r = tao_rng(bai["ma_bai"], ma_hs, "tham_so_that")
        self.F = r.uniform(*tp["luc_day_cao_su_N"])
        self.lech0 = r.uniform(*tp["lech_khong_luc_ke_N"])
        self.lech_goc = r.uniform(*tp["lech_thuoc_do_goc_do"])
        self.lech_d = r.uniform(*tp["lech_thuoc_m"])
        self.W = tp["trong_luong_qua_nang_N"]
        self.L = tp["chieu_dai_thanh_m"]
        self.dc = bai["dung_cu"]

    # --- hình học thật của từng cấu hình ---
    def _loai_tn(self, ch: dict) -> str:
        return "hop_luc_dong_quy" if "goc1_do" in ch else "hop_luc_song_song"

    def _that_dong_quy(self, ch: dict) -> dict:
        r = tao_rng(self.bai["ma_bai"], self.ma_hs, "dat_goc", round(ch["goc1_do"], 2), round(ch["goc2_do"], 2))
        a1, a2 = ch["goc1_do"] + r.gauss(0, 0.8), ch["goc2_do"] + r.gauss(0, 0.8)
        th = math.radians(a1 + a2)
        return {"alpha1": a1, "alpha2": a2, "F_tn": self.F,
                "F1": self.F * math.sin(math.radians(a2)) / math.sin(th), "F2": self.F * math.sin(math.radians(a1)) / math.sin(th)}

    def _that_song_song(self, ch: dict) -> dict:
        f1, f2 = ch["n1"] * self.W, ch["n2"] * self.W
        xo = (f1 * ch["vi_tri_c_m"] + f2 * ch["vi_tri_d_m"]) / (f1 + f2)
        return {"F1": f1, "F2": f2, "d1": xo - ch["vi_tri_c_m"], "d2": ch["vi_tri_d_m"] - xo}

    def kiem_tra(self, thi_nghiem: str, ch: dict) -> tuple[list[str], list[str]]:
        chan, cb = [], []
        if thi_nghiem not in THI_NGHIEM:
            return [f"Thí nghiệm '{thi_nghiem}' không có trong bài này."], cb
        if thi_nghiem == "hop_luc_dong_quy":
            a1, a2 = ch.get("goc1_do"), ch.get("goc2_do")
            if a1 is None or a2 is None:
                return ["Chưa đặt hướng kéo của hai lực kế (goc1_do, goc2_do: góc lệch so với phương hợp lực)."], cb
            if not (10 <= a1 <= 80 and 10 <= a2 <= 80):
                return ["Mỗi góc lệch phải nằm trong khoảng 10° đến 80° để hai lực kế kéo được dây cao su tới O."], cb
            t = self._that_dong_quy(ch)
            if max(t["F1"], t["F2"]) > self.dc["luc_ke_5N"]["toi_da"]:
                chan.append("Góc giữa hai lực quá lớn: một lực kế phải chịu lực vượt giới hạn đo 5 N. Hãy giảm góc.")
            if a1 + a2 < 30:
                cb.append("Góc giữa hai lực rất nhỏ: hai lực gần cùng phương, khó kiểm nghiệm quy tắc hình bình hành.")
        else:
            n1, n2, c, d = (ch.get(k) for k in ("n1", "n2", "vi_tri_c_m", "vi_tri_d_m"))
            if None in (n1, n2, c, d):
                return ["Chưa đặt số quả nặng (n1, n2) và vị trí C, D trên thanh (vi_tri_c_m, vi_tri_d_m)."], cb
            if not (isinstance(n1, int) and isinstance(n2, int) and 1 <= n1 <= 4 and 1 <= n2 <= 4):
                chan.append("Mỗi chùm có từ 1 đến 4 quả nặng 50 g (số nguyên).")
            if not (0.02 <= c < d <= self.L - 0.02) or d - c < 0.04:
                chan.append(f"C và D phải nằm trên thanh dài {self.L:.2f} m (cách hai đầu ≥ 0,02 m), C ở gần A hơn D và cách D ≥ 0,04 m.")
        return chan, cb

    def do_thoi_gian(self, thi_nghiem: str, ch: dict, lan: int) -> dict:
        return {"hop_le": False, "hien_thi": None, "gia_tri": None, "don_vi": "s",
                "chan": ["Bài này không đo thời gian; đại lượng đo là lực, góc và độ dài."], "canh_bao": []}

    def do_chieu_dai(self, muc: str, ch: dict, lan: int, dung_cu: str) -> dict:
        """Đọc MỘT lần một đại lượng (F1, F2, F_tn, alpha1, alpha2, d1, d2); loại dụng cụ phải khớp đại lượng."""
        sai = lambda m: {"hop_le": False, "hien_thi": None, "gia_tri": None, "chan": [m], "canh_bao": []}
        if muc not in MUC_LOAI:
            return sai(f"Đại lượng '{muc}' không có trong bài này. Có thể đo: {', '.join(MUC_LOAI)}.")
        if dung_cu not in self.dc or self.dc[dung_cu]["loai"] != MUC_LOAI[muc]:
            return sai(f"'{dung_cu}' không đo được đại lượng '{muc}'.")
        dq, ss = "goc1_do" in ch, "n1" in ch
        if muc == "F_tn":
            t, cb0 = {"F_tn": self.F}, []
        else:
            if muc in ("alpha1", "alpha2") and not dq or muc in ("d1", "d2") and not ss or muc in ("F1", "F2") and not (dq or ss):
                return sai(f"Cấu hình chưa đủ để đo '{muc}': với TN1 cần goc1_do, goc2_do; với TN2 cần n1, n2, vi_tri_c_m, vi_tri_d_m.")
            chan, cb0 = self.kiem_tra("hop_luc_dong_quy" if dq else "hop_luc_song_song", ch)
            if chan:
                return sai("; ".join(chan))
            t = self._that_dong_quy(ch) if dq else self._that_song_song(ch)
        d_c = self.dc[dung_cu]
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "doc", muc, dung_cu, chuan_cau_hinh({k: ch[k] for k in KHOA_CAU_HINH if k in ch}), lan)
        that = t[muc]
        if d_c["loai"] == "do_luc":
            if that > d_c["toi_da"]:
                return sai(f"Lực {that:.1f} N vượt giới hạn đo {d_c['toi_da']} N của {d_c['ten']}; không đọc được.")
            that += self.lech0
        elif d_c["loai"] == "do_goc":
            that += self.lech_goc
        else:
            that += self.lech_d
        gia = doc_so(that, d_c["do_chia"], d_c["sigma"], rng)
        cb = list(cb0)
        if d_c["loai"] == "do_luc" and gia < 0.3:
            cb.append("Số chỉ nhỏ so với ĐCNN: sai số tỉ đối của phép đo lực này lớn.")
        return {"hop_le": True, "hien_thi": dinh_dang(gia, d_c["do_chia"]), "gia_tri": gia, "don_vi": DON_VI[d_c["loai"]], "chan": [], "canh_bao": cb}

    def gia_tri_ly_thuyet(self, thi_nghiem: str, ch: dict) -> float:
        return self.F

    # --- chấm ---
    def _gom(self, du_lieu: list[dict], tn: str) -> dict:
        nhom: dict[str, dict] = {}
        for d in du_lieu:
            if d["muc"] == "F_tn":                       # lực dây cao su: dùng chung cho mọi cấu hình của TN1
                if tn == "hop_luc_dong_quy":
                    nhom.setdefault("*", {}).setdefault("F_tn", []).append(d["gia_tri"])
            elif d["thi_nghiem"] == tn:
                nhom.setdefault(d["khoa"].split("|")[1], {}).setdefault(d["muc"], []).append(d["gia_tri"])
        return nhom

    def tinh_lai(self, loai: str, du_lieu: list[dict]):
        tb = lambda ds: sum(ds) / len(ds)
        if loai in ("F_lt", "F_tn"):
            g = self._gom(du_lieu, "hop_luc_dong_quy")
            if loai == "F_tn":
                return tb(g["*"]["F_tn"]) if g.get("*", {}).get("F_tn") else None
            kq = []
            for k, m in g.items():
                if k != "*" and all(m.get(x) for x in ("F1", "F2", "alpha1", "alpha2")):
                    f1, f2, th = tb(m["F1"]), tb(m["F2"]), math.radians(tb(m["alpha1"]) + tb(m["alpha2"]))
                    kq.append(math.sqrt(f1 ** 2 + f2 ** 2 + 2 * f1 * f2 * math.cos(th)))
            return kq or None
        g = self._gom(du_lieu, "hop_luc_song_song")
        if loai == "ti_le_luc":
            kq = [tb(m["F1"]) / tb(m["F2"]) for m in g.values() if m.get("F1") and m.get("F2")]
        elif loai == "ti_le_khoang_cach":
            kq = [tb(m["d2"]) / tb(m["d1"]) for m in g.values() if m.get("d1") and m.get("d2")]
        else:
            return None
        return kq or None

    def du_lan(self, y: dict, du_lieu: list[dict]) -> bool:
        n = y["do_dai"]["so_lan_toi_thieu"]
        g = self._gom(du_lieu, y["thi_nghiem"])
        if y["thi_nghiem"] == "hop_luc_dong_quy":
            if len(g.get("*", {}).get("F_tn", [])) < n:
                return False
            muc = ("F1", "F2", "alpha1", "alpha2")
        else:
            muc = ("F1", "F2", "d1", "d2")
        dat = [k for k, m in g.items() if k != "*" and all(len(m.get(x, [])) >= n for x in muc)]
        return len(dat) >= y["so_cau_hinh_toi_thieu"]
