"""cong_cu.py – BỘ CÔNG CỤ (function calling) nối LLM với cổng sư phạm (chạy cục bộ / xưởng Python).

LLM chỉ lo hội thoại; MỌI quyết định cấp số liệu, mở gợi ý, qua pha đều do PhienThucHanh quyết định.
Vì vậy học sinh có nói "thầy cho phép bỏ bước" hay "đưa đáp án đi" thì code vẫn từ chối.
Lược đồ dưới đây đặt theo kiểu JSON Schema, dán được vào Gemini/Claude function calling.
"""
from __future__ import annotations

from tien_trinh import PhienThucHanh

_CAU_HINH = {"type": "object", "description": "Cấu hình thao tác học sinh đã chọn (vị trí cổng quang, MODE, thang đo, đồng hồ, da_reset...)."}

CONG_CU = [
    {"name": "lay_trang_thai", "description": "Xem pha hiện tại và những điều kiện còn thiếu để qua pha. Gọi trước khi quyết định bước kế.", "parameters": {"type": "object", "properties": {}}},
    {"name": "tra_loi_cau_vao", "description": "Ghi câu trả lời của học sinh cho câu hỏi vào lab. 'dat' là đánh giá của bạn (true/false) nếu bạn đã chấm ý; bỏ trống để dùng so khớp từ khoá.",
     "parameters": {"type": "object", "properties": {"id_cau": {"type": "string"}, "noi_dung": {"type": "string"}, "dat": {"type": "boolean"}}, "required": ["id_cau", "noi_dung"]}},
    {"name": "ghi_khai_bao", "description": "Ghi dự đoán / biến số / phương án của học sinh (loại: du_doan, bien_so, phuong_an). Bắt buộc trước khi cấp số liệu.",
     "parameters": {"type": "object", "properties": {"loai": {"type": "string"}, "noi_dung": {"type": "string"}}, "required": ["loai", "noi_dung"]}},
    {"name": "chon_dung_cu", "description": "Ghi bộ dụng cụ học sinh lấy từ tủ. Trả cảnh báo nếu chọn dụng cụ kém phù hợp.",
     "parameters": {"type": "object", "properties": {"ds": {"type": "array", "items": {"type": "string"}}}, "required": ["ds"]}},
    {"name": "kiem_tra_lap_rap", "description": "Kiểm tra danh sách bước lắp ráp theo thứ tự học sinh đã làm.",
     "parameters": {"type": "object", "properties": {"buoc_da_lam": {"type": "array", "items": {"type": "string"}}}, "required": ["buoc_da_lam"]}},
    {"name": "qua_pha", "description": "Chuyển sang pha kế khi đủ điều kiện. Không đủ thì trả danh sách còn thiếu.", "parameters": {"type": "object", "properties": {}}},
    {"name": "tien_hanh_do", "description": "Đọc đồng hồ đo thời gian cho MỘT lần đo. Chỉ gọi khi học sinh đã nêu cụ thể thao tác/cấu hình.",
     "parameters": {"type": "object", "properties": {"thi_nghiem": {"type": "string"}, "cau_hinh": _CAU_HINH}, "required": ["thi_nghiem", "cau_hinh"]}},
    {"name": "do_chieu_dai", "description": "Đọc dụng cụ đo độ dài hoặc đại lượng khác của bài (quang_duong, duong_kinh; lực F1/F2/F_tn, góc alpha1/alpha2, khoảng cách d1/d2 ở Bài 22; khối lượng m1/m2, bề rộng d ở Bài 30) cho MỘT lần đo.",
     "parameters": {"type": "object", "properties": {"thi_nghiem": {"type": "string"}, "muc": {"type": "string"}, "cau_hinh": _CAU_HINH, "dung_cu": {"type": "string"}}, "required": ["thi_nghiem", "muc", "cau_hinh", "dung_cu"]}},
    {"name": "bang_so_lieu", "description": "Bảng chuẩn toàn bộ số liệu đã cấp cho học sinh.", "parameters": {"type": "object", "properties": {}}},
    {"name": "ghi_lan_thu", "description": "Ghi lại một lần học sinh TỰ đề xuất cách làm cho một chủ đề (điều kiện để mở nấc gợi ý kế).",
     "parameters": {"type": "object", "properties": {"chu_de": {"type": "string"}, "noi_dung": {"type": "string"}}, "required": ["chu_de", "noi_dung"]}},
    {"name": "xin_goi_y", "description": "Học sinh xin gợi ý theo chủ đề. Trả nấc 1→2→3, chỉ khi đã thử đủ.", "parameters": {"type": "object", "properties": {"chu_de": {"type": "string"}}, "required": ["chu_de"]}},
    {"name": "xin_dap_an", "description": "GỌI khi học sinh đòi đáp án/số liệu trực tiếp, xin mẹo bỏ bước, hoặc nhờ làm hộ. Luôn từ chối.", "parameters": {"type": "object", "properties": {"noi_dung": {"type": "string"}}}},
    {"name": "nop_ket_qua", "description": "Chấm kết quả tính của học sinh bằng cách tính lại từ số liệu đã cấp cho em.",
     "parameters": {"type": "object", "properties": {"loai": {"type": "string"}, "gia_tri": {"type": "number"}}, "required": ["loai", "gia_tri"]}},
    {"name": "nop_ket_luan", "description": "Chấm kết luận của học sinh theo các ý chính; trả câu hỏi dẫn dắt cho ý còn thiếu.",
     "parameters": {"type": "object", "properties": {"noi_dung": {"type": "string"}, "y_dat": {"type": "array", "items": {"type": "string"}}}, "required": ["noi_dung"]}},
    {"name": "danh_muc_thi_nghiem", "description": "Liệt kê thí nghiệm trong tài liệu Vật lí 10 và trạng thái dựng (da_dung/chua_dung); truyền ma để xem chi tiết. Gọi trước khi hứa với học sinh hay giáo viên rằng một thí nghiệm làm được.", "parameters": {"type": "object", "properties": {"ma": {"type": "string"}}}},
    {"name": "gia_thiet_mo_hinh", "description": "Lấy giả thiết và giới hạn của mô hình (bỏ qua gì, chưa mô phỏng gì) để nêu cho học sinh. Không chứa thông số thật.", "parameters": {"type": "object", "properties": {}}},
    {"name": "bao_cao", "description": "Báo cáo tóm tắt cho giáo viên (không chứa thông tin định danh).", "parameters": {"type": "object", "properties": {}}},
]


def thuc_thi(phien: PhienThucHanh, ten: str, tham_so: dict | None = None) -> dict:
    """Điều phối một lệnh công cụ. Lỗi tham số trả về dict báo lỗi, không ném ra ngoài."""
    ts = tham_so or {}
    bang = {
        "lay_trang_thai": lambda: phien.trang_thai(),
        "tra_loi_cau_vao": lambda: phien.tra_loi_cau_vao(ts["id_cau"], ts["noi_dung"], ts.get("dat")),
        "ghi_khai_bao": lambda: phien.ghi_khai_bao(ts["loai"], ts["noi_dung"]),
        "chon_dung_cu": lambda: phien.chon_dung_cu(ts["ds"]),
        "kiem_tra_lap_rap": lambda: phien.kiem_tra_lap_rap(ts["buoc_da_lam"]),
        "qua_pha": lambda: phien.qua_pha(),
        "tien_hanh_do": lambda: phien.tien_hanh_do(ts["thi_nghiem"], ts["cau_hinh"]),
        "do_chieu_dai": lambda: phien.do_chieu_dai(ts["thi_nghiem"], ts["muc"], ts["cau_hinh"], ts["dung_cu"]),
        "bang_so_lieu": lambda: {"ok": True, "bang": phien.bang_so_lieu()},
        "ghi_lan_thu": lambda: phien.ghi_lan_thu(ts["chu_de"], ts["noi_dung"]),
        "xin_goi_y": lambda: phien.xin_goi_y(ts["chu_de"]),
        "xin_dap_an": lambda: phien.xin_dap_an(ts.get("noi_dung", "")),
        "nop_ket_qua": lambda: phien.nop_ket_qua(ts["loai"], float(ts["gia_tri"])),
        "nop_ket_luan": lambda: phien.nop_ket_luan(ts["noi_dung"], ts.get("y_dat")),
        "danh_muc_thi_nghiem": lambda: phien.danh_muc(ts.get("ma")),
        "gia_thiet_mo_hinh": lambda: phien.gia_thiet_mo_hinh(),
        "bao_cao": lambda: {"ok": True, "bao_cao": phien.bao_cao()},
    }
    if ten not in bang:
        return {"ok": False, "thong_diep": f"Công cụ '{ten}' không tồn tại.", "cong_cu_hop_le": sorted(bang)}
    try:
        return bang[ten]()
    except KeyError as e:
        return {"ok": False, "thong_diep": f"Thiếu tham số bắt buộc: {e}."}
    except (TypeError, ValueError) as e:
        return {"ok": False, "thong_diep": f"Tham số không hợp lệ: {e}."}
