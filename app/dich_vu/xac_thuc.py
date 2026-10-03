"""
Dich vu Xac Thuc: dang nhap, dang xuat, doi mat khau, chong brute-force.

Tang nay la noi DUY NHAT trong ung dung duoc phep kiem tra mat khau va
cap nhat trang thai dang nhap cua tai khoan. Giao dien (PySide6) chi duoc
goi cac ham o day, khong duoc tu truy van bang nguoi_dung.
"""

from __future__ import annotations

import datetime as _datetime
import logging
from dataclasses import dataclass

from app.cau_hinh.cai_dat import lay_cau_hinh
from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.mo_hinh.nguoi_dung import NguoiDung, TrangThaiTaiKhoan
from app.tien_ich.bao_mat import kiem_tra_do_manh_mat_khau, kiem_tra_mat_khau, bam_mat_khau

_bo_ghi_log = logging.getLogger(__name__)


class LoiXacThuc(Exception):
    """Ngoai le tuy chinh cho cac loi xay ra trong qua trinh xac thuc."""


@dataclass
class PhienDangNhap:
    """Thong tin phien dang nhap hien tai, dung xuyen suot ung dung sau khi dang nhap."""

    nguoi_dung_id: int
    ten_dang_nhap: str
    ho_ten: str
    vai_tro: str


def dang_nhap(ten_dang_nhap: str, mat_khau: str, dia_chi_ip: str = "127.0.0.1") -> PhienDangNhap:
    """Xac thuc tai khoan, tra ve PhienDangNhap neu thanh cong.

    Phat sinh LoiXacThuc voi thong bao tieng Viet ro rang neu that bai
    (sai mat khau, tai khoan bi khoa, tai khoan ngung hoat dong...).
    Tu dong khoa tai khoan sau khi dang nhap sai qua so lan cho phep.
    """
    cau_hinh_bao_mat = lay_cau_hinh().bao_mat

    with mo_phien_lam_viec() as phien:
        nguoi_dung = phien.query(NguoiDung).filter_by(ten_dang_nhap=ten_dang_nhap).first()

        if nguoi_dung is None:
            ghi_nhat_ky(
                hanh_dong="DANG_NHAP",
                nguoi_dung_id=None,
                noi_dung=f"Dang nhap that bai: khong ton tai tai khoan '{ten_dang_nhap}'.",
                dia_chi_ip=dia_chi_ip,
                thanh_cong=False,
            )
            raise LoiXacThuc("Ten dang nhap hoac mat khau khong dung.")

        _kiem_tra_va_tu_mo_khoa_neu_het_han(nguoi_dung, cau_hinh_bao_mat, phien)

        if nguoi_dung.trang_thai == TrangThaiTaiKhoan.NGUNG_HOAT_DONG:
            raise LoiXacThuc("Tai khoan da bi ngung hoat dong. Vui long lien he Quan tri vien.")

        if nguoi_dung.trang_thai == TrangThaiTaiKhoan.KHOA:
            raise LoiXacThuc(
                "Tai khoan dang bi khoa do dang nhap sai qua nhieu lan. "
                f"Vui long thu lai sau {cau_hinh_bao_mat.thoi_gian_khoa_tai_khoan_phut} phut."
            )

        if not kiem_tra_mat_khau(mat_khau, nguoi_dung.mat_khau_bam):
            nguoi_dung.so_lan_dang_nhap_sai += 1
            da_khoa = False
            if nguoi_dung.so_lan_dang_nhap_sai >= cau_hinh_bao_mat.so_lan_dang_nhap_sai_toi_da:
                nguoi_dung.trang_thai = TrangThaiTaiKhoan.KHOA
                nguoi_dung.thoi_diem_khoa = _datetime.datetime.utcnow()
                da_khoa = True
            phien.commit()

            ghi_nhat_ky(
                hanh_dong="DANG_NHAP",
                nguoi_dung_id=nguoi_dung.id,
                noi_dung=f"Dang nhap that bai lan thu {nguoi_dung.so_lan_dang_nhap_sai}.",
                dia_chi_ip=dia_chi_ip,
                thanh_cong=False,
            )
            if da_khoa:
                raise LoiXacThuc(
                    "Sai mat khau qua nhieu lan. Tai khoan da bi khoa tam thoi "
                    f"trong {cau_hinh_bao_mat.thoi_gian_khoa_tai_khoan_phut} phut."
                )
            raise LoiXacThuc("Ten dang nhap hoac mat khau khong dung.")

        # Dang nhap thanh cong: reset so lan sai, cap nhat lan dang nhap cuoi.
        nguoi_dung.so_lan_dang_nhap_sai = 0
        nguoi_dung.thoi_diem_khoa = None
        nguoi_dung.lan_dang_nhap_cuoi = _datetime.datetime.utcnow()
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="DANG_NHAP",
            nguoi_dung_id=nguoi_dung.id,
            noi_dung="Dang nhap thanh cong.",
            dia_chi_ip=dia_chi_ip,
            thanh_cong=True,
        )

        return PhienDangNhap(
            nguoi_dung_id=nguoi_dung.id,
            ten_dang_nhap=nguoi_dung.ten_dang_nhap,
            ho_ten=nguoi_dung.ho_ten,
            vai_tro=nguoi_dung.vai_tro.value,
        )


def _kiem_tra_va_tu_mo_khoa_neu_het_han(nguoi_dung: NguoiDung, cau_hinh_bao_mat, phien) -> None:
    """Neu tai khoan dang KHOA nhung da het thoi gian khoa, tu dong mo khoa lai."""
    if nguoi_dung.trang_thai != TrangThaiTaiKhoan.KHOA or nguoi_dung.thoi_diem_khoa is None:
        return
    thoi_gian_da_troi_qua = _datetime.datetime.utcnow() - nguoi_dung.thoi_diem_khoa
    if thoi_gian_da_troi_qua >= _datetime.timedelta(
        minutes=cau_hinh_bao_mat.thoi_gian_khoa_tai_khoan_phut
    ):
        nguoi_dung.trang_thai = TrangThaiTaiKhoan.HOAT_DONG
        nguoi_dung.so_lan_dang_nhap_sai = 0
        nguoi_dung.thoi_diem_khoa = None
        phien.commit()


def dang_xuat(nguoi_dung_id: int, dia_chi_ip: str = "127.0.0.1") -> None:
    """Ghi nhat ky dang xuat. Ban than viec dang xuat chu yeu xu ly o tang giao dien."""
    ghi_nhat_ky(
        hanh_dong="DANG_XUAT",
        nguoi_dung_id=nguoi_dung_id,
        noi_dung="Nguoi dung dang xuat khoi he thong.",
        dia_chi_ip=dia_chi_ip,
        thanh_cong=True,
    )


def doi_mat_khau(
    nguoi_dung_id: int, mat_khau_cu: str, mat_khau_moi: str, dia_chi_ip: str = "127.0.0.1"
) -> None:
    """Doi mat khau cho tai khoan hien tai. Phat sinh LoiXacThuc neu khong hop le."""
    with mo_phien_lam_viec() as phien:
        nguoi_dung = phien.get(NguoiDung, nguoi_dung_id)
        if nguoi_dung is None:
            raise LoiXacThuc("Khong tim thay tai khoan.")

        if not kiem_tra_mat_khau(mat_khau_cu, nguoi_dung.mat_khau_bam):
            ghi_nhat_ky(
                hanh_dong="DOI_MAT_KHAU",
                nguoi_dung_id=nguoi_dung_id,
                noi_dung="Doi mat khau that bai: mat khau cu khong dung.",
                dia_chi_ip=dia_chi_ip,
                thanh_cong=False,
            )
            raise LoiXacThuc("Mat khau hien tai khong dung.")

        hop_le, thong_bao_loi = kiem_tra_do_manh_mat_khau(mat_khau_moi)
        if not hop_le:
            raise LoiXacThuc(thong_bao_loi)

        nguoi_dung.mat_khau_bam = bam_mat_khau(mat_khau_moi)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="DOI_MAT_KHAU",
            nguoi_dung_id=nguoi_dung_id,
            noi_dung="Doi mat khau thanh cong.",
            dia_chi_ip=dia_chi_ip,
            thanh_cong=True,
        )
