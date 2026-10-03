"""Kiem thu dich vu Sinh Vien: them/sua/xoa, chong trung ma, khong xoa vat ly khi da co diem danh."""

from __future__ import annotations

import datetime

import pytest

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu import sinh_vien as dv_sinh_vien
from app.dich_vu.phan_quyen import LoiKhongDuQuyen
from app.dich_vu.sinh_vien import LoiDuLieuSinhVien
from app.mo_hinh.diem_danh import DiemDanh, PhuongThucDiemDanh, TrangThaiDiemDanh
from app.mo_hinh.sinh_vien import GioiTinh, TrangThaiSinhVien

MA_SINH_VIEN_TEST = "SV_TEST_KT01"


@pytest.fixture()
def sinh_vien_tam():
    """Tao mot sinh vien tam thoi de kiem thu, tu dong don dep sau khi test xong."""
    sinh_vien_id = dv_sinh_vien.them_sinh_vien(
        "ADMIN",
        ma_sinh_vien=MA_SINH_VIEN_TEST,
        ho_ten="Sinh Vien Kiem Thu",
        ngay_sinh=datetime.date(2004, 1, 1),
        gioi_tinh=GioiTinh.NAM,
        email=None,
        so_dien_thoai=None,
        dia_chi=None,
        lop_id=None,
        khoa_id=None,
        nguoi_thuc_hien_id=1,
    )
    yield sinh_vien_id

    with mo_phien_lam_viec() as phien:
        from app.mo_hinh.khuon_mat import KhuonMat
        from app.mo_hinh.sinh_vien import SinhVien

        phien.query(DiemDanh).filter_by(sinh_vien_id=sinh_vien_id).delete()
        phien.query(KhuonMat).filter_by(sinh_vien_id=sinh_vien_id).delete()
        ban_ghi = phien.get(SinhVien, sinh_vien_id)
        if ban_ghi is not None:
            phien.delete(ban_ghi)
        phien.commit()


def test_them_sinh_vien_thanh_cong(sinh_vien_tam) -> None:
    thong_tin = dv_sinh_vien.lay_sinh_vien_theo_id(sinh_vien_tam)
    assert thong_tin is not None
    assert thong_tin.ma_sinh_vien == MA_SINH_VIEN_TEST
    assert thong_tin.trang_thai == TrangThaiSinhVien.DANG_HOC.value


def test_them_sinh_vien_trung_ma_bi_tu_choi(sinh_vien_tam) -> None:
    with pytest.raises(LoiDuLieuSinhVien):
        dv_sinh_vien.them_sinh_vien(
            "ADMIN", ma_sinh_vien=MA_SINH_VIEN_TEST, ho_ten="Trung Ma", nguoi_thuc_hien_id=1
        )


def test_sinh_vien_khong_du_quyen_bi_tu_choi() -> None:
    with pytest.raises(LoiKhongDuQuyen):
        dv_sinh_vien.them_sinh_vien(
            "SINH_VIEN", ma_sinh_vien="SV_KHONG_HOP_LE", ho_ten="X", nguoi_thuc_hien_id=1
        )


def test_cap_nhat_thong_tin_sinh_vien(sinh_vien_tam) -> None:
    dv_sinh_vien.cap_nhat_sinh_vien(
        "ADMIN", sinh_vien_id=sinh_vien_tam, ho_ten="Ten Da Cap Nhat", nguoi_thuc_hien_id=1
    )
    thong_tin = dv_sinh_vien.lay_sinh_vien_theo_id(sinh_vien_tam)
    assert thong_tin.ho_ten == "Ten Da Cap Nhat"


def test_doi_trang_thai_sinh_vien(sinh_vien_tam) -> None:
    dv_sinh_vien.doi_trang_thai_sinh_vien(
        "ADMIN", sinh_vien_tam, TrangThaiSinhVien.BAO_LUU, nguoi_thuc_hien_id=1
    )
    thong_tin = dv_sinh_vien.lay_sinh_vien_theo_id(sinh_vien_tam)
    assert thong_tin.trang_thai == TrangThaiSinhVien.BAO_LUU.value


def test_xoa_sinh_vien_that_bai_khi_da_co_lich_su_diem_danh(sinh_vien_tam) -> None:
    """Sinh vien da co ban ghi diem danh KHONG duoc phep xoa vat ly (chi doi trang thai)."""
    with mo_phien_lam_viec() as phien:
        from app.mo_hinh.buoi_hoc import BuoiHoc

        buoi_hoc_gia = phien.query(BuoiHoc).first()
        if buoi_hoc_gia is None:
            pytest.skip("Chua co buoi hoc nao trong CSDL de kiem thu tinh huong nay.")
        ban_ghi_diem_danh = DiemDanh(
            buoi_hoc_id=buoi_hoc_gia.id,
            sinh_vien_id=sinh_vien_tam,
            trang_thai=TrangThaiDiemDanh.CO_MAT,
            phuong_thuc=PhuongThucDiemDanh.THU_CONG,
        )
        phien.add(ban_ghi_diem_danh)
        phien.commit()

    with pytest.raises(LoiDuLieuSinhVien):
        dv_sinh_vien.xoa_sinh_vien("ADMIN", sinh_vien_tam, nguoi_thuc_hien_id=1)


def test_lay_danh_sach_sinh_vien_tim_kiem_theo_ten(sinh_vien_tam) -> None:
    ket_qua = dv_sinh_vien.lay_danh_sach_sinh_vien(tu_khoa_tim_kiem="Sinh Vien Kiem Thu")
    assert any(sv.id == sinh_vien_tam for sv in ket_qua)
