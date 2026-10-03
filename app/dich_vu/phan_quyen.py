"""
Dich vu Phan Quyen (RBAC - Role Based Access Control).

Moi thao tac nghiep vu quan trong (them/sua/xoa/xuat bao cao...) PHAI goi
qua ham `yeu_cau_quyen(...)` trong module nay TRUOC KHI thuc hien, bat ke
giao dien co an nut hay khong. Day la lop phong thu thu hai, dam bao du
mot request bi gia mao tu tang giao dien cung khong the vuot qua.
"""

from __future__ import annotations

from enum import Enum, auto

from app.mo_hinh.nguoi_dung import VaiTro


class QuyenHeThong(Enum):
    """Danh sach quyen (permission) rieng le trong he thong."""

    QUAN_LY_TAI_KHOAN = auto()
    QUAN_LY_SINH_VIEN = auto()
    QUAN_LY_GIANG_VIEN = auto()
    QUAN_LY_KHOA = auto()
    QUAN_LY_LOP = auto()
    QUAN_LY_MON_HOC = auto()
    QUAN_LY_CAMERA = auto()
    QUAN_LY_BUOI_HOC = auto()
    DANG_KY_KHUON_MAT = auto()
    THUC_HIEN_DIEM_DANH = auto()
    SUA_DIEM_DANH_THU_CONG = auto()
    XEM_LICH_SU_DIEM_DANH_TOAN_TRUONG = auto()
    XEM_LICH_SU_DIEM_DANH_LOP_PHU_TRACH = auto()
    XEM_LICH_SU_DIEM_DANH_CA_NHAN = auto()
    XUAT_BAO_CAO = auto()
    XEM_NHAT_KY_HE_THONG = auto()
    THAY_DOI_CAU_HINH_HE_THONG = auto()


_BANG_PHAN_QUYEN: dict[VaiTro, set[QuyenHeThong]] = {
    VaiTro.ADMIN: set(QuyenHeThong),  # Admin co toan bo quyen.
    VaiTro.GIANG_VIEN: {
        QuyenHeThong.QUAN_LY_BUOI_HOC,
        QuyenHeThong.THUC_HIEN_DIEM_DANH,
        QuyenHeThong.SUA_DIEM_DANH_THU_CONG,
        QuyenHeThong.XEM_LICH_SU_DIEM_DANH_LOP_PHU_TRACH,
        QuyenHeThong.XUAT_BAO_CAO,
    },
    VaiTro.SINH_VIEN: {
        QuyenHeThong.XEM_LICH_SU_DIEM_DANH_CA_NHAN,
    },
}


class LoiKhongDuQuyen(PermissionError):
    """Ngoai le phat sinh khi tai khoan khong co quyen thuc hien hanh dong."""


def co_quyen(vai_tro: VaiTro | str, quyen_can_kiem_tra: QuyenHeThong) -> bool:
    """Kiem tra mot vai tro co so huu mot quyen cu the hay khong."""
    if isinstance(vai_tro, str):
        vai_tro = VaiTro(vai_tro)
    return quyen_can_kiem_tra in _BANG_PHAN_QUYEN.get(vai_tro, set())


def yeu_cau_quyen(vai_tro: VaiTro | str, quyen_can_kiem_tra: QuyenHeThong) -> None:
    """Phat sinh LoiKhongDuQuyen neu vai tro khong co quyen can kiem tra.

    Cac ham trong tang Service PHAI goi ham nay o dau moi thao tac nhay cam,
    vi du:
        yeu_cau_quyen(vai_tro_nguoi_dung, QuyenHeThong.QUAN_LY_SINH_VIEN)
    """
    if not co_quyen(vai_tro, quyen_can_kiem_tra):
        ten_vai_tro = vai_tro.value if isinstance(vai_tro, VaiTro) else vai_tro
        raise LoiKhongDuQuyen(
            f"Tai khoan voi vai tro '{ten_vai_tro}' khong co quyen thuc hien hanh dong nay."
        )
