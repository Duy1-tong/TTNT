"""Dich vu Nhat Ky: ghi va truy van nhat ky he thong (audit log)."""

from __future__ import annotations

import datetime as _datetime
import logging
from dataclasses import dataclass

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.mo_hinh.nguoi_dung import NguoiDung
from app.mo_hinh.nhat_ky_he_thong import KetQuaHanhDong, NhatKyHeThong

_bo_ghi_log = logging.getLogger(__name__)


@dataclass
class BanGhiNhatKy:
    """DTO (Data Transfer Object) cho mot dong nhat ky, an toan de dung ngoai phien lam viec."""

    id: int
    nguoi_dung_id: int | None
    ten_dang_nhap: str
    hanh_dong: str
    doi_tuong: str | None
    doi_tuong_id: int | None
    noi_dung: str | None
    dia_chi_ip: str | None
    thoi_gian: _datetime.datetime
    ket_qua: str


def ghi_nhat_ky(
    hanh_dong: str,
    nguoi_dung_id: int | None,
    noi_dung: str | None = None,
    doi_tuong: str | None = None,
    doi_tuong_id: int | None = None,
    dia_chi_ip: str = "127.0.0.1",
    thanh_cong: bool = True,
) -> None:
    """Ghi mot ban ghi vao bang nhat_ky_he_thong.

    QUAN TRONG: khong bao gio truyen mat khau (dang ro hay da bam) vao
    tham so `noi_dung`. Ham nay khong throw loi ra ngoai de tranh lam
    gian doan luong nghiep vu chinh khi ghi log that bai — chi log canh bao
    noi bo.
    """
    try:
        with mo_phien_lam_viec() as phien:
            ban_ghi = NhatKyHeThong(
                nguoi_dung_id=nguoi_dung_id,
                hanh_dong=hanh_dong,
                doi_tuong=doi_tuong,
                doi_tuong_id=doi_tuong_id,
                noi_dung=noi_dung,
                dia_chi_ip=dia_chi_ip,
                ket_qua=KetQuaHanhDong.THANH_CONG if thanh_cong else KetQuaHanhDong.THAT_BAI,
            )
            phien.add(ban_ghi)
            phien.commit()
    except Exception as loi:  # noqa: BLE001 - khong de loi ghi log lam sap ung dung
        _bo_ghi_log.error("Khong the ghi nhat ky he thong: %s", loi)


def lay_danh_sach_nhat_ky(
    gioi_han: int = 200,
    hanh_dong: str | None = None,
    nguoi_dung_id: int | None = None,
) -> list[BanGhiNhatKy]:
    """Lay danh sach nhat ky he thong, sap xep moi nhat truoc, co the loc theo dieu kien."""
    with mo_phien_lam_viec() as phien:
        truy_van = (
            phien.query(NhatKyHeThong, NguoiDung.ten_dang_nhap)
            .outerjoin(NguoiDung, NhatKyHeThong.nguoi_dung_id == NguoiDung.id)
        )
        if hanh_dong:
            truy_van = truy_van.filter(NhatKyHeThong.hanh_dong == hanh_dong)
        if nguoi_dung_id is not None:
            truy_van = truy_van.filter(NhatKyHeThong.nguoi_dung_id == nguoi_dung_id)
        ket_qua = truy_van.order_by(NhatKyHeThong.thoi_gian.desc()).limit(gioi_han).all()

        return [
            BanGhiNhatKy(
                id=ban_ghi.id,
                nguoi_dung_id=ban_ghi.nguoi_dung_id,
                ten_dang_nhap=ten_dang_nhap or "(He thong)",
                hanh_dong=ban_ghi.hanh_dong,
                doi_tuong=ban_ghi.doi_tuong,
                doi_tuong_id=ban_ghi.doi_tuong_id,
                noi_dung=ban_ghi.noi_dung,
                dia_chi_ip=ban_ghi.dia_chi_ip,
                thoi_gian=ban_ghi.thoi_gian,
                ket_qua=ban_ghi.ket_qua.value,
            )
            for ban_ghi, ten_dang_nhap in ket_qua
        ]
