"""
Module quan ly ket noi toi MySQL/MariaDB (XAMPP) thong qua SQLAlchemy + PyMySQL.

Kien truc: PySide6 -> Service -> SQLAlchemy ORM -> PyMySQL -> MySQL/MariaDB (XAMPP)
Khong co giao dien nao duoc phep ket noi truc tiep toi database.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.cau_hinh.cai_dat import lay_cau_hinh

_bo_ghi_log = logging.getLogger(__name__)

_dong_co: Engine | None = None
_lop_tao_phien: sessionmaker | None = None


class LoiKetNoiCoSoDuLieu(Exception):
    """Ngoai le tuy chinh, phat sinh khi khong the ket noi toi MySQL/MariaDB."""


def lay_dong_co(buoc_lai: bool = False) -> Engine:
    """Tra ve (hoac tao moi) SQLAlchemy Engine dung chung cho toan ung dung."""
    global _dong_co
    if _dong_co is None or buoc_lai:
        cau_hinh = lay_cau_hinh().co_so_du_lieu
        _dong_co = create_engine(
            cau_hinh.chuoi_ket_noi,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            future=True,
        )
    return _dong_co


def lay_lop_tao_phien() -> sessionmaker:
    """Tra ve (hoac tao moi) sessionmaker dung chung cho toan ung dung."""
    global _lop_tao_phien
    if _lop_tao_phien is None:
        _lop_tao_phien = sessionmaker(
            bind=lay_dong_co(), autoflush=False, autocommit=False, expire_on_commit=False
        )
    return _lop_tao_phien


@contextmanager
def mo_phien_lam_viec() -> Generator[Session, None, None]:
    """Context manager tao mot phien lam viec (Session) va tu dong dong lai.

    Vi du su dung:
        with mo_phien_lam_viec() as phien:
            phien.add(doi_tuong)
            phien.commit()
    """
    lop_tao = lay_lop_tao_phien()
    phien = lop_tao()
    try:
        yield phien
    except SQLAlchemyError:
        phien.rollback()
        raise
    finally:
        phien.close()


def kiem_tra_ket_noi_mysql() -> tuple[bool, str]:
    """Kiem tra MySQL/MariaDB (XAMPP) co dang chay va co the ket noi hay khong.

    Tra ve (True, thong_bao) neu thanh cong, (False, thong_bao_loi) neu that bai.
    Ham nay KHONG lam ung dung crash trong bat ky truong hop nao.
    """
    cau_hinh = lay_cau_hinh().co_so_du_lieu
    try:
        dong_co_kiem_tra = create_engine(
            cau_hinh.chuoi_ket_noi_khong_co_database,
            connect_args={"connect_timeout": 5},
            future=True,
        )
        with dong_co_kiem_tra.connect() as ket_noi:
            ket_noi.execute(text("SELECT 1"))
        dong_co_kiem_tra.dispose()
        return True, "Da ket noi toi may chu MySQL/MariaDB thanh cong."
    except OperationalError as loi:
        thong_bao = (
            "Khong the ket noi den MySQL.\n\n"
            "Vui long:\n"
            "1. Mo XAMPP Control Panel.\n"
            "2. Nhan Start tai MySQL.\n"
            "3. Kiem tra cong 3306.\n"
            "4. Chay lai chuong trinh.\n\n"
            f"Chi tiet loi ky thuat: {loi}"
        )
        _bo_ghi_log.error("Khong the ket noi MySQL: %s", loi)
        return False, thong_bao
    except Exception as loi:  # noqa: BLE001 - can bat moi loi ket noi khong luong truoc
        thong_bao = f"Loi khong xac dinh khi ket noi MySQL: {loi}"
        _bo_ghi_log.error(thong_bao)
        return False, thong_bao


def kiem_tra_database_ton_tai() -> tuple[bool, str]:
    """Kiem tra database `diem_danh_khuon_mat` da ton tai tren MySQL hay chua."""
    cau_hinh = lay_cau_hinh().co_so_du_lieu
    thanh_cong, thong_bao = kiem_tra_ket_noi_mysql()
    if not thanh_cong:
        return False, thong_bao
    try:
        dong_co_kiem_tra = create_engine(
            cau_hinh.chuoi_ket_noi_khong_co_database,
            connect_args={"connect_timeout": 5},
            future=True,
        )
        with dong_co_kiem_tra.connect() as ket_noi:
            ket_qua = ket_noi.execute(
                text("SHOW DATABASES LIKE :ten_db"), {"ten_db": cau_hinh.ten_co_so_du_lieu}
            )
            ton_tai = ket_qua.first() is not None
        dong_co_kiem_tra.dispose()
        if ton_tai:
            return True, f"Database '{cau_hinh.ten_co_so_du_lieu}' da ton tai."
        return False, f"Database '{cau_hinh.ten_co_so_du_lieu}' chua ton tai."
    except Exception as loi:  # noqa: BLE001
        return False, f"Loi khi kiem tra database: {loi}"


def kiem_tra_cac_bang_can_thiet() -> tuple[bool, str, list[str]]:
    """Kiem tra cac bang bat buoc da duoc tao trong database hay chua."""
    cac_bang_can_thiet = [
        "nguoi_dung",
        "sinh_vien",
        "giang_vien",
        "khoa",
        "lop_hoc",
        "mon_hoc",
        "lop_mon_hoc",
        "sinh_vien_lop",
        "buoi_hoc",
        "diem_danh",
        "khuon_mat",
        "camera",
        "nhat_ky_he_thong",
        "cau_hinh",
    ]
    try:
        dong_co = lay_dong_co(buoc_lai=True)
        with dong_co.connect() as ket_noi:
            ket_qua = ket_noi.execute(text("SHOW TABLES"))
            cac_bang_hien_co = {hang[0] for hang in ket_qua}
        cac_bang_thieu = [ten for ten in cac_bang_can_thiet if ten not in cac_bang_hien_co]
        if cac_bang_thieu:
            return (
                False,
                f"Con thieu {len(cac_bang_thieu)} bang: {', '.join(cac_bang_thieu)}",
                cac_bang_thieu,
            )
        return True, "Da co du toan bo bang can thiet.", []
    except Exception as loi:  # noqa: BLE001
        return False, f"Loi khi kiem tra danh sach bang: {loi}", cac_bang_can_thiet
