"""
Goi chua toan bo model SQLAlchemy ORM anh xa toi cac bang trong MySQL.

Import tat ca model tai day de dam bao Base.metadata nhan biet day du
truoc khi goi Base.metadata.create_all().
"""

from app.mo_hinh.nguoi_dung import NguoiDung  # noqa: F401
from app.mo_hinh.khoa import Khoa  # noqa: F401
from app.mo_hinh.lop_hoc import LopHoc  # noqa: F401
from app.mo_hinh.giang_vien import GiangVien  # noqa: F401
from app.mo_hinh.sinh_vien import SinhVien  # noqa: F401
from app.mo_hinh.mon_hoc import MonHoc  # noqa: F401
from app.mo_hinh.lop_mon_hoc import LopMonHoc  # noqa: F401
from app.mo_hinh.sinh_vien_lop import SinhVienLop  # noqa: F401
from app.mo_hinh.buoi_hoc import BuoiHoc  # noqa: F401
from app.mo_hinh.diem_danh import DiemDanh  # noqa: F401
from app.mo_hinh.khuon_mat import KhuonMat  # noqa: F401
from app.mo_hinh.camera import Camera  # noqa: F401
from app.mo_hinh.nhat_ky_he_thong import NhatKyHeThong  # noqa: F401
from app.mo_hinh.cau_hinh import CauHinh  # noqa: F401

__all__ = [
    "NguoiDung",
    "Khoa",
    "LopHoc",
    "GiangVien",
    "SinhVien",
    "MonHoc",
    "LopMonHoc",
    "SinhVienLop",
    "BuoiHoc",
    "DiemDanh",
    "KhuonMat",
    "Camera",
    "NhatKyHeThong",
    "CauHinh",
]
