"""Kiem thu dich vu Phan Quyen (RBAC): dam bao moi vai tro chi co dung quyen duoc cap."""

from __future__ import annotations

import pytest

from app.dich_vu.phan_quyen import LoiKhongDuQuyen, QuyenHeThong, co_quyen, yeu_cau_quyen
from app.mo_hinh.nguoi_dung import VaiTro


def test_admin_co_toan_bo_quyen() -> None:
    for quyen in QuyenHeThong:
        assert co_quyen(VaiTro.ADMIN, quyen) is True


def test_giang_vien_co_quyen_diem_danh_nhung_khong_co_quyen_quan_ly_sinh_vien() -> None:
    assert co_quyen(VaiTro.GIANG_VIEN, QuyenHeThong.THUC_HIEN_DIEM_DANH) is True
    assert co_quyen(VaiTro.GIANG_VIEN, QuyenHeThong.SUA_DIEM_DANH_THU_CONG) is True
    assert co_quyen(VaiTro.GIANG_VIEN, QuyenHeThong.QUAN_LY_SINH_VIEN) is False
    assert co_quyen(VaiTro.GIANG_VIEN, QuyenHeThong.QUAN_LY_TAI_KHOAN) is False


def test_sinh_vien_chi_co_quyen_xem_lich_su_ca_nhan() -> None:
    assert co_quyen(VaiTro.SINH_VIEN, QuyenHeThong.XEM_LICH_SU_DIEM_DANH_CA_NHAN) is True
    assert co_quyen(VaiTro.SINH_VIEN, QuyenHeThong.THUC_HIEN_DIEM_DANH) is False
    assert co_quyen(VaiTro.SINH_VIEN, QuyenHeThong.QUAN_LY_SINH_VIEN) is False
    assert co_quyen(VaiTro.SINH_VIEN, QuyenHeThong.XUAT_BAO_CAO) is False


def test_yeu_cau_quyen_khong_phat_sinh_loi_khi_co_quyen() -> None:
    yeu_cau_quyen(VaiTro.ADMIN, QuyenHeThong.QUAN_LY_SINH_VIEN)  # Khong duoc phat sinh loi.


def test_yeu_cau_quyen_phat_sinh_loi_khi_khong_co_quyen() -> None:
    with pytest.raises(LoiKhongDuQuyen):
        yeu_cau_quyen(VaiTro.SINH_VIEN, QuyenHeThong.QUAN_LY_SINH_VIEN)


def test_co_quyen_chap_nhan_vai_tro_dang_chuoi() -> None:
    """Ham co_quyen phai hoat dong dung ca khi vai_tro truyen vao la string (tu PhienDangNhap)."""
    assert co_quyen("ADMIN", QuyenHeThong.QUAN_LY_SINH_VIEN) is True
    assert co_quyen("SINH_VIEN", QuyenHeThong.QUAN_LY_SINH_VIEN) is False
