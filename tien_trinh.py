"""tien_trinh.py – CỔNG SƯ PHẠM của agent thí nghiệm mô phỏng (chạy cục bộ / xưởng Python).

Luồng: 4 pha cố định  vao_lab -> chon_dung_cu_lap_rap -> do_nhieu_lan -> xu_ly_ket_luan.
Đây là nơi THỰC THI (bằng code, không chỉ bằng lời nhắc) các quy tắc của file Word:
  1. Không phát số liệu trước khi học sinh khai báo dự đoán, biến số, phương án và chọn dụng cụ, lắp ráp đúng.
  2. Gợi ý theo 3 nấc; chỉ mở nấc kế khi học sinh đã thử đủ số lần. Xin đáp án -> từ chối, không "bẻ lái" được.
  3. Số liệu sinh ra có tính nhất quán nội tại (engine tất định); cảnh báo khi chọn sai dụng cụ/thang đo.
  4. Chấm kết quả nộp bằng cách tính lại từ CHÍNH số liệu đã cấp cho học sinh.
Biến môi trường: không cần. Thông số bài nằm ở bai_hoc/*.json, công tắc ở cau_hinh.json (một nguồn sự thật).
"""
from __future__ import annotations

import json
from pathlib import Path

from mo_phong import bai_03, bai_06, bai_11, bai_22, bai_30, sai_so
from mo_phong.chung import chuan_cau_hinh
from nhat_ky import MA_HS_HOP_LE, NhatKy, khong_dau

GOC = Path(__file__).parent
MO_HINH = {"mang_nghieng_bi_thep": bai_06.MoPhong, "roi_tu_do_tru_thep": bai_11.MoPhong,
           "xe_do_choi": bai_03.MoPhong, "tong_hop_luc": bai_22.MoPhong, "dem_khi_va_cham": bai_30.MoPhong}
KHOA_CU = ("vi_tri_e_m", "vi_tri_f_m", "vi_tri_cong_m", "s_dat_m", "vat")   # khoá cấu hình của Bài 6, 11
PHA = ("vao_lab", "chon_dung_cu_lap_rap", "do_nhieu_lan", "xu_ly_ket_luan")


def nap_bai(ma_bai: str) -> dict:
    return json.loads((GOC / "bai_hoc" / f"{ma_bai}.json").read_text(encoding="utf-8"))


def nap_cau_hinh() -> dict:
    return json.loads((GOC / "cau_hinh.json").read_text(encoding="utf-8"))


NHAN_THI_NGHIEM = {"toc_do_trung_binh": "Tốc độ trung bình (E→F)", "toc_do_tuc_thoi": "Tốc độ tức thời (một cổng)", "roi_tu_do": "Rơi tự do",
                   "xe_do_choi": "Xe đồ chơi chạy pin", "hop_luc_dong_quy": "Tổng hợp hai lực đồng quy", "hop_luc_song_song": "Tổng hợp hai lực song song cùng chiều",
                   "va_cham_mem": "Va chạm mềm", "day_lo_xo": "Hai xe đẩy nhau bằng lò xo"}
NHAN_DAI_LUONG = {"t": "t (s)", "quang_duong": "s (m)", "duong_kinh": "d (m)", "F1": "F₁ (N)", "F2": "F₂ (N)", "F_tn": "F_tn (N)",
                  "alpha1": "α₁ (độ)", "alpha2": "α₂ (độ)", "d1": "d₁ (m)", "d2": "d₂ (m)", "m1": "m₁ (kg)", "m2": "m₂ (kg)", "d": "d (m)"}
NHAN_KHOA_MOI = {"goc1_do": "α₁ đặt", "goc2_do": "α₂ đặt", "n1": "số quả nặng C", "n2": "số quả nặng D", "vi_tri_c_m": "C cách A",
                 "vi_tri_d_m": "D cách A", "cong": "cổng", "xe": "xe", "qua_can_xe1": "quả cân thêm xe 1", "qua_can_xe2": "quả cân thêm xe 2"}
NHAN_VAT = {"tru_thep": "trụ thép", "vien_bi": "viên bi thép"}


def phay(x) -> str:
    """Số thập phân kiểu Việt Nam (dấu phẩy) để hiển thị cho học sinh."""
    return str(x).replace(".", ",")


def mo_ta_cau_hinh(cau: dict) -> str:
    """Mô tả cấu hình bằng chữ dễ đọc, không lộ khoá kỹ thuật."""
    nhan = {"vi_tri_e_m": "E cách chỗ thả", "vi_tri_f_m": "F cách chỗ thả", "vi_tri_cong_m": "cổng cách chỗ thả", "s_dat_m": "cổng cách nam châm"}
    phan = [f"{nhan[k]} {phay(f'{v:.3f}'.rstrip('0').rstrip('.'))} m" for k, v in cau.items() if k in nhan]
    phan += [f"{NHAN_KHOA_MOI[k]} = {phay(v)}" for k, v in cau.items() if k in NHAN_KHOA_MOI]
    if "vat" in cau:
        phan.append(NHAN_VAT.get(cau["vat"], cau["vat"]))
    return "; ".join(phan)


def _ok(thong_diep: str, **them) -> dict:
    return {"ok": True, "thong_diep": thong_diep, **them}


def _tu_choi(thong_diep: str, **them) -> dict:
    return {"ok": False, "thong_diep": thong_diep, **them}


class PhienThucHanh:
    def __init__(self, bai: dict, ma_hs: str, cau_hinh: dict | None = None, nhat_ky: NhatKy | None = None):
        if not MA_HS_HOP_LE.match(ma_hs):
            raise ValueError("Mã học sinh chỉ gồm chữ/số/gạch (2–16 ký tự), không dùng tên thật.")
        self.bai, self.ma_hs = bai, ma_hs
        self.cfg = cau_hinh or nap_cau_hinh()
        self.mo_phong = MO_HINH[bai["mo_hinh"]](bai, ma_hs)
        self.nk = nhat_ky or NhatKy(GOC / "nhat_ky", bat=self.cfg["cong_tac"]["GHI_NHAT_KY"])
        self.pha = 0
        self.cau_vao_dat: set[str] = set()
        self.khai_bao: dict[str, str] = {}
        self.dung_cu_chon: set[str] = set()
        self.buoc_lap_rap: list[str] = []
        self.so_lan_thu: dict[str, int] = {}
        self.muc_goi_y: dict[str, int] = {}
        self.so_lan_xin_dap_an = 0
        self.can_giao_vien = False
        self.du_lieu: list[dict] = []          # mọi số liệu đã cấp cho học sinh
        self.ket_qua_dat: set[str] = set()
        self.ket_luan_dat: set[str] = set()
        self.canh_bao_da_gap: list[str] = []

    # ---------------- tiện ích ----------------
    def _log(self, su_kien: str, **ct) -> None:
        self.nk.ghi(self.ma_hs, self.bai["ma_bai"], su_kien, pha=PHA[self.pha], **ct)

    def trang_thai(self) -> dict:
        return {"bai": self.bai["ten_bai"], "pha": PHA[self.pha], "so_pha": f"{self.pha + 1}/4",
                "cau_vao_dat": sorted(self.cau_vao_dat), "da_khai_bao": sorted(self.khai_bao),
                "dung_cu_da_chon": sorted(self.dung_cu_chon), "so_so_lieu_da_cap": len(self.du_lieu),
                "con_thieu_de_qua_pha": [k for k in self._dieu_kien_pha() if not self._dat(k)]}

    # ---------------- pha 0: điều kiện vào lab ----------------
    def tra_loi_cau_vao(self, id_cau: str, noi_dung: str, dat: bool | None = None) -> dict:
        cau = next((c for c in self.bai["cau_vao"] if c["id"] == id_cau), None)
        if cau is None:
            return _tu_choi("Không có câu hỏi vào lab này.")
        if dat is None:  # chế độ ngoại tuyến: so khớp nhóm từ khoá
            nd = khong_dau(noi_dung)
            dat = all(any(khong_dau(tk) in nd for tk in nhom) for nhom in cau["nhom_tu_khoa"])
        self.so_lan_thu["cau_vao"] = self.so_lan_thu.get("cau_vao", 0) + 1
        self._log("tra_loi_cau_vao", id=id_cau, dat=dat, noi_dung=noi_dung)
        if dat:
            self.cau_vao_dat.add(id_cau)
            return _ok("Đạt câu này.", con_lai=len(self.bai["cau_vao"]) - len(self.cau_vao_dat))
        return _tu_choi("Chưa đủ ý. Em xem lại kiến thức nền rồi trả lời lại nhé.", cau_hoi=cau["cau_hoi"])

    # ---------------- pha 1: khai báo, chọn dụng cụ, lắp ráp ----------------
    def ghi_khai_bao(self, loai: str, noi_dung: str) -> dict:
        if loai not in self.bai["khai_bao"]:
            return _tu_choi(f"Loại khai báo hợp lệ: {', '.join(self.bai['khai_bao'])}.")
        if self.pha < 1:
            return _tu_choi("Hãy hoàn thành điều kiện vào lab trước.", pha_hien_tai=PHA[self.pha])
        so_tu = len(noi_dung.split())
        if so_tu < self.cfg["do_dai_toi_thieu_tu"]:
            return _tu_choi(f"Câu trả lời còn quá ngắn ({so_tu} từ). Hãy nêu rõ ý và lí do.", cau_hoi=self.bai["khai_bao"][loai]["cau_hoi"])
        self.khai_bao[loai] = noi_dung
        self.so_lan_thu[loai] = self.so_lan_thu.get(loai, 0) + 1
        self._log("khai_bao", loai=loai, noi_dung=noi_dung)
        return _ok(f"Đã ghi nhận phần '{loai}'. Chưa có số liệu nào được cấp; hãy tiếp tục các bước còn lại.")

    def chon_dung_cu(self, ds: list[str]) -> dict:
        dc, canh_bao = self.bai["dung_cu"], []
        for k in ds:
            if k not in dc:
                return _tu_choi(f"'{k}' không có trong tủ dụng cụ.", tu_dung_cu=sorted(dc))
        for k in ds:
            if "ghi_chu_khi_chon" in dc[k]:
                canh_bao.append(f"{dc[k]['ten']}: {dc[k]['ghi_chu_khi_chon']}")
        self.dung_cu_chon = set(ds)
        thieu = [loai for loai, n in self.bai["dung_cu_can_co"].items()
                 if sum(1 for k in ds if dc[k]["loai"] == loai) < n]
        self._log("chon_dung_cu", ds=ds, thieu=thieu)
        if thieu:
            return _tu_choi("Bộ dụng cụ em chọn chưa đo được hết các đại lượng trong phương án của em.", loai_con_thieu=thieu, canh_bao=canh_bao)
        return _ok("Đã ghi nhận bộ dụng cụ.", canh_bao=canh_bao)

    def kiem_tra_lap_rap(self, buoc_da_lam: list[str]) -> dict:
        lr = self.bai["lap_rap"]
        hop_le = {b["id"] for b in lr["buoc"]}
        la = [b for b in buoc_da_lam if b not in hop_le]
        if la:
            return _tu_choi(f"Bước không hợp lệ: {la}.", cac_buoc=[b["id"] for b in lr["buoc"]])
        vi_tri = {b: i for i, b in enumerate(buoc_da_lam)}
        loi = []
        for truoc, sau in lr["thu_tu"]:
            if sau in vi_tri and (truoc not in vi_tri or vi_tri[truoc] > vi_tri[sau]):
                loi.append(f"Bước '{sau}' làm trước khi xong bước '{truoc}'.")
        thieu = [b for b in lr["bat_buoc"] if b not in vi_tri]
        self.buoc_lap_rap = list(buoc_da_lam)
        self._log("lap_rap", buoc=buoc_da_lam, loi=loi, thieu=thieu)
        if loi or thieu:
            return _tu_choi("Lắp ráp chưa đạt.", sai_thu_tu=loi, con_thieu=thieu, an_toan=self.bai["an_toan"])
        return _ok("Lắp ráp đạt.", an_toan=self.bai["an_toan"])

    # ---------------- điều kiện qua pha ----------------
    def _dieu_kien_pha(self) -> list[str]:
        return self.bai["pha"][self.pha]["dieu_kien"]

    def _dat(self, khoa: str) -> bool:
        if khoa == "cau_vao_dat":
            return len(self.cau_vao_dat) >= min(self.cfg["so_cau_vao_phai_dat"], len(self.bai["cau_vao"]))
        if khoa.startswith("khai_bao:"):
            return khoa.split(":")[1] in self.khai_bao
        if khoa == "dung_cu_da_chon":
            dc = self.bai["dung_cu"]
            return bool(self.dung_cu_chon) and all(
                any(dc[k]["loai"] == loai for k in self.dung_cu_chon) for loai in self.bai["dung_cu_can_co"])
        if khoa == "lap_rap_dat":
            return self.kiem_tra_lap_rap_im(self.buoc_lap_rap)
        if khoa == "do_du_lan":
            return all(self._du_lan(y) for y in self.bai["yeu_cau_do"])
        if khoa == "ket_qua_dat":
            return bool(self.ket_qua_dat) and self.ket_qua_dat >= set(self.bai["danh_gia_ket_qua"]["loai"])
        if khoa == "ket_luan_dat":
            return self.ket_luan_dat >= {k["id"] for k in self.bai["ket_luan"]}
        return False

    def kiem_tra_lap_rap_im(self, buoc: list[str]) -> bool:
        lr = self.bai["lap_rap"]
        vt = {b: i for i, b in enumerate(buoc)}
        return all(b in vt for b in lr["bat_buoc"]) and all(
            (s not in vt) or (t in vt and vt[t] < vt[s]) for t, s in lr["thu_tu"])

    def _dat_het_pha(self) -> bool:
        return all(self._dat(k) for k in self._dieu_kien_pha())

    def qua_pha(self) -> dict:
        thieu = [k for k in self._dieu_kien_pha() if not self._dat(k)]
        if thieu:
            return _tu_choi("Chưa thể sang pha tiếp theo.", con_thieu=thieu, pha_hien_tai=PHA[self.pha])
        if self.pha == len(PHA) - 1:
            return _ok("Em đã hoàn thành bài thực hành.", hoan_thanh=True)
        self.pha += 1
        self._log("qua_pha", pha_moi=PHA[self.pha])
        return _ok(f"Sang pha: {self.bai['pha'][self.pha]['ten']}.", pha=PHA[self.pha])

    # ---------------- pha 2: đo ----------------
    def _cong_do(self) -> dict | None:
        if self.pha < 2:
            return _tu_choi("Chưa đến bước đo. Hoàn thành pha trước rồi mới nhận số liệu.", pha_hien_tai=PHA[self.pha],
                            con_thieu=[k for k in self._dieu_kien_pha() if not self._dat(k)])
        if self.pha == 2 and not self._dat("lap_rap_dat"):
            return _tu_choi("Lắp ráp chưa đạt.")
        return None

    def _khoa_ch(self, cau: dict) -> dict:
        ks = getattr(self.mo_phong, "KHOA_CAU_HINH", KHOA_CU)
        return {k: v for k, v in cau.items() if k in ks}

    def _du_lieu_tot(self) -> list[dict]:
        return [d for d in self.du_lieu if d["gia_tri"] is not None and not d.get("loi_thao_tac")]

    def _lan_tiep(self, loai: str, khoa: str) -> int:
        return 1 + sum(1 for d in self.du_lieu if d["loai"] == loai and d["khoa"] == khoa)

    def tien_hanh_do(self, thi_nghiem: str, cau_hinh: dict) -> dict:
        t = self._cong_do()
        if t:
            self._log("do_bi_chan", thi_nghiem=thi_nghiem)
            return t
        dh = cau_hinh.get("dong_ho", getattr(self.mo_phong, "DONG_HO_MAC_DINH", "mc964"))
        if dh not in self.dung_cu_chon:
            return _tu_choi(f"Em chưa lấy '{dh}' ra khỏi tủ dụng cụ.", dung_cu_da_chon=sorted(self.dung_cu_chon))
        khoa = thi_nghiem + "|" + chuan_cau_hinh(self._khoa_ch(cau_hinh))
        lan = self._lan_tiep("thoi_gian", khoa)
        kq = self.mo_phong.do_thoi_gian(thi_nghiem, cau_hinh, lan)
        if kq["chan"]:
            self._log("do_chan_vat_ly", thi_nghiem=thi_nghiem, ly_do="; ".join(kq["chan"]))
            return _tu_choi("Không thể thực hiện phép đo này.", ly_do=kq["chan"], canh_bao=kq["canh_bao"])
        self.du_lieu.append({"loai": "thoi_gian", "khoa": khoa, "thi_nghiem": thi_nghiem, "cau_hinh": dict(cau_hinh),
                             "lan": lan, "gia_tri": kq["gia_tri"], "hien_thi": kq["hien_thi"], "don_vi": "s",
                             "loi_thao_tac": kq.get("loi_thao_tac", False)})
        self.canh_bao_da_gap += kq["canh_bao"]
        self._log("do_thoi_gian", thi_nghiem=thi_nghiem, lan=lan, hien_thi=kq["hien_thi"], canh_bao=len(kq["canh_bao"]))
        return _ok("Đã đo.", lan=lan, hien_thi=phay(kq["hien_thi"]), don_vi="s", canh_bao=kq["canh_bao"])

    def do_chieu_dai(self, thi_nghiem: str, muc: str, cau_hinh: dict, dung_cu: str) -> dict:
        t = self._cong_do()
        if t:
            return t
        if dung_cu not in self.dung_cu_chon:
            return _tu_choi(f"Em chưa lấy '{dung_cu}' ra khỏi tủ dụng cụ.", dung_cu_da_chon=sorted(self.dung_cu_chon))
        khoa = thi_nghiem + "|" + chuan_cau_hinh(self._khoa_ch(cau_hinh)) + "|" + muc
        lan = self._lan_tiep("do_dai", khoa)
        kq = self.mo_phong.do_chieu_dai(muc, cau_hinh, lan, dung_cu)
        if not kq["hop_le"]:
            return _tu_choi("Không thể thực hiện phép đo này.", ly_do=kq["chan"])
        self.du_lieu.append({"loai": "do_dai", "khoa": khoa, "thi_nghiem": thi_nghiem, "muc": muc, "cau_hinh": dict(cau_hinh),
                             "dung_cu": dung_cu, "lan": lan, "gia_tri": kq["gia_tri"], "hien_thi": kq["hien_thi"], "don_vi": kq.get("don_vi", "m")})
        self.canh_bao_da_gap += kq["canh_bao"]
        self._log("do_chieu_dai", muc=muc, lan=lan, dung_cu=dung_cu)
        return _ok("Đã đo.", lan=lan, hien_thi=phay(kq["hien_thi"]), don_vi=kq.get("don_vi", "m"), canh_bao=kq["canh_bao"])

    def _nhom(self, thi_nghiem: str) -> dict[str, dict]:
        nhom: dict[str, dict] = {}
        for d in self.du_lieu:
            if d["thi_nghiem"] != thi_nghiem or d["gia_tri"] is None or d.get("loi_thao_tac"):
                continue   # số liệu do thao tác sai được bỏ khỏi phần chấm
            g = nhom.setdefault(d["khoa"].split("|")[1], {"t": [], "x": {}})
            if d["loai"] == "thoi_gian":
                g["t"].append(d["gia_tri"])
            else:
                g["x"].setdefault(d["muc"], []).append(d["gia_tri"])
        return nhom

    def _du_lan(self, y: dict) -> bool:
        if hasattr(self.mo_phong, "du_lan"):
            return self.mo_phong.du_lan(y, self._du_lieu_tot())
        nhom = self._nhom(y["thi_nghiem"])
        dat = [g for g in nhom.values()
               if len(g["t"]) >= y["so_lan_t_toi_thieu"] and len(g["x"].get(y["do_dai"]["muc"], [])) >= y["do_dai"]["so_lan_toi_thieu"]]
        return len(dat) >= y["so_cau_hinh_toi_thieu"]

    def bang_so_lieu(self, danh_dau_loi: bool = False) -> str:
        """Bảng chuẩn (Markdown) toàn bộ số liệu đã cấp, nhóm theo thí nghiệm và cấu hình.
        danh_dau_loi=True (dùng cho báo cáo giáo viên): thêm dấu * sau lần đo do thao tác sai."""
        dong = ["| Thí nghiệm | Cấu hình | Đại lượng | Các lần đo |", "|---|---|---|---|"]
        gom: dict[tuple, list] = {}
        for d in self.du_lieu:
            cau = self._khoa_ch(d["cau_hinh"])
            dl = "t" if d["loai"] == "thoi_gian" else d["muc"]
            gia = phay(d["hien_thi"]) + ("*" if danh_dau_loi and d.get("loi_thao_tac") else "")
            gom.setdefault((d["thi_nghiem"], mo_ta_cau_hinh(cau), dl), []).append(gia)
        for (ten, cau, dl), ds in gom.items():
            dong.append(f"| {NHAN_THI_NGHIEM.get(ten, ten)} | {cau} | {NHAN_DAI_LUONG.get(dl, dl)} | {'; '.join(ds)} |")
        if danh_dau_loi:
            dong.append("\n(*) Lần đo do thao tác sai, bị loại khỏi phần chấm.")
        return "\n".join(dong)

    # ---------------- gợi ý và chống "làm hộ" ----------------
    def ghi_lan_thu(self, chu_de: str, noi_dung: str) -> dict:
        if len(noi_dung.split()) < 3:
            return _tu_choi("Hãy viết ít nhất một câu nêu cách em nghĩ.")
        self.so_lan_thu[chu_de] = self.so_lan_thu.get(chu_de, 0) + 1
        self._log("lan_thu", chu_de=chu_de, noi_dung=noi_dung)
        return _ok("Đã ghi nhận cách em nghĩ.")

    def xin_goi_y(self, chu_de: str) -> dict:
        ds = self.bai["goi_y"].get(chu_de)
        if ds is None:
            return _tu_choi("Chủ đề này chưa có gợi ý.", chu_de_co_goi_y=sorted(self.bai["goi_y"]))
        nac = self.muc_goi_y.get(chu_de, 0)
        if nac >= len(ds):
            return _tu_choi("Em đã dùng hết các nấc gợi ý của chủ đề này. Hãy thử trình bày hướng làm của em, hoặc hỏi thầy/cô.")
        can = self.cfg["so_lan_thu_truoc_goi_y"][nac]
        da = self.so_lan_thu.get(chu_de, 0)
        if da < can:
            self._log("goi_y_bi_tu_choi", chu_de=chu_de, nac=nac + 1)
            return _tu_choi(f"Trước khi gợi ý nấc {nac + 1}, em hãy tự đề xuất cách làm của mình (còn thiếu {can - da} lần thử).")
        self.muc_goi_y[chu_de] = nac + 1
        self._log("goi_y", chu_de=chu_de, nac=nac + 1)
        return _ok(ds[nac], nac=nac + 1, con_lai=len(ds) - nac - 1)

    def xin_dap_an(self, noi_dung: str = "") -> dict:
        self.so_lan_xin_dap_an += 1
        self._log("xin_dap_an", lan=self.so_lan_xin_dap_an, noi_dung=noi_dung)
        tb = "Thầy/cô không đưa đáp án hay số liệu trực tiếp. Em hãy nêu dự đoán hoặc cách làm của em, rồi mình cùng kiểm tra."
        if self.so_lan_xin_dap_an >= self.cfg["so_lan_xin_dap_an_goi_giao_vien"]:
            self.can_giao_vien = True
            tb += " Nếu em đang kẹt thật sự, hãy giơ tay hỏi giáo viên để được hỗ trợ trực tiếp."
        return _tu_choi(tb, can_giao_vien=self.can_giao_vien)

    # ---------------- pha 3: chấm kết quả và kết luận ----------------
    def _tinh_lai(self, loai: str):
        if hasattr(self.mo_phong, "tinh_lai"):
            return self.mo_phong.tinh_lai(loai, self._du_lieu_tot())
        if loai == "v_tb":
            g = list(self._nhom("toc_do_trung_binh").values())
            if not g or not g[0]["t"] or not g[0].get("x", {}).get("quang_duong"):
                return None
            return sai_so.trung_binh(g[0]["x"]["quang_duong"]) / sai_so.trung_binh(g[0]["t"])
        if loai == "v_tuc_thoi":
            g = list(self._nhom("toc_do_tuc_thoi").values())
            if not g or not g[0]["t"] or not g[0].get("x", {}).get("duong_kinh"):
                return None
            return sai_so.trung_binh(g[0]["x"]["duong_kinh"]) / sai_so.trung_binh(g[0]["t"])
        if loai == "g_tb":
            gs = [2 * sai_so.trung_binh(g["x"]["quang_duong"]) / sai_so.trung_binh(g["t"]) ** 2
                  for g in self._nhom("roi_tu_do").values() if g["t"] and g["x"].get("quang_duong")]
            return sai_so.trung_binh(gs) if gs else None
        return None

    def nop_ket_qua(self, loai: str, gia_tri: float) -> dict:
        if self.pha < 3:
            return _tu_choi("Chưa đến bước xử lí số liệu.", pha_hien_tai=PHA[self.pha])
        if loai not in self.bai["danh_gia_ket_qua"]["loai"]:
            return _tu_choi("Loại kết quả không hợp lệ.", loai_hop_le=self.bai["danh_gia_ket_qua"]["loai"])
        ref = self._tinh_lai(loai)
        if ref is None:
            return _tu_choi("Chưa đủ số liệu đã đo để kiểm tra kết quả này. Hãy đo bổ sung.")
        if isinstance(ref, list):        # nhiều cấu hình hợp lệ: so với giá trị gần nhất em đã có số liệu
            if not ref:
                return _tu_choi("Chưa đủ số liệu đã đo để kiểm tra kết quả này. Hãy đo bổ sung.")
            ref = min(ref, key=lambda r: abs(gia_tri - r))
        sai = abs(gia_tri - ref) / ref * 100
        dg = self.bai["danh_gia_ket_qua"]
        dat = sai <= dg.get("dung_sai_theo_loai", {}).get(loai, dg["dung_sai_phan_tram"])
        self._log("nop_ket_qua", loai=loai, gia_tri=gia_tri, dat=dat)
        if dat:
            self.ket_qua_dat.add(loai)
            return _ok("Kết quả khớp với số liệu em đã đo.")
        # không lộ giá trị đúng, chỉ gợi hướng kiểm tra
        return _tu_choi("Kết quả chưa khớp với chính số liệu em đã đo. Hãy kiểm tra lại: lấy trung bình trước hay sau khi chia, đơn vị (m, s), và số chữ số.",
                        huong="lon_hon" if gia_tri > ref else "nho_hon")

    def nop_ket_luan(self, noi_dung: str, y_dat: list[str] | None = None) -> dict:
        if self.pha < 3:
            return _tu_choi("Chưa đến bước kết luận.")
        nd = khong_dau(noi_dung)
        for y in self.bai["ket_luan"]:
            tot = (y["id"] in y_dat) if y_dat is not None else all(any(khong_dau(t) in nd for t in n) for n in y["nhom_tu_khoa"])
            if tot:
                self.ket_luan_dat.add(y["id"])
        thieu = [y for y in self.bai["ket_luan"] if y["id"] not in self.ket_luan_dat]
        self._log("nop_ket_luan", con_thieu=[y["id"] for y in thieu])
        if thieu:
            return _tu_choi("Kết luận của em còn thiếu ý. Hãy trả lời câu hỏi dẫn dắt sau.", cau_hoi_dan_dat=[y["cau_hoi_dan_dat"] for y in thieu][:1])
        return _ok("Kết luận đã đủ ý.", cau_hoi_phan_bien=self.bai["phan_bien"])

    def danh_muc(self, ma: str | None = None) -> dict:
        """[20/11] Danh mục thí nghiệm theo tài liệu tổng hợp: cái nào đã dựng, cái nào chưa. Không có ma -> liệt kê."""
        dm = json.loads((GOC / "bai_hoc" / "danh_muc.json").read_text(encoding="utf-8"))
        if ma is None:
            return _ok("Danh mục thí nghiệm.", che_do=dm["che_do"],
                       muc=[{k: m[k] for k in ("ma", "ten", "nhom", "trang_thai")} for m in dm["muc"]])
        m = next((x for x in dm["muc"] if x["ma"] == ma), None)
        return _ok("Chi tiết thí nghiệm.", muc=m) if m else _tu_choi(f"Không có thí nghiệm mã '{ma}'.", ma_hop_le=[x["ma"] for x in dm["muc"]])

    def gia_thiet_mo_hinh(self) -> dict:
        """[20/11] Giả thiết và giới hạn của mô hình (định tính, không lộ thông số thật). Quy tắc 'Tính minh bạch'."""
        self._log("gia_thiet")
        return _ok("Giả thiết và giới hạn của mô hình.", gia_thiet=self.bai.get("gia_thiet", []), gioi_han=self.bai.get("gioi_han_mo_hinh", []))

    def bao_cao(self) -> str:
        """Tóm tắt cho giáo viên: bảng số liệu, mức hoàn thành, chỗ kẹt (không chứa thông tin định danh)."""
        dong = [f"# Báo cáo phiên – {self.bai['ten_bai']} – mã {self.ma_hs}", "", f"Pha hiện tại: {self.bai['pha'][self.pha]['ten']} ({self.pha + 1}/4)", "",
                "## Số liệu đã cấp", self.bang_so_lieu(danh_dau_loi=True) if self.du_lieu else "(chưa có)", "",
                "## Kiểm soát chất lượng",
                f"- Số lần xin đáp án: {self.so_lan_xin_dap_an}" + (" → cần giáo viên hỗ trợ" if self.can_giao_vien else ""),
                f"- Nấc gợi ý đã dùng: {self.muc_goi_y or 'không'}",
                f"- Cảnh báo mô phỏng gặp phải: {len(self.canh_bao_da_gap)}",
                f"- Kết quả đạt: {sorted(self.ket_qua_dat) or 'chưa'}; ý kết luận đạt: {sorted(self.ket_luan_dat) or 'chưa'}"]
        return "\n".join(dong)
