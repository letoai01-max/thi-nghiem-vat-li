"""mo_phong/bai_03.py – MÔ HÌNH Bài 3 "Tính sai số trong phép đo. Ghi kết quả đo" (xe đồ chơi chạy pin).

Thế giới mô phỏng: xe chạy thẳng với tốc độ gần không đổi v (mỗi lượt chạy dao động nhẹ ~1%).
  t_doc = s / v_i + tre + nhieu_bam_tay        (tre: lệch hệ thống do bấm dừng trễ hơn bấm bắt đầu, ẩn)
  s_doc = s_that + lech_thuoc + nhieu_dat_thuoc (lech_thuoc: lệch điểm 0 của thước, ẩn)
Mục đích sư phạm: sai số ngẫu nhiên do phản xạ người bấm là nguồn sai số chính; học sinh phải đo nhiều lần,
tính trung bình, sai số ngẫu nhiên, sai số dụng cụ (ĐCNN/2) và sai số gián tiếp δv = δs + δt.
"""
from __future__ import annotations

from . import sai_so
from .chung import dinh_dang, doc_so, luong_tu_hoa, tao_rng

THI_NGHIEM = ("xe_do_choi",)
KHOA_CAU_HINH = ("s_dat_m",)
DONG_HO_MAC_DINH = "dong_ho_bam_giay"


class MoPhong:
    KHOA_CAU_HINH = KHOA_CAU_HINH
    DONG_HO_MAC_DINH = DONG_HO_MAC_DINH
    def __init__(self, bai: dict, ma_hs: str):
        self.bai, self.ma_hs = bai, ma_hs
        tp = bai["tham_so_that"]
        r = tao_rng(bai["ma_bai"], ma_hs, "tham_so_that")
        self.v = r.uniform(*tp["toc_do_xe_m_s"])
        self.tre = r.uniform(*tp["lech_bam_tay_s"])
        self.lech = r.uniform(*tp["lech_thuoc_m"])
        self.L = tp["duong_chay_toi_da_m"]
        self.dc = bai["dung_cu"]

    def kiem_tra(self, thi_nghiem: str, ch: dict) -> tuple[list[str], list[str]]:
        chan, cb = [], []
        if thi_nghiem not in THI_NGHIEM:
            return [f"Thí nghiệm '{thi_nghiem}' không có trong bài này."], cb
        dh = ch.get("dong_ho", DONG_HO_MAC_DINH)
        if dh not in self.dc or self.dc[dh]["loai"] != "do_thoi_gian":
            return [f"'{dh}' không phải dụng cụ đo thời gian trong bộ thí nghiệm."], cb
        if ch.get("thang_do") not in (None, *self.dc[dh]["thang_do"]):
            chan.append("Đồng hồ này không có thang đo em chọn.")
        s = ch.get("s_dat_m")
        if s is None:
            chan.append("Chưa đặt quãng đường chạy s (khoảng cách giữa vạch xuất phát và vạch đích).")
        elif s < 0.3 or s > self.L:
            chan.append(f"Đường chạy của xe dài 0,3 m đến {self.L:.1f} m. Hãy chọn s trong khoảng đó.")
        elif s < 0.8:
            cb.append("Quãng đường ngắn: thời gian chạy chỉ vài giây nên sai số tỉ đối do bấm tay sẽ lớn.")
        return chan, cb

    def do_thoi_gian(self, thi_nghiem: str, ch: dict, lan: int) -> dict:
        chan, cb = self.kiem_tra(thi_nghiem, ch)
        if chan:
            return {"hop_le": False, "hien_thi": None, "gia_tri": None, "don_vi": "s", "chan": chan, "canh_bao": cb}
        dh = self.dc[ch.get("dong_ho", DONG_HO_MAC_DINH)]
        tdo = dh["thang_do"][ch.get("thang_do") or next(iter(dh["thang_do"]))]
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "chay", round(ch["s_dat_m"], 4), lan)
        v_i = self.v * (1 + rng.gauss(0, 0.01))
        t = max(ch["s_dat_m"] / v_i + self.tre + rng.gauss(0, dh["sigma_s"]), tdo["do_chia_s"])
        gia = luong_tu_hoa(t, tdo["do_chia_s"])
        if gia > tdo["toi_da_s"]:
            return {"hop_le": True, "hien_thi": "OvEr", "gia_tri": None, "don_vi": "s", "chan": [],
                    "canh_bao": cb + ["Giá trị vượt thang đo của đồng hồ."]}
        if dh["sigma_s"] > 5 * tdo["do_chia_s"]:
            cb = cb + ["Độ chia nhỏ hơn nhiều so với dao động của các lần đo: số chữ số thập phân không phản ánh độ chính xác thực."]
        return {"hop_le": True, "hien_thi": dinh_dang(gia, tdo["do_chia_s"]), "gia_tri": gia, "don_vi": "s", "chan": [], "canh_bao": cb}

    def do_chieu_dai(self, muc: str, ch: dict, lan: int, dung_cu: str) -> dict:
        if dung_cu not in self.dc or self.dc[dung_cu]["loai"] != "do_chieu_dai":
            return {"hop_le": False, "gia_tri": None, "chan": [f"'{dung_cu}' không phải dụng cụ đo độ dài."], "canh_bao": []}
        if muc != "quang_duong" or ch.get("s_dat_m") is None:
            return {"hop_le": False, "gia_tri": None, "chan": ["Chưa có đối tượng hợp lệ để đo (hãy đặt s_dat_m và đo 'quang_duong')."], "canh_bao": []}
        d_c = self.dc[dung_cu]
        if ch["s_dat_m"] > d_c["toi_da_m"]:
            return {"hop_le": False, "gia_tri": None, "chan": [f"{d_c['ten']} chỉ đo tới {d_c['toi_da_m']} m; quãng đường dài hơn giới hạn đo (GHĐ)."], "canh_bao": []}
        rng = tao_rng(self.bai["ma_bai"], self.ma_hs, "do_dai", dung_cu, round(ch["s_dat_m"], 4), lan)
        gia = doc_so(ch["s_dat_m"] + self.lech, d_c["do_chia_m"], d_c["sigma_m"], rng)
        cb = []
        if d_c["do_chia_m"] / 2 / gia > 0.02:
            cb.append(f"Độ chia của dụng cụ lớn so với đại lượng đo (sai số dụng cụ cỡ {d_c['do_chia_m'] / 2 / gia * 100:.1f}%).")
        return {"hop_le": True, "hien_thi": dinh_dang(gia, d_c["do_chia_m"]), "gia_tri": gia, "don_vi": "m", "chan": [], "canh_bao": cb}

    def gia_tri_ly_thuyet(self, thi_nghiem: str, ch: dict) -> float:
        return self.v

    # --- chấm: tính lại từ chính số liệu đã cấp ---
    def _gom(self, du_lieu: list[dict]) -> dict:
        nhom: dict[str, dict] = {}
        for d in du_lieu:
            if d["thi_nghiem"] not in THI_NGHIEM:
                continue
            g = nhom.setdefault(d["khoa"].split("|")[1], {"t": [], "s": [], "dh": None, "dc": None, "ch": d["cau_hinh"]})
            if d["loai"] == "thoi_gian":
                g["t"].append(d["gia_tri"])
                g["dh"] = d["cau_hinh"]
            else:
                g["s"].append(d["gia_tri"])
                g["dc"] = d["dung_cu"]
        return nhom

    def _dcnn_t(self, ch: dict) -> float:
        dh = self.dc[ch.get("dong_ho", DONG_HO_MAC_DINH)]
        return dh["thang_do"][ch.get("thang_do") or next(iter(dh["thang_do"]))]["do_chia_s"]

    def tinh_lai(self, loai: str, du_lieu: list[dict]):
        kq = []
        for g in self._gom(du_lieu).values():
            if not g["t"] or not g["s"]:
                continue
            v = sai_so.trung_binh(g["s"]) / sai_so.trung_binh(g["t"])
            if loai == "v_xe":
                kq.append(v)
            elif loai == "dv":
                ds = sai_so.sai_so_tuyet_doi(g["s"], self.dc[g["dc"]]["do_chia_m"])
                dt = sai_so.sai_so_tuyet_doi(g["t"], self._dcnn_t(g["dh"]))
                kq.append((ds / sai_so.trung_binh(g["s"]) + dt / sai_so.trung_binh(g["t"])) * v)
        return kq or None

    def du_lan(self, y: dict, du_lieu: list[dict]) -> bool:
        dat = [g for g in self._gom(du_lieu).values()
               if len(g["t"]) >= y["so_lan_t_toi_thieu"] and len(g["s"]) >= y["do_dai"]["so_lan_toi_thieu"]]
        return len(dat) >= y["so_cau_hinh_toi_thieu"]
