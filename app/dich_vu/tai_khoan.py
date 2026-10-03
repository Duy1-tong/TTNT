"""Dich vu Quan Ly Tai Khoan: tao, khoa/mo khoa, dat lai mat khau, doi vai tro (chi ADMIN)."""

from __future__ import annotations

import datetime as _datetime
from dataclasses import dataclass

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.dich_vu.phan_quyen import QuyenHeThong, yeu_cau_quyen
from app.mo_hinh.nguoi_dung import NguoiDung, TrangThaiTaiKhoan, VaiTro
from app.tien_ich.bao_mat import bam_mat_khau, kiem_tra_do_manh_mat_khau


class LoiDuLieuTaiKhoan(Exception):
    """Loi nghiep vu lien quan den quan ly tai khoan."""


@dataclass
class ThongTinTaiKhoan:
    """DTO the hien mot tai khoan trong danh sach quan ly."""

    id: int
    ten_dang_nhap: str
    ho_ten: str
    email: str | None
    vai_tro: str
    trang_thai: str
    lan_dang_nhap_cuoi: _datetime.datetime | None


def lay_danh_sach_tai_khoan(vai_tro_loc: VaiTro | None = None) -> list[ThongTinTaiKhoan]:
    """Lay danh sach tai khoan, co the loc theo vai tro."""
    with mo_phien_lam_viec() as phien:
        truy_van = phien.query(NguoiDung)
        if vai_tro_loc is not None:
            truy_van = truy_van.filter(NguoiDung.vai_tro == vai_tro_loc)
        danh_sach = truy_van.order_by(NguoiDung.ten_dang_nhap).all()
        return [
            ThongTinTaiKhoan(
                id=nd.id,
                ten_dang_nhap=nd.ten_dang_nhap,
                ho_ten=nd.ho_ten,
                email=nd.email,
                vai_tro=nd.vai_tro.value,
                trang_thai=nd.trang_thai.value,
                lan_dang_nhap_cuoi=nd.lan_dang_nhap_cuoi,
            )
            for nd in danh_sach
        ]


def tao_tai_khoan(
    vai_tro_nguoi_thuc_hien: str,
    ten_dang_nhap: str,
    mat_khau_ban_dau: str,
    ho_ten: str,
    vai_tro_moi: VaiTro,
    email: str | None = None,
    nguoi_thuc_hien_id: int | None = None,
) -> int:
    """Tao tai khoan moi (chi ADMIN duoc phep). Tra ve id tai khoan vua tao."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_TAI_KHOAN)

    hop_le, thong_bao_loi = kiem_tra_do_manh_mat_khau(mat_khau_ban_dau)
    if not hop_le:
        raise LoiDuLieuTaiKhoan(thong_bao_loi)

    with mo_phien_lam_viec() as phien:
        if phien.query(NguoiDung).filter_by(ten_dang_nhap=ten_dang_nhap).first() is not None:
            raise LoiDuLieuTaiKhoan(f"Ten dang nhap '{ten_dang_nhap}' da ton tai.")

        tai_khoan_moi = NguoiDung(
            ten_dang_nhap=ten_dang_nhap,
            mat_khau_bam=bam_mat_khau(mat_khau_ban_dau),
            ho_ten=ho_ten,
            email=email,
            vai_tro=vai_tro_moi,
            trang_thai=TrangThaiTaiKhoan.HOAT_DONG,
        )
        phien.add(tai_khoan_moi)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="TAO_TAI_KHOAN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="nguoi_dung",
            doi_tuong_id=tai_khoan_moi.id,
            noi_dung=f"Tao tai khoan moi '{ten_dang_nhap}' voi vai tro {vai_tro_moi.value}.",
        )
        return tai_khoan_moi.id


def khoa_hoac_mo_khoa_tai_khoan(
    vai_tro_nguoi_thuc_hien: str,
    tai_khoan_id: int,
    khoa: bool,
    nguoi_thuc_hien_id: int | None = None,
) -> None:
    """Khoa hoac mo khoa mot tai khoan (chi ADMIN duoc phep)."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_TAI_KHOAN)

    with mo_phien_lam_viec() as phien:
        nguoi_dung = phien.get(NguoiDung, tai_khoan_id)
        if nguoi_dung is None:
            raise LoiDuLieuTaiKhoan("Khong tim thay tai khoan.")

        nguoi_dung.trang_thai = TrangThaiTaiKhoan.KHOA if khoa else TrangThaiTaiKhoan.HOAT_DONG
        if khoa:
            nguoi_dung.thoi_diem_khoa = _datetime.datetime.utcnow()
        else:
            nguoi_dung.thoi_diem_khoa = None
            nguoi_dung.so_lan_dang_nhap_sai = 0
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="KHOA_TAI_KHOAN" if khoa else "MO_KHOA_TAI_KHOAN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="nguoi_dung",
            doi_tuong_id=tai_khoan_id,
            noi_dung=f"{'Khoa' if khoa else 'Mo khoa'} tai khoan '{nguoi_dung.ten_dang_nhap}'.",
        )


def dat_lai_mat_khau(
    vai_tro_nguoi_thuc_hien: str,
    tai_khoan_id: int,
    mat_khau_moi: str,
    nguoi_thuc_hien_id: int | None = None,
) -> None:
    """Dat lai mat khau cho mot tai khoan (chi ADMIN duoc phep, dung khi nguoi dung quen mat khau)."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_TAI_KHOAN)

    hop_le, thong_bao_loi = kiem_tra_do_manh_mat_khau(mat_khau_moi)
    if not hop_le:
        raise LoiDuLieuTaiKhoan(thong_bao_loi)

    with mo_phien_lam_viec() as phien:
        nguoi_dung = phien.get(NguoiDung, tai_khoan_id)
        if nguoi_dung is None:
            raise LoiDuLieuTaiKhoan("Khong tim thay tai khoan.")

        nguoi_dung.mat_khau_bam = bam_mat_khau(mat_khau_moi)
        nguoi_dung.so_lan_dang_nhap_sai = 0
        nguoi_dung.trang_thai = TrangThaiTaiKhoan.HOAT_DONG
        nguoi_dung.thoi_diem_khoa = None
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="DAT_LAI_MAT_KHAU",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="nguoi_dung",
            doi_tuong_id=tai_khoan_id,
            noi_dung=f"Dat lai mat khau cho tai khoan '{nguoi_dung.ten_dang_nhap}'.",
        )
