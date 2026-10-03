"""
Module doc cau hinh he thong tu file .env.

Toan bo thong tin nhay cam (tai khoan MySQL, khoa bi mat...) deu duoc
doc tu bien moi truong / file .env, KHONG hard-code trong source code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

THU_MUC_GOC = Path(__file__).resolve().parent.parent.parent
DUONG_DAN_FILE_ENV = THU_MUC_GOC / ".env"

# Nap file .env neu ton tai. Neu chua co .env, ung dung van chay duoc
# voi gia tri mac dinh (chi danh cho moi truong phat trien/thu nghiem).
if DUONG_DAN_FILE_ENV.exists():
    load_dotenv(dotenv_path=DUONG_DAN_FILE_ENV)
else:
    load_dotenv()


def _doc_bien_moi_truong_int(ten_bien: str, gia_tri_mac_dinh: int) -> int:
    """Doc bien moi truong dang so nguyen, tra ve mac dinh neu loi."""
    gia_tri_chuoi = os.getenv(ten_bien)
    if gia_tri_chuoi is None or gia_tri_chuoi.strip() == "":
        return gia_tri_mac_dinh
    try:
        return int(gia_tri_chuoi)
    except ValueError:
        return gia_tri_mac_dinh


def _doc_bien_moi_truong_float(ten_bien: str, gia_tri_mac_dinh: float) -> float:
    """Doc bien moi truong dang so thuc, tra ve mac dinh neu loi."""
    gia_tri_chuoi = os.getenv(ten_bien)
    if gia_tri_chuoi is None or gia_tri_chuoi.strip() == "":
        return gia_tri_mac_dinh
    try:
        return float(gia_tri_chuoi)
    except ValueError:
        return gia_tri_mac_dinh


@dataclass(frozen=True)
class CauHinhCoSoDuLieu:
    """Thong tin ket noi den MySQL/MariaDB chay qua XAMPP."""

    may_chu: str = field(default_factory=lambda: os.getenv("DB_HOST", "127.0.0.1"))
    cong: int = field(default_factory=lambda: _doc_bien_moi_truong_int("DB_PORT", 3306))
    ten_co_so_du_lieu: str = field(
        default_factory=lambda: os.getenv("DB_NAME", "diem_danh_khuon_mat")
    )
    tai_khoan: str = field(default_factory=lambda: os.getenv("DB_USER", "root"))
    mat_khau: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    @property
    def chuoi_ket_noi(self) -> str:
        """Tra ve SQLAlchemy connection string cho PyMySQL."""
        mat_khau_ma_hoa_url = self.mat_khau.replace("@", "%40") if self.mat_khau else ""
        return (
            f"mysql+pymysql://{self.tai_khoan}:{mat_khau_ma_hoa_url}"
            f"@{self.may_chu}:{self.cong}/{self.ten_co_so_du_lieu}?charset=utf8mb4"
        )

    @property
    def chuoi_ket_noi_khong_co_database(self) -> str:
        """Chuoi ket noi toi server MySQL nhung chua chi dinh database cu the.

        Dung khi can kiem tra/tao database lan dau.
        """
        mat_khau_ma_hoa_url = self.mat_khau.replace("@", "%40") if self.mat_khau else ""
        return (
            f"mysql+pymysql://{self.tai_khoan}:{mat_khau_ma_hoa_url}"
            f"@{self.may_chu}:{self.cong}/?charset=utf8mb4"
        )


@dataclass(frozen=True)
class CauHinhBaoMat:
    """Cau hinh lien quan den bao mat: bam mat khau, khoa tai khoan..."""

    so_lan_dang_nhap_sai_toi_da: int = field(
        default_factory=lambda: _doc_bien_moi_truong_int("SO_LAN_DANG_NHAP_SAI_TOI_DA", 5)
    )
    thoi_gian_khoa_tai_khoan_phut: int = field(
        default_factory=lambda: _doc_bien_moi_truong_int("THOI_GIAN_KHOA_TAI_KHOAN_PHUT", 15)
    )
    khoa_bi_mat_embedding: str = field(
        default_factory=lambda: os.getenv("KHOA_BI_MAT_EMBEDDING", "")
    )


@dataclass(frozen=True)
class CauHinhAI:
    """Cau hinh cho phan nhan dien khuon mat bang AI."""

    nguong_do_tuong_dong: float = field(
        default_factory=lambda: _doc_bien_moi_truong_float("NGUONG_DO_TUONG_DONG", 0.45)
    )
    thu_muc_model: str = field(
        default_factory=lambda: os.getenv("THU_MUC_MODEL", "app/tai_nguyen/model")
    )
    chi_so_camera_mac_dinh: int = field(
        default_factory=lambda: _doc_bien_moi_truong_int("CHI_SO_CAMERA_MAC_DINH", 0)
    )


@dataclass(frozen=True)
class CauHinhUngDung:
    """Cau hinh chung cua ung dung."""

    ten_ung_dung: str = field(
        default_factory=lambda: os.getenv(
            "TEN_UNG_DUNG", "He Thong Diem Danh Sinh Vien Bang Khuon Mat"
        )
    )
    muc_ghi_log: str = field(default_factory=lambda: os.getenv("MUC_GHI_LOG", "INFO"))
    thu_muc_nhat_ky: str = field(default_factory=lambda: os.getenv("THU_MUC_NHAT_KY", "nhat_ky"))
    thu_muc_bao_cao: str = field(default_factory=lambda: os.getenv("THU_MUC_BAO_CAO", "bao_cao"))
    thu_muc_anh_sinh_vien: str = field(
        default_factory=lambda: os.getenv("THU_MUC_ANH_SINH_VIEN", "du_lieu/anh_sinh_vien")
    )
    thu_muc_du_lieu_khuon_mat: str = field(
        default_factory=lambda: os.getenv("THU_MUC_DU_LIEU_KHUON_MAT", "du_lieu/khuon_mat")
    )


class CaiDatHeThong:
    """Lop tong hop toan bo cau hinh, dung theo mo hinh singleton don gian."""

    _instance: "CaiDatHeThong | None" = None

    def __init__(self) -> None:
        self.co_so_du_lieu = CauHinhCoSoDuLieu()
        self.bao_mat = CauHinhBaoMat()
        self.ai = CauHinhAI()
        self.ung_dung = CauHinhUngDung()
        self.thu_muc_goc = THU_MUC_GOC

    @classmethod
    def lay_thuc_the(cls) -> "CaiDatHeThong":
        """Tra ve thuc the duy nhat cua cau hinh he thong (singleton)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def duong_dan_tuyet_doi(self, duong_dan_tuong_doi: str) -> Path:
        """Chuyen duong dan tuong doi (tinh tu goc du an) thanh duong dan tuyet doi."""
        return (self.thu_muc_goc / duong_dan_tuong_doi).resolve()


def lay_cau_hinh() -> CaiDatHeThong:
    """Ham tien ich de lay cau hinh he thong tu bat ky module nao."""
    return CaiDatHeThong.lay_thuc_the()
