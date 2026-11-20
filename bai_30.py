"""mo_phong/bai_30.py – MÔ HÌNH Bài 30 "Xác định động lượng trước và sau va chạm" (đệm khí, hai cổng quang).

Mỗi LẦN đo là một lần va chạm; lần k ở cổng 1 và lần k ở cổng 2 thuộc CÙNG một va chạm (cùng v₁ ngẫu nhiên của lần đẩy).
  Va chạm mềm: xe 1 (m₁, tốc độ v₁ qua cổng 1) dính xe 2 đứng yên (m₂) -> cả hệ qua cổng 2 với
      v₁₂ = m₁v₁/(m₁+m₂)·(1 − ε),  ε = hao hụt hệ thống nhỏ (ma sát còn lại của đệm khí, ẩn) cộng nhiễu.
  Đẩy bằng lò xo: hệ đứng yên p = 0 -> xe 1 qua cổng 1, xe 2 qua cổng 2; m₁v₁ = m₂v₂·(1 + e).
  Tốc độ tính từ thời gian chắn sáng: v = d/Δt (d = bề rộng tấm cản quang, đo bằng thước cặp).
Khối lượng xe: m = m₀ + 0,05·(số quả cân thêm) – học sinh phải cân từng xe bằng cân điện tử.
"""
from __future__ import annotations

import math

from .chung import chuan_cau_hinh, dinh_dang, doc_so, luong_tu_hoa, tao_rng

THI_NGHIEM = ("va_cham_mem", "day_lo_xo")
KHOA_CAU_HINH = ("cong", "xe", "qua_can_xe1", "qua_can_xe2")
MUC_LOAI = {"m1": "can", "m2": "can", "d": "do_chieu_dai"}
DONG_HO_MAC_DINH = "mc964"
KHOI_LUONG_QUA_CAN = 0.05


class MoPhong:
    KHOA_CAU_HINH = KHOA_CAU_HINH
    DONG_HO_MAC_DINH = DONG_HO_MAC_DINH
    def __init__(self, bai: dict, ma_hs: str):
        self.bai, self.ma_hs = bai, ma_hs
        tp = bai["tham_so_that"]
        r = tao_rng(bai["ma_bai"], ma_hs, "tham_so_that")
        self.m0 = (r.uniform(*tp["khoi_luong_xe_kg"]), r.uniform(*tp["khoi_luong_xe_kg"]))
        self.d = r.uniform(*tp["be_rong_tam_chan_m"])
        self.eps = r.uniform(*tp["hao_hut_va_cham_mem"])
        self.e_day = r.uniform(*tp["lech_day_lo_xo"])
        self.v_min, self.v_max = tp["toc_do_xe1_m_s"]
        self.dc = bai["dung_cu"]

    def _m(self, ch: dict) -> tuple[float, float]:
        return (self.m0[0] + KHOI_LUONG_QUA_CAN * ch.get("qua_can_xe1", 0), self.m0[1] + KHOI_LUONG_QUA_CAN * ch.get("qua_can_xe2", 0))

    def _kiem_khoi_luong(self, ch: dict) -> list[str]:
        n = [ch.get("qua_can_xe1"), ch.get("qua_can_xe2")]
        if any(not isinstance(x, int) or not 0 <= x <= 4 for x in n):
            return ["Số quả cân thêm trên mỗi xe là số nguyên từ 0 đến 4 (qua_can_xe1, qua_can_xe2)."]
        return []

    def kiem_tra(self, thi_nghiem: str, ch: dict) -> tuple[list[str], list[str]]:
        chan, cb = [], []
        if thi_nghiem not in THI_NGHIEM:
            return [f"Thí nghiệm '{thi_nghiem}' không có trong bài này."], cb
        dh = ch.get("dong_ho", DONG_HO_MAC_DINH)
        if dh not in self.dc or self.dc[dh]["loai"] != "do_thoi_gian":
            return [f"'{dh}' không phải dụng cụ đo thời gian trong bộ thí nghiệm."], cb
        if ch.get("thang_do") not in (None, *self.dc[dh]["thang_do"]):
            chan.append("Đồng hồ này không có thang đo em chọn.")
        if self.dc[dh].get("sigma_s", 0) > 0.01:
            chan.append("Thời gian chắn sáng chỉ cỡ vài chục mili giây; đồng hồ bấm tay không đo được. Hãy dùng đồng hồ hiện số với cổng quang điện.")
        chan += self._kiem_khoi_luong(ch)
        cong, xe = ch.get("cong"), ch.get("xe")
        if cong not in (1, 2) or xe not in (1, 2):
            chan.append("Hãy nêu rõ cổng quang (cong: 1 hoặc 2) và xe đi qua (xe: 1 hoặc 2).")
        elif thi_nghiem == "va_cham_mem" and (cong, xe) not in ((1, 1), (2, 1), (2, 2)):
            chan.append("Va chạm mềm: xe 2 đứng yên giữa hai cổng, trước va chạm không qua cổng 1; chỉ xe 1 qua cổng 1.")
        elif thi_nghiem == "day_lo_xo" and cong != xe:
            chan.append("Đẩy bằng lò xo: xe 1 đi về phía cổng 1, xe 2 về phía cổng 2; hãy chọn cổng ứng với xe của em.")
        return chan, cb

    def _bien_co(self, thi_nghiem: str, ch: dict, lan: int) -> dict:
        """Một lần va chạm (lần lan): các tốc độ thật. Không phụ thuộc cổng -> hai cổng cùng một va chạm."""
        m1, m2 = self._m(ch)
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "va_cham", thi_nghiem, ch.get("qua_can_xe1"), ch.get("qua_can_xe2"), lan)
        if thi_nghiem == "va_cham_mem":
            v1 = rng.uniform(self.v_min, self.v_max)
            v12 = m1 * v1 / (m1 + m2) * (1 - self.eps - abs(rng.gauss(0, 0.004)))
            return {(1, 1): v1, (2, 1): v12, (2, 2): v12}
        e = self.e_day + rng.gauss(0, 0.01)
        v1 = rng.uniform(self.v_min, self.v_max)
        return {(1, 1): v1, (2, 2): m1 * v1 / m2 * (1 + e)}

    def do_thoi_gian(self, thi_nghiem: str, ch: dict, lan: int) -> dict:
        chan, cb = self.kiem_tra(thi_nghiem, ch)
        if chan:
            return {"hop_le": False, "hien_thi": None, "gia_tri": None, "don_vi": "s", "chan": chan, "canh_bao": cb}
        dh = self.dc[ch.get("dong_ho", DONG_HO_MAC_DINH)]
        tdo = dh["thang_do"][ch.get("thang_do") or next(iter(dh["thang_do"]))]
        if ch.get("mode", "A") != "A":
            return {"hop_le": True, "hien_thi": "----", "gia_tri": None, "don_vi": "s", "chan": [], "loi_thao_tac": True,
                    "canh_bao": cb + ["Đồng hồ không hiển thị thời gian chắn sáng của một cổng ở MODE này. Hãy kiểm tra lại MODE."]}
        v = self._bien_co(thi_nghiem, ch, lan)[(ch["cong"], ch["xe"])]
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "do_t", thi_nghiem, chuan_cau_hinh({k: ch[k] for k in KHOA_CAU_HINH if k in ch}), lan)
        gia = luong_tu_hoa(self.d / v + rng.gauss(0, dh["sigma_s"]), tdo["do_chia_s"])
        if gia > tdo["toi_da_s"]:
            return {"hop_le": True, "hien_thi": "OvEr", "gia_tri": None, "don_vi": "s", "chan": [], "canh_bao": cb + ["Giá trị vượt thang đo đã chọn."]}
        if gia > 0 and tdo["do_chia_s"] / 2 / gia > 0.01:
            cb = cb + [f"Độ chia của thang đo đáng kể so với thời gian chắn sáng (sai số dụng cụ cỡ {tdo['do_chia_s'] / 2 / gia * 100:.1f}%). Hãy cân nhắc thang đo mịn hơn."]
        return {"hop_le": True, "hien_thi": dinh_dang(gia, tdo["do_chia_s"]), "gia_tri": gia, "don_vi": "s", "chan": [], "canh_bao": cb}

    def do_chieu_dai(self, muc: str, ch: dict, lan: int, dung_cu: str) -> dict:
        """Đọc khối lượng xe (m1, m2; cân điện tử) hoặc bề rộng tấm cản quang (d; thước cặp)."""
        sai = lambda m: {"hop_le": False, "hien_thi": None, "gia_tri": None, "chan": [m], "canh_bao": []}
        if muc not in MUC_LOAI:
            return sai(f"Đại lượng '{muc}' không có trong bài này. Có thể đo: m1, m2, d.")
        if dung_cu not in self.dc or self.dc[dung_cu]["loai"] != MUC_LOAI[muc]:
            return sai(f"'{dung_cu}' không đo được đại lượng '{muc}'.")
        if muc != "d" and (chan := self._kiem_khoi_luong(ch)):
            return sai(chan[0])
        d_c = self.dc[dung_cu]
        that = self.d if muc == "d" else self._m(ch)[0 if muc == "m1" else 1]
        if that > d_c["toi_da"]:
            return sai(f"{d_c['ten']} có giới hạn đo {d_c['toi_da']}; vật vượt giới hạn.")
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "do_vl", muc, dung_cu, ch.get("qua_can_xe1"), ch.get("qua_can_xe2"), lan)
        gia = doc_so(that, d_c["do_chia"], d_c["sigma"], rng)
        cb = [f"Độ chia của dụng cụ lớn so với đại lượng đo (sai số dụng cụ cỡ {d_c['do_chia'] / 2 / gia * 100:.1f}%)."] if gia > 0 and d_c["do_chia"] / 2 / gia > 0.02 else []
        return {"hop_le": True, "hien_thi": dinh_dang(gia, d_c["do_chia"]), "gia_tri": gia, "don_vi": "m" if muc == "d" else "kg", "chan": [], "canh_bao": cb}

    def gia_tri_ly_thuyet(self, thi_nghiem: str, ch: dict) -> float:
        return 0.0

    # --- chấm ---
    def _gom(self, du_lieu: list[dict], tn: str) -> tuple[dict, dict, list]:
        """-> (theo cấu hình khối lượng: {m1, m2, t:{(cong,xe): [..]}}, bề rộng d, [])"""
        cfg: dict[tuple, dict] = {}
        ds: list[float] = []
        for r in du_lieu:
            c = r["cau_hinh"]
            if r["loai"] == "do_dai" and r["muc"] == "d":
                ds.append(r["gia_tri"])
            elif r["loai"] == "do_dai":
                if r["thi_nghiem"] == tn:
                    g = cfg.setdefault((c.get("qua_can_xe1"), c.get("qua_can_xe2")), {"m1": [], "m2": [], "t": {}})
                    g[r["muc"]].append(r["gia_tri"])
            elif r["thi_nghiem"] == tn:
                g = cfg.setdefault((c.get("qua_can_xe1"), c.get("qua_can_xe2")), {"m1": [], "m2": [], "t": {}})
                g["t"].setdefault((c.get("cong"), c.get("xe")), []).append(r["gia_tri"])
        return cfg, {"d": ds}, []

    def tinh_lai(self, loai: str, du_lieu: list[dict]):
        tb = lambda x: sum(x) / len(x)
        tn = "day_lo_xo" if loai == "ti_so_p_day" else "va_cham_mem"
        cfg, dd, _ = self._gom(du_lieu, tn)
        kq = []
        for g in cfg.values():
            if not (g["m1"] and g["m2"]):
                continue
            m1, m2, t = tb(g["m1"]), tb(g["m2"]), {k: tb(v) for k, v in g["t"].items()}
            if loai == "p_truoc" and (1, 1) in t and dd["d"]:
                kq.append(m1 * tb(dd["d"]) / t[(1, 1)])
            elif loai == "p_sau" and (2, 1) in t and dd["d"]:
                kq.append((m1 + m2) * tb(dd["d"]) / t[(2, 1)])
            elif loai == "ti_so_p_day" and (1, 1) in t and (2, 2) in t:
                kq.append(m2 * t[(1, 1)] / (m1 * t[(2, 2)]))
        return kq or None

    def du_lan(self, y: dict, du_lieu: list[dict]) -> bool:
        n = y["do_dai"]["so_lan_toi_thieu"]
        cfg, dd, _ = self._gom(du_lieu, y["thi_nghiem"])
        if len(dd["d"]) < n:
            return False
        cong = ((1, 1), (2, 1)) if y["thi_nghiem"] == "va_cham_mem" else ((1, 1), (2, 2))
        dat = [g for g in cfg.values() if len(g["m1"]) >= n and len(g["m2"]) >= n and all(len(g["t"].get(k, [])) >= y["so_lan_t_toi_thieu"] for k in cong)]
        return len(dat) >= y["so_cau_hinh_toi_thieu"]
