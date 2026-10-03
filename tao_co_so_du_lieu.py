#!/usr/bin/env python3
"""
Script rieng le chi de tao/khoi tao co so du lieu (khong kiem tra Python,
thu vien hay model AI nhu `cai_dat.py`).

Chay bang lenh:
    python tao_co_so_du_lieu.py

Thuc hien:
    1. Kiem tra MySQL dang chay.
    2. Kiem tra database `diem_danh_khuon_mat` da ton tai chua.
    3. Neu chua, tao database moi.
    4. Tao toan bo bang (dung SQLAlchemy ORM, khong can chay tay schema.sql).
    5. Tao du lieu mau va tai khoan Admin mac dinh.

Dung khi ban chi muon (hoac can) tao lai database ma khong chay lai toan
bo quy trinh kiem tra moi truong cua cai_dat.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    from app.co_so_du_lieu.ket_noi import kiem_tra_ket_noi_mysql
    from app.co_so_du_lieu.khoi_tao import khoi_tao_toan_bo

    print("=" * 70)
    print("TẠO CƠ SỞ DỮ LIỆU — HỆ THỐNG ĐIỂM DANH SINH VIÊN BẰNG KHUÔN MẶT")
    print("=" * 70)

    thanh_cong, thong_bao = kiem_tra_ket_noi_mysql()
    print(f"\n[1/3] Kiểm tra kết nối MySQL: {'OK' if thanh_cong else 'THẤT BẠI'}")
    if not thanh_cong:
        print(f"\n{thong_bao}")
        return 1

    print("[2/3] Tạo database và toàn bộ bảng...")
    print("[3/3] Nạp dữ liệu mẫu...")
    ket_qua = khoi_tao_toan_bo(nap_mau=True)

    thanh_cong_toan_bo = True
    for thanh_cong_buoc, thong_bao_buoc in ket_qua:
        bieu_tuong = "✔" if thanh_cong_buoc else "✘"
        print(f"  [{bieu_tuong}] {thong_bao_buoc}")
        if not thanh_cong_buoc:
            thanh_cong_toan_bo = False

    if thanh_cong_toan_bo:
        print("\n🎉 Đã tạo cơ sở dữ liệu thành công! Chạy 'python run.py' để bắt đầu sử dụng.")
        return 0

    print("\n⚠ Có lỗi xảy ra trong quá trình tạo cơ sở dữ liệu. Xem chi tiết ở trên.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
