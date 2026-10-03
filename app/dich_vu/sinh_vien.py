"""Dich vu Quan Ly Sinh Vien: them, sua, tim kiem, xoa mem sinh vien."""

from __future__ import annotations

import datetime as _datetime
from dataclasses import dataclass

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.dich_vu.phan_quyen import QuyenHeThong, yeu_cau_quyen
from app.mo_hinh.diem_danh import DiemDanh
from app.mo_hinh.lop_hoc import LopHoc
from app.mo_hinh.sinh_vien import GioiTinh, SinhVien, TrangThaiSinhVien
from app.tien_ich.kiem_tra_du_lieu import (
    kiem_tra_chuoi_khong_rong,
    kiem_tra_dinh_dang_email,
    kiem_tra_dinh_dang_ma_dinh_danh,
    kiem_tra_dinh_dang_so_dien_thoai,
    kiem_tra_ngay_sinh_hop_le,
)


class LoiDuLieuSinhVien(Exception):
    """Loi nghiep vu lien quan den du lieu sinh vien."""


@dataclass
class ThongTinSinhVien:
    """DTO the hien mot sinh vien trong danh sach / form chi tiet."""

    id: int
    ma_sinh_vien: str
    ho_ten: str
    ngay_sinh: _datetime.date | None
    gioi_tinh: str | None
    email: str | None
    so_dien_thoai: str | None
    dia_chi: str | None
    lop_id: int | None
    ten_lop: str | None
    khoa_id: int | None
    anh_dai_dien: str | None
    trang_thai: str
    so_khuon_mat_da_dang_ky: int


def _chuyen_sang_dto(sinh_vien: SinhVien, ten_lop: str | None, so_khuon_mat: int) -> ThongTinSinhVien:
    return ThongTinSinhVien(
        id=sinh_vien.id,
        ma_sinh_vien=sinh_vien.ma_sinh_vien,
        ho_ten=sinh_vien.ho_ten,
        ngay_sinh=sinh_vien.ngay_sinh,
        gioi_tinh=sinh_vien.gioi_tinh.value if sinh_vien.gioi_tinh else None,
        email=sinh_vien.email,
        so_dien_thoai=sinh_vien.so_dien_thoai,
        dia_chi=sinh_vien.dia_chi,
        lop_id=sinh_vien.lop_id,
        ten_lop=ten_lop,
        khoa_id=sinh_vien.khoa_id,
        anh_dai_dien=sinh_vien.anh_dai_dien,
        trang_thai=sinh_vien.trang_thai.value,
        so_khuon_mat_da_dang_ky=so_khuon_mat,
    )


def _kiem_tra_hop_le(
    ma_sinh_vien: str, ho_ten: str, email: str | None, so_dien_thoai: str | None, ngay_sinh
) -> None:
    for hop_le, thong_bao in (
        kiem_tra_dinh_dang_ma_dinh_danh(ma_sinh_vien, "Ma sinh vien"),
        kiem_tra_chuoi_khong_rong(ho_ten, "Ho ten"),
        kiem_tra_dinh_dang_email(email),
        kiem_tra_dinh_dang_so_dien_thoai(so_dien_thoai),
        kiem_tra_ngay_sinh_hop_le(ngay_sinh),
    ):
        if not hop_le:
            raise LoiDuLieuSinhVien(thong_bao)


def lay_danh_sach_sinh_vien(
    tu_khoa_tim_kiem: str | None = None,
    lop_id: int | None = None,
    trang_thai: TrangThaiSinhVien | None = None,
) -> list[ThongTinSinhVien]:
    """Lay danh sach sinh vien, ho tro tim kiem theo ten/ma va loc theo lop/trang thai."""
    with mo_phien_lam_viec() as phien:
        truy_van = phien.query(SinhVien)
        if tu_khoa_tim_kiem:
            mau_tim = f"%{tu_khoa_tim_kiem.strip()}%"
            truy_van = truy_van.filter(
                (SinhVien.ho_ten.ilike(mau_tim)) | (SinhVien.ma_sinh_vien.ilike(mau_tim))
            )
        if lop_id is not None:
            truy_van = truy_van.filter(SinhVien.lop_id == lop_id)
        if trang_thai is not None:
            truy_van = truy_van.filter(SinhVien.trang_thai == trang_thai)

        danh_sach = truy_van.order_by(SinhVien.ho_ten).all()
        ket_qua: list[ThongTinSinhVien] = []
        for sinh_vien in danh_sach:
            ten_lop = None
            if sinh_vien.lop_id is not None:
                lop = phien.get(LopHoc, sinh_vien.lop_id)
                ten_lop = lop.ten_lop if lop else None
            so_khuon_mat = len(sinh_vien.danh_sach_khuon_mat)
            ket_qua.append(_chuyen_sang_dto(sinh_vien, ten_lop, so_khuon_mat))
        return ket_qua


def lay_sinh_vien_theo_id(sinh_vien_id: int) -> ThongTinSinhVien | None:
    """Lay chi tiet mot sinh vien theo id."""
    with mo_phien_lam_viec() as phien:
        sinh_vien = phien.get(SinhVien, sinh_vien_id)
        if sinh_vien is None:
            return None
        ten_lop = None
        if sinh_vien.lop_id is not None:
            lop = phien.get(LopHoc, sinh_vien.lop_id)
            ten_lop = lop.ten_lop if lop else None
        return _chuyen_sang_dto(sinh_vien, ten_lop, len(sinh_vien.danh_sach_khuon_mat))


def them_sinh_vien(
    vai_tro_nguoi_thuc_hien: str,
    ma_sinh_vien: str,
    ho_ten: str,
    ngay_sinh: _datetime.date | None = None,
    gioi_tinh: GioiTinh | None = None,
    email: str | None = None,
    so_dien_thoai: str | None = None,
    dia_chi: str | None = None,
    lop_id: int | None = None,
    khoa_id: int | None = None,
    nguoi_thuc_hien_id: int | None = None,
) -> int:
    """Them moi mot sinh vien. Tra ve id sinh vien vua tao."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_SINH_VIEN)
    _kiem_tra_hop_le(ma_sinh_vien, ho_ten, email, so_dien_thoai, ngay_sinh)

    with mo_phien_lam_viec() as phien:
        if phien.query(SinhVien).filter_by(ma_sinh_vien=ma_sinh_vien).first() is not None:
            raise LoiDuLieuSinhVien(f"Ma sinh vien '{ma_sinh_vien}' da ton tai.")
        if email and phien.query(SinhVien).filter_by(email=email).first() is not None:
            raise LoiDuLieuSinhVien(f"Email '{email}' da duoc su dung boi sinh vien khac.")

        sinh_vien_moi = SinhVien(
            ma_sinh_vien=ma_sinh_vien,
            ho_ten=ho_ten,
            ngay_sinh=ngay_sinh,
            gioi_tinh=gioi_tinh,
            email=email,
            so_dien_thoai=so_dien_thoai,
            dia_chi=dia_chi,
            lop_id=lop_id,
            khoa_id=khoa_id,
            trang_thai=TrangThaiSinhVien.DANG_HOC,
        )
        phien.add(sinh_vien_moi)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="THEM_SINH_VIEN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="sinh_vien",
            doi_tuong_id=sinh_vien_moi.id,
            noi_dung=f"Them sinh vien moi: {ma_sinh_vien} - {ho_ten}.",
        )
        return sinh_vien_moi.id


def cap_nhat_sinh_vien(
    vai_tro_nguoi_thuc_hien: str,
    sinh_vien_id: int,
    ho_ten: str,
    ngay_sinh: _datetime.date | None = None,
    gioi_tinh: GioiTinh | None = None,
    email: str | None = None,
    so_dien_thoai: str | None = None,
    dia_chi: str | None = None,
    lop_id: int | None = None,
    khoa_id: int | None = None,
    nguoi_thuc_hien_id: int | None = None,
) -> None:
    """Cap nhat thong tin mot sinh vien da ton tai."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_SINH_VIEN)

    with mo_phien_lam_viec() as phien:
        sinh_vien = phien.get(SinhVien, sinh_vien_id)
        if sinh_vien is None:
            raise LoiDuLieuSinhVien("Khong tim thay sinh vien.")

        _kiem_tra_hop_le(sinh_vien.ma_sinh_vien, ho_ten, email, so_dien_thoai, ngay_sinh)

        if email and email != sinh_vien.email:
            trung = phien.query(SinhVien).filter(
                SinhVien.email == email, SinhVien.id != sinh_vien_id
            ).first()
            if trung is not None:
                raise LoiDuLieuSinhVien(f"Email '{email}' da duoc su dung boi sinh vien khac.")

        sinh_vien.ho_ten = ho_ten
        sinh_vien.ngay_sinh = ngay_sinh
        sinh_vien.gioi_tinh = gioi_tinh
        sinh_vien.email = email
        sinh_vien.so_dien_thoai = so_dien_thoai
        sinh_vien.dia_chi = dia_chi
        sinh_vien.lop_id = lop_id
        sinh_vien.khoa_id = khoa_id
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="CAP_NHAT_SINH_VIEN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="sinh_vien",
            doi_tuong_id=sinh_vien_id,
            noi_dung=f"Cap nhat thong tin sinh vien {sinh_vien.ma_sinh_vien}.",
        )


def doi_trang_thai_sinh_vien(
    vai_tro_nguoi_thuc_hien: str,
    sinh_vien_id: int,
    trang_thai_moi: TrangThaiSinhVien,
    nguoi_thuc_hien_id: int | None = None,
) -> None:
    """Doi trang thai sinh vien (xoa mem): DANG_HOC / NGHI_HOC / BAO_LUU / TOT_NGHIEP.

    KHONG xoa vat ly ban ghi sinh vien de bao toan lich su diem danh.
    """
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_SINH_VIEN)

    with mo_phien_lam_viec() as phien:
        sinh_vien = phien.get(SinhVien, sinh_vien_id)
        if sinh_vien is None:
            raise LoiDuLieuSinhVien("Khong tim thay sinh vien.")

        sinh_vien.trang_thai = trang_thai_moi
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="DOI_TRANG_THAI_SINH_VIEN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="sinh_vien",
            doi_tuong_id=sinh_vien_id,
            noi_dung=f"Doi trang thai sinh vien {sinh_vien.ma_sinh_vien} sang {trang_thai_moi.value}.",
        )


def xoa_sinh_vien(
    vai_tro_nguoi_thuc_hien: str, sinh_vien_id: int, nguoi_thuc_hien_id: int | None = None
) -> None:
    """Xoa vat ly mot sinh vien — CHI cho phep neu sinh vien chua co lich su diem danh nao."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_SINH_VIEN)

    with mo_phien_lam_viec() as phien:
        sinh_vien = phien.get(SinhVien, sinh_vien_id)
        if sinh_vien is None:
            raise LoiDuLieuSinhVien("Khong tim thay sinh vien.")

        co_lich_su = phien.query(DiemDanh).filter_by(sinh_vien_id=sinh_vien_id).first() is not None
        if co_lich_su:
            raise LoiDuLieuSinhVien(
                "Khong the xoa sinh vien da co lich su diem danh. "
                "Vui long chuyen trang thai sang NGHI_HOC/BAO_LUU/TOT_NGHIEP thay vi xoa."
            )

        ma_sinh_vien = sinh_vien.ma_sinh_vien
        phien.delete(sinh_vien)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="XOA_SINH_VIEN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="sinh_vien",
            doi_tuong_id=sinh_vien_id,
            noi_dung=f"Xoa sinh vien {ma_sinh_vien}.",
        )


def lay_sinh_vien_theo_nguoi_dung_id(nguoi_dung_id: int) -> ThongTinSinhVien | None:
    """Tra ve ho so sinh vien lien ket voi mot tai khoan dang nhap cu the.

    Dung khi tai khoan dang nhap co vai tro SINH_VIEN can tu tra cuu ho so
    va lich su diem danh cua chinh minh.
    """
    with mo_phien_lam_viec() as phien:
        sinh_vien = phien.query(SinhVien).filter_by(nguoi_dung_id=nguoi_dung_id).first()
        if sinh_vien is None:
            return None
        ten_lop = None
        if sinh_vien.lop_id is not None:
            lop = phien.get(LopHoc, sinh_vien.lop_id)
            ten_lop = lop.ten_lop if lop else None
        return _chuyen_sang_dto(sinh_vien, ten_lop, len(sinh_vien.danh_sach_khuon_mat))
