"""Dich vu Cau Hinh He Thong: doc/ghi cac tham so cau hinh dong (bang cau_hinh)."""

from __future__ import annotations

from dataclasses import dataclass

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.dich_vu.phan_quyen import QuyenHeThong, yeu_cau_quyen
from app.mo_hinh.cau_hinh import CauHinh


class LoiCauHinh(Exception):
    """Loi nghiep vu lien quan den cau hinh he thong."""


@dataclass
class ThongTinCauHinh:
    """DTO the hien mot dong cau hinh khoa-gia tri."""

    id: int
    khoa_cau_hinh: str
    gia_tri: str | None
    mo_ta: str | None


def lay_danh_sach_cau_hinh() -> list[ThongTinCauHinh]:
    """Lay toan bo cac dong cau hinh dang co trong CSDL."""
    with mo_phien_lam_viec() as phien:
        danh_sach = phien.query(CauHinh).order_by(CauHinh.khoa_cau_hinh).all()
        return [
            ThongTinCauHinh(id=c.id, khoa_cau_hinh=c.khoa_cau_hinh, gia_tri=c.gia_tri, mo_ta=c.mo_ta)
            for c in danh_sach
        ]


def lay_gia_tri_cau_hinh(khoa_cau_hinh: str, gia_tri_mac_dinh: str | None = None) -> str | None:
    """Lay gia tri cua mot khoa cau hinh cu the, tra ve mac dinh neu chua co."""
    with mo_phien_lam_viec() as phien:
        ban_ghi = phien.query(CauHinh).filter_by(khoa_cau_hinh=khoa_cau_hinh).first()
        return ban_ghi.gia_tri if ban_ghi is not None else gia_tri_mac_dinh


def cap_nhat_cau_hinh(
    vai_tro_nguoi_thuc_hien: str,
    khoa_cau_hinh: str,
    gia_tri_moi: str,
    nguoi_thuc_hien_id: int | None = None,
) -> None:
    """Cap nhat (hoac tao moi neu chua co) mot dong cau hinh. Chi ADMIN duoc phep."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.THAY_DOI_CAU_HINH_HE_THONG)

    with mo_phien_lam_viec() as phien:
        ban_ghi = phien.query(CauHinh).filter_by(khoa_cau_hinh=khoa_cau_hinh).first()
        if ban_ghi is None:
            ban_ghi = CauHinh(khoa_cau_hinh=khoa_cau_hinh, gia_tri=gia_tri_moi)
            phien.add(ban_ghi)
        else:
            ban_ghi.gia_tri = gia_tri_moi
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="THAY_DOI_CAU_HINH",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="cau_hinh",
            doi_tuong_id=ban_ghi.id,
            noi_dung=f"Cap nhat cau hinh '{khoa_cau_hinh}' = '{gia_tri_moi}'.",
        )
