#!/usr/bin/env python3
"""
Diem vao chinh cua ung dung.

Chay bang lenh:
    python run.py

Truoc khi mo giao dien dang nhap, chuong trinh se kiem tra ket noi
MySQL/MariaDB (XAMPP). Neu chua san sang, chuong trinh se hien thong
bao huong dan chi tiet thay vi bi crash.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import QApplication, QMessageBox

from app.cau_hinh.cai_dat import lay_cau_hinh
from app.co_so_du_lieu.ket_noi import (
    kiem_tra_cac_bang_can_thiet,
    kiem_tra_database_ton_tai,
    kiem_tra_ket_noi_mysql,
)


def _cau_hinh_ghi_log() -> None:
    """Thiet lap logging ghi ra file trong thu muc nhat_ky/ va ra man hinh console."""
    cau_hinh = lay_cau_hinh()
    thu_muc_nhat_ky = cau_hinh.duong_dan_tuyet_doi(cau_hinh.ung_dung.thu_muc_nhat_ky)
    thu_muc_nhat_ky.mkdir(parents=True, exist_ok=True)
    duong_dan_file_log = thu_muc_nhat_ky / "ung_dung.log"

    logging.basicConfig(
        level=getattr(logging, cau_hinh.ung_dung.muc_ghi_log.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(duong_dan_file_log, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def _nap_stylesheet(ung_dung: QApplication) -> None:
    """Nap file QSS tao giao dien dep, bo qua neu khong tim thay file."""
    cau_hinh = lay_cau_hinh()
    duong_dan_qss = cau_hinh.thu_muc_goc / "app" / "tai_nguyen" / "giao_dien" / "style.qss"
    if duong_dan_qss.exists():
        ung_dung.setStyleSheet(duong_dan_qss.read_text(encoding="utf-8"))


def _kiem_tra_san_sang_co_so_du_lieu() -> tuple[bool, str]:
    """Kiem tra tuan tu: MySQL dang chay -> database ton tai -> du bang.

    Tra ve (True, "") neu moi thu san sang, hoac (False, thong_bao_loi) de
    hien thi cho nguoi dung, KHONG lam ung dung crash.
    """
    thanh_cong, thong_bao = kiem_tra_ket_noi_mysql()
    if not thanh_cong:
        return False, thong_bao

    thanh_cong, thong_bao = kiem_tra_database_ton_tai()
    if not thanh_cong:
        return False, (
            f"{thong_bao}\n\n"
            "Vui long chay 'python cai_dat.py' de tu dong tao database, "
            "hoac import thu cong file database/schema.sql bang phpMyAdmin."
        )

    thanh_cong, thong_bao, _ = kiem_tra_cac_bang_can_thiet()
    if not thanh_cong:
        return False, (
            f"{thong_bao}\n\n"
            "Vui long chay 'python cai_dat.py' de tu dong tao cac bang con thieu."
        )

    return True, "Da ket noi co so du lieu."


def main() -> int:
    _cau_hinh_ghi_log()
    bo_ghi_log = logging.getLogger(__name__)
    bo_ghi_log.info("Khoi dong ung dung.")

    ung_dung_qt = QApplication(sys.argv)
    ung_dung_qt.setApplicationName(lay_cau_hinh().ung_dung.ten_ung_dung)
    _nap_stylesheet(ung_dung_qt)

    san_sang, thong_bao = _kiem_tra_san_sang_co_so_du_lieu()
    if not san_sang:
        bo_ghi_log.error("Co so du lieu chua san sang: %s", thong_bao)
        QMessageBox.critical(None, "Không thể kết nối cơ sở dữ liệu", thong_bao)
        return 1

    from app.giao_dien.dang_nhap import ManHinhDangNhap

    cac_cua_so_dang_mo = []  # giu tham chieu de tranh bi garbage-collected

    man_hinh_dang_nhap = ManHinhDangNhap()

    def _khi_dang_nhap_thanh_cong(phien_dang_nhap) -> None:
        from app.giao_dien.cua_so_chinh import CuaSoChinh

        cua_so_chinh = CuaSoChinh(phien_dang_nhap)
        cua_so_chinh.show()
        cac_cua_so_dang_mo.append(cua_so_chinh)
        man_hinh_dang_nhap.close()

    man_hinh_dang_nhap.dang_nhap_thanh_cong.connect(_khi_dang_nhap_thanh_cong)
    man_hinh_dang_nhap.show()

    return ung_dung_qt.exec()


if __name__ == "__main__":
    sys.exit(main())
