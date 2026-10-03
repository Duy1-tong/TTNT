"""Kiem thu dich vu Xac Thuc: dang nhap thanh cong, sai mat khau, khoa tai khoan."""

from __future__ import annotations

import pytest

from app.cau_hinh.cai_dat import lay_cau_hinh
from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.xac_thuc import LoiXacThuc, dang_nhap, doi_mat_khau
from app.mo_hinh.nguoi_dung import NguoiDung, TrangThaiTaiKhoan, VaiTro
from app.tien_ich.bao_mat import bam_mat_khau

TEN_DANG_NHAP_TEST = "test_dang_nhap_tam"
MAT_KHAU_TEST = "MatKhauTest@123"


@pytest.fixture()
def tai_khoan_tam():
    """Tao mot tai khoan tam thoi de kiem thu dang nhap, tu dong xoa sau khi test xong."""
    with mo_phien_lam_viec() as phien:
        tai_khoan = NguoiDung(
            ten_dang_nhap=TEN_DANG_NHAP_TEST,
            mat_khau_bam=bam_mat_khau(MAT_KHAU_TEST),
            ho_ten="Tai Khoan Kiem Thu Dang Nhap",
            vai_tro=VaiTro.SINH_VIEN,
            trang_thai=TrangThaiTaiKhoan.HOAT_DONG,
        )
        phien.add(tai_khoan)
        phien.commit()
        tai_khoan_id = tai_khoan.id

    yield tai_khoan_id

    with mo_phien_lam_viec() as phien:
        ban_ghi = phien.get(NguoiDung, tai_khoan_id)
        if ban_ghi is not None:
            phien.delete(ban_ghi)
            phien.commit()


def test_dang_nhap_thanh_cong_voi_mat_khau_dung(tai_khoan_tam) -> None:
    phien_dang_nhap = dang_nhap(TEN_DANG_NHAP_TEST, MAT_KHAU_TEST)
    assert phien_dang_nhap.ten_dang_nhap == TEN_DANG_NHAP_TEST
    assert phien_dang_nhap.vai_tro == "SINH_VIEN"


def test_dang_nhap_that_bai_voi_mat_khau_sai(tai_khoan_tam) -> None:
    with pytest.raises(LoiXacThuc):
        dang_nhap(TEN_DANG_NHAP_TEST, "mat_khau_sai_hoan_toan")


def test_dang_nhap_voi_tai_khoan_khong_ton_tai() -> None:
    with pytest.raises(LoiXacThuc):
        dang_nhap("tai_khoan_khong_bao_gio_ton_tai_xyz", "bat_ky_mat_khau_nao")


def test_khoa_tai_khoan_sau_qua_nhieu_lan_dang_nhap_sai(tai_khoan_tam) -> None:
    so_lan_toi_da = lay_cau_hinh().bao_mat.so_lan_dang_nhap_sai_toi_da

    for _ in range(so_lan_toi_da - 1):
        with pytest.raises(LoiXacThuc):
            dang_nhap(TEN_DANG_NHAP_TEST, "sai_mat_khau")

    # Lan sai cuoi cung phai khien tai khoan bi khoa
    with pytest.raises(LoiXacThuc, match="khoa"):
        dang_nhap(TEN_DANG_NHAP_TEST, "sai_mat_khau")

    with mo_phien_lam_viec() as phien:
        tai_khoan = phien.get(NguoiDung, tai_khoan_tam)
        assert tai_khoan.trang_thai == TrangThaiTaiKhoan.KHOA

    # Ngay ca voi mat khau dung, tai khoan van bi tu choi vi dang bi khoa
    with pytest.raises(LoiXacThuc):
        dang_nhap(TEN_DANG_NHAP_TEST, MAT_KHAU_TEST)


def test_doi_mat_khau_thanh_cong_va_dang_nhap_lai_bang_mat_khau_moi(tai_khoan_tam) -> None:
    mat_khau_moi = "MatKhauMoi@456"
    doi_mat_khau(tai_khoan_tam, MAT_KHAU_TEST, mat_khau_moi)
    phien_dang_nhap = dang_nhap(TEN_DANG_NHAP_TEST, mat_khau_moi)
    assert phien_dang_nhap.nguoi_dung_id == tai_khoan_tam


def test_doi_mat_khau_that_bai_neu_mat_khau_cu_sai(tai_khoan_tam) -> None:
    with pytest.raises(LoiXacThuc):
        doi_mat_khau(tai_khoan_tam, "mat_khau_cu_sai", "MatKhauMoi@456")


def test_doi_mat_khau_that_bai_neu_mat_khau_moi_qua_yeu(tai_khoan_tam) -> None:
    with pytest.raises(LoiXacThuc):
        doi_mat_khau(tai_khoan_tam, MAT_KHAU_TEST, "123")
