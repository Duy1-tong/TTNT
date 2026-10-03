#!/usr/bin/env python3
"""
Script cai dat / khoi tao he thong.

Chay bang lenh:
    python cai_dat.py

Thuc hien tuan tu:
    1. Kiem tra phien ban Python.
    2. Kiem tra cac thu vien Python bat buoc va tuy chon (AI).
    3. Kiem tra XAMPP/MySQL dang chay.
    4. Kiem tra/tao database `diem_danh_khuon_mat`.
    5. Tao toan bo bang du lieu.
    6. Nap du lieu mau (tai khoan Admin/Giang vien/Sinh vien mau).
    7. Kiem tra model AI (co fallback neu thieu).
    8. Bao cao ket qua tong hop.

Script nay AN TOAN de chay nhieu lan (idempotent): neu database/bang da
ton tai, no se bo qua thay vi bao loi.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SO_KY_TU_KHUNG = 70


def _in_tieu_de(tieu_de: str) -> None:
    print("\n" + "=" * SO_KY_TU_KHUNG)
    print(tieu_de)
    print("=" * SO_KY_TU_KHUNG)


def _in_dong(nhan: str, ket_qua_ok: bool, chi_tiet: str = "") -> None:
    bieu_tuong = "✔" if ket_qua_ok else "✘"
    print(f"  [{bieu_tuong}] {nhan}")
    if chi_tiet:
        for dong in chi_tiet.strip().splitlines():
            print(f"        {dong}")


def buoc_1_kiem_tra_python() -> bool:
    _in_tieu_de("BƯỚC 1/8 — KIỂM TRA PHIÊN BẢN PYTHON")
    phien_ban = sys.version_info
    hop_le = phien_ban.major == 3 and phien_ban.minor in (11, 12, 13)
    _in_dong(
        f"Python {phien_ban.major}.{phien_ban.minor}.{phien_ban.micro}",
        hop_le,
        "" if hop_le else "Khuyến nghị dùng Python 3.11 hoặc 3.12 để tương thích tốt nhất.",
    )
    return True  # Khong chan cai dat, chi canh bao.


def buoc_2_kiem_tra_thu_vien() -> bool:
    _in_tieu_de("BƯỚC 2/8 — KIỂM TRA THƯ VIỆN PYTHON")

    thu_vien_bat_buoc = {
        "PySide6": "PySide6",
        "cv2": "opencv-python",
        "numpy": "numpy",
        "sqlalchemy": "SQLAlchemy",
        "pymysql": "PyMySQL",
        "bcrypt": "bcrypt",
        "dotenv": "python-dotenv",
        "openpyxl": "openpyxl",
        "reportlab": "reportlab",
        "matplotlib": "matplotlib",
        "PIL": "Pillow",
    }
    thu_vien_ai_tuy_chon = {
        "ultralytics": "ultralytics (YOLO)",
        "insightface": "insightface",
        "onnxruntime": "onnxruntime",
    }

    tat_ca_bat_buoc_du = True
    for module_name, ten_hien_thi in thu_vien_bat_buoc.items():
        co_san = importlib.util.find_spec(module_name) is not None
        _in_dong(ten_hien_thi, co_san)
        if not co_san:
            tat_ca_bat_buoc_du = False

    print()
    print("  Thư viện AI nâng cao (tùy chọn — hệ thống tự dùng OpenCV dự phòng nếu thiếu):")
    for module_name, ten_hien_thi in thu_vien_ai_tuy_chon.items():
        co_san = importlib.util.find_spec(module_name) is not None
        _in_dong(ten_hien_thi, co_san)

    if not tat_ca_bat_buoc_du:
        print(
            "\n  ⚠ Một số thư viện bắt buộc còn thiếu. Vui lòng chạy:\n"
            "      pip install -r requirements.txt"
        )
    return tat_ca_bat_buoc_du


def buoc_3_kiem_tra_mysql() -> bool:
    _in_tieu_de("BƯỚC 3/8 — KIỂM TRA XAMPP / MYSQL")
    from app.co_so_du_lieu.ket_noi import kiem_tra_ket_noi_mysql

    thanh_cong, thong_bao = kiem_tra_ket_noi_mysql()
    _in_dong("Kết nối tới MySQL/MariaDB (localhost:3306)", thanh_cong, thong_bao)
    if not thanh_cong:
        print(
            "\n  Vui lòng:\n"
            "  1. Mở XAMPP Control Panel.\n"
            "  2. Nhấn Start tại MySQL.\n"
            "  3. Kiểm tra cổng 3306.\n"
            "  4. Chạy lại: python cai_dat.py\n"
        )
    return thanh_cong


def buoc_4_5_6_khoi_tao_database() -> bool:
    _in_tieu_de("BƯỚC 4-6/8 — TẠO DATABASE, BẢNG VÀ DỮ LIỆU MẪU")
    from app.co_so_du_lieu.khoi_tao import khoi_tao_toan_bo

    ten_buoc = [
        "Kiểm tra / tạo database 'diem_danh_khuon_mat'",
        "Tạo toàn bộ bảng dữ liệu",
        "Nạp dữ liệu mẫu (tài khoản Admin/Giảng viên/Sinh viên mẫu)",
    ]
    ket_qua = khoi_tao_toan_bo(nap_mau=True)
    tat_ca_thanh_cong = True
    for chi_so, (thanh_cong, thong_bao) in enumerate(ket_qua):
        nhan = ten_buoc[chi_so] if chi_so < len(ten_buoc) else f"Bước {chi_so + 1}"
        _in_dong(nhan, thanh_cong, thong_bao)
        if not thanh_cong:
            tat_ca_thanh_cong = False
            break
    return tat_ca_thanh_cong


def buoc_7_kiem_tra_model_ai() -> bool:
    _in_tieu_de("BƯỚC 7/8 — KIỂM TRA MODEL AI")
    from app.tri_tue_nhan_tao.phat_hien_khuon_mat import BoPhatHienKhuonMat
    from app.tri_tue_nhan_tao.tao_embedding import BoTaoEmbedding

    bo_phat_hien = BoPhatHienKhuonMat()
    _in_dong(
        f"Phương pháp phát hiện khuôn mặt: {bo_phat_hien.ten_phuong_phap_dang_dung}", True
    )
    bo_embedding = BoTaoEmbedding()
    _in_dong(
        f"Mô hình trích xuất đặc trưng: {bo_embedding.ten_mo_hinh} "
        f"(phiên bản {bo_embedding.phien_ban_mo_hinh})",
        True,
    )
    if bo_embedding.ten_mo_hinh == "opencv_fallback":
        print(
            "\n  ⚠ Hệ thống đang dùng phương pháp AI dự phòng (OpenCV) vì chưa cài\n"
            "    được insightface/onnxruntime. Chương trình vẫn hoạt động đầy đủ,\n"
            "    nhưng để có độ chính xác nhận diện cao nhất, khuyến nghị cài thêm:\n"
            "      pip install insightface onnxruntime ultralytics\n"
        )
    return True


def buoc_8_tong_ket(cac_ket_qua: dict[str, bool]) -> None:
    _in_tieu_de("BƯỚC 8/8 — TỔNG KẾT")
    for nhan, ok in cac_ket_qua.items():
        _in_dong(nhan, ok)

    if all(cac_ket_qua.values()):
        print(
            "\n🎉 CÀI ĐẶT HOÀN TẤT! Hệ thống đã sẵn sàng.\n\n"
            "Chạy chương trình bằng lệnh:\n"
            "    python run.py\n\n"
            "Tài khoản đăng nhập mẫu:\n"
            "    admin / Admin@123\n"
            "    giangvien01 / GiangVien@123\n"
            "    sinhvien01 / SinhVien@123\n"
        )
    else:
        print(
            "\n⚠ CÀI ĐẶT CHƯA HOÀN TẤT. Vui lòng khắc phục các mục có dấu ✘ ở trên,\n"
            "  sau đó chạy lại: python cai_dat.py\n"
        )


def main() -> int:
    print("╔" + "═" * (SO_KY_TU_KHUNG - 2) + "╗")
    print("  CÀI ĐẶT HỆ THỐNG ĐIỂM DANH SINH VIÊN BẰNG KHUÔN MẶT".center(SO_KY_TU_KHUNG))
    print("╚" + "═" * (SO_KY_TU_KHUNG - 2) + "╝")

    cac_ket_qua: dict[str, bool] = {}

    cac_ket_qua["Phiên bản Python"] = buoc_1_kiem_tra_python()
    cac_ket_qua["Thư viện Python bắt buộc"] = buoc_2_kiem_tra_thu_vien()

    if not cac_ket_qua["Thư viện Python bắt buộc"]:
        buoc_8_tong_ket(cac_ket_qua)
        return 1

    cac_ket_qua["Kết nối MySQL/MariaDB (XAMPP)"] = buoc_3_kiem_tra_mysql()
    if not cac_ket_qua["Kết nối MySQL/MariaDB (XAMPP)"]:
        buoc_8_tong_ket(cac_ket_qua)
        return 1

    cac_ket_qua["Khởi tạo database / bảng / dữ liệu mẫu"] = buoc_4_5_6_khoi_tao_database()
    cac_ket_qua["Model AI"] = buoc_7_kiem_tra_model_ai()

    buoc_8_tong_ket(cac_ket_qua)
    return 0 if all(cac_ket_qua.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
