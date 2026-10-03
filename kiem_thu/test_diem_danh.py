"""Kiem thu dich vu Diem Danh: tao buoi hoc, diem danh thu cong, chong trung, tu dong vang."""

from __future__ import annotations

import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu import danh_muc, sinh_vien as dv_sinh_vien
from app.dich_vu import diem_danh as dv_diem_danh
from app.dich_vu.diem_danh import LoiDiemDanh
from app.mo_hinh.diem_danh import DiemDanh, PhuongThucDiemDanh, TrangThaiDiemDanh

MA_MON_TEST = "MON_TEST_DD"
MA_LOP_MON_TEST = "LOPMON_TEST_DD"
MA_SINH_VIEN_TEST = "SV_TEST_DD01"


@pytest.fixture()
def boi_canh_diem_danh():
    """Chuan bi mot lop hoc phan + sinh vien dang ky, don dep toan bo sau khi xong."""
    mon_id = danh_muc.them_mon_hoc("ADMIN", ma_mon=MA_MON_TEST, ten_mon="Mon Kiem Thu", so_tin_chi=2)
    lop_mon_id = danh_muc.them_lop_mon_hoc(
        "ADMIN", ma_lop_mon=MA_LOP_MON_TEST, mon_hoc_id=mon_id, giang_vien_id=None,
        hoc_ky="HK_TEST", nam_hoc="2099-2100",
    )
    sinh_vien_id = dv_sinh_vien.them_sinh_vien(
        "ADMIN", ma_sinh_vien=MA_SINH_VIEN_TEST, ho_ten="Sinh Vien Kiem Thu Diem Danh",
        nguoi_thuc_hien_id=1,
    )
    danh_muc.dang_ky_sinh_vien_vao_lop_mon_hoc("ADMIN", sinh_vien_id, lop_mon_id)

    yield {"mon_id": mon_id, "lop_mon_id": lop_mon_id, "sinh_vien_id": sinh_vien_id}

    with mo_phien_lam_viec() as phien:
        from app.mo_hinh.buoi_hoc import BuoiHoc
        from app.mo_hinh.lop_mon_hoc import LopMonHoc
        from app.mo_hinh.mon_hoc import MonHoc
        from app.mo_hinh.sinh_vien import SinhVien
        from app.mo_hinh.sinh_vien_lop import SinhVienLop

        cac_buoi = phien.query(BuoiHoc).filter_by(lop_mon_hoc_id=lop_mon_id).all()
        for buoi in cac_buoi:
            phien.query(DiemDanh).filter_by(buoi_hoc_id=buoi.id).delete()
            phien.delete(buoi)
        phien.query(SinhVienLop).filter_by(lop_mon_hoc_id=lop_mon_id).delete()
        phien.commit()

        ban_ghi_lop_mon = phien.get(LopMonHoc, lop_mon_id)
        if ban_ghi_lop_mon is not None:
            phien.delete(ban_ghi_lop_mon)
        ban_ghi_mon = phien.get(MonHoc, mon_id)
        if ban_ghi_mon is not None:
            phien.delete(ban_ghi_mon)
        ban_ghi_sinh_vien = phien.get(SinhVien, sinh_vien_id)
        if ban_ghi_sinh_vien is not None:
            phien.delete(ban_ghi_sinh_vien)
        phien.commit()


def test_tao_buoi_hoc_va_mo_diem_danh(boi_canh_diem_danh) -> None:
    buoi_hoc_id = dv_diem_danh.tao_buoi_hoc(
        "ADMIN", lop_mon_hoc_id=boi_canh_diem_danh["lop_mon_id"], ngay_hoc=datetime.date.today(),
        gio_bat_dau=datetime.time(8, 0), gio_ket_thuc=datetime.time(10, 0), phong_hoc="P.KT",
        nguoi_thuc_hien_id=1,
    )
    assert buoi_hoc_id > 0
    dv_diem_danh.mo_diem_danh_cho_buoi_hoc("ADMIN", buoi_hoc_id, nguoi_thuc_hien_id=1)

    danh_sach = dv_diem_danh.lay_danh_sach_buoi_hoc(lop_mon_hoc_id=boi_canh_diem_danh["lop_mon_id"])
    buoi = next(b for b in danh_sach if b.id == buoi_hoc_id)
    assert buoi.trang_thai == "DANG_DIEM_DANH"


def test_tao_buoi_hoc_gio_ket_thuc_truoc_gio_bat_dau_bi_tu_choi(boi_canh_diem_danh) -> None:
    with pytest.raises(LoiDiemDanh):
        dv_diem_danh.tao_buoi_hoc(
            "ADMIN", lop_mon_hoc_id=boi_canh_diem_danh["lop_mon_id"], ngay_hoc=datetime.date.today(),
            gio_bat_dau=datetime.time(10, 0), gio_ket_thuc=datetime.time(8, 0), phong_hoc=None,
            nguoi_thuc_hien_id=1,
        )


def test_diem_danh_thu_cong_va_chong_trung_lap(boi_canh_diem_danh) -> None:
    buoi_hoc_id = dv_diem_danh.tao_buoi_hoc(
        "ADMIN", lop_mon_hoc_id=boi_canh_diem_danh["lop_mon_id"], ngay_hoc=datetime.date.today(),
        gio_bat_dau=datetime.time(8, 0), gio_ket_thuc=datetime.time(10, 0), phong_hoc=None,
        nguoi_thuc_hien_id=1,
    )
    dv_diem_danh.mo_diem_danh_cho_buoi_hoc("ADMIN", buoi_hoc_id, nguoi_thuc_hien_id=1)

    dv_diem_danh.diem_danh_thu_cong(
        "ADMIN", buoi_hoc_id, boi_canh_diem_danh["sinh_vien_id"], TrangThaiDiemDanh.CO_MAT,
        nguoi_thuc_hien_id=1,
    )
    # Goi lai lan 2 phai CAP NHAT ban ghi cu, khong tao ban ghi moi (nho UNIQUE constraint)
    dv_diem_danh.diem_danh_thu_cong(
        "ADMIN", buoi_hoc_id, boi_canh_diem_danh["sinh_vien_id"], TrangThaiDiemDanh.DI_MUON,
        nguoi_thuc_hien_id=1,
    )

    with mo_phien_lam_viec() as phien:
        cac_ban_ghi = (
            phien.query(DiemDanh)
            .filter_by(buoi_hoc_id=buoi_hoc_id, sinh_vien_id=boi_canh_diem_danh["sinh_vien_id"])
            .all()
        )
        assert len(cac_ban_ghi) == 1
        assert cac_ban_ghi[0].trang_thai == TrangThaiDiemDanh.DI_MUON


def test_rang_buoc_duy_nhat_chan_diem_danh_trung_o_cap_csdl(boi_canh_diem_danh) -> None:
    """Kiem tra truc tiep UNIQUE(buoi_hoc_id, sinh_vien_id) o tang CSDL."""
    buoi_hoc_id = dv_diem_danh.tao_buoi_hoc(
        "ADMIN", lop_mon_hoc_id=boi_canh_diem_danh["lop_mon_id"], ngay_hoc=datetime.date.today(),
        gio_bat_dau=datetime.time(8, 0), gio_ket_thuc=datetime.time(10, 0), phong_hoc=None,
        nguoi_thuc_hien_id=1,
    )
    with mo_phien_lam_viec() as phien:
        phien.add(DiemDanh(
            buoi_hoc_id=buoi_hoc_id, sinh_vien_id=boi_canh_diem_danh["sinh_vien_id"],
            trang_thai=TrangThaiDiemDanh.CO_MAT, phuong_thuc=PhuongThucDiemDanh.THU_CONG,
        ))
        phien.commit()

    with mo_phien_lam_viec() as phien:
        phien.add(DiemDanh(
            buoi_hoc_id=buoi_hoc_id, sinh_vien_id=boi_canh_diem_danh["sinh_vien_id"],
            trang_thai=TrangThaiDiemDanh.VANG, phuong_thuc=PhuongThucDiemDanh.THU_CONG,
        ))
        with pytest.raises(IntegrityError):
            phien.commit()
        phien.rollback()


def test_dong_diem_danh_tu_dong_danh_dau_vang(boi_canh_diem_danh) -> None:
    buoi_hoc_id = dv_diem_danh.tao_buoi_hoc(
        "ADMIN", lop_mon_hoc_id=boi_canh_diem_danh["lop_mon_id"], ngay_hoc=datetime.date.today(),
        gio_bat_dau=datetime.time(8, 0), gio_ket_thuc=datetime.time(10, 0), phong_hoc=None,
        nguoi_thuc_hien_id=1,
    )
    dv_diem_danh.mo_diem_danh_cho_buoi_hoc("ADMIN", buoi_hoc_id, nguoi_thuc_hien_id=1)
    # Khong diem danh cho ai ca, roi dong lai
    dv_diem_danh.dong_diem_danh_cho_buoi_hoc("ADMIN", buoi_hoc_id, nguoi_thuc_hien_id=1)

    danh_sach = dv_diem_danh.lay_danh_sach_diem_danh_theo_buoi_hoc(buoi_hoc_id)
    ban_ghi_sinh_vien = next(
        d for d in danh_sach if d.sinh_vien_id == boi_canh_diem_danh["sinh_vien_id"]
    )
    assert ban_ghi_sinh_vien.trang_thai == "VANG"
