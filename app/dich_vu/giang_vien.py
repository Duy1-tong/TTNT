"""Dich vu Quan Ly Giang Vien: them, sua, tim kiem giang vien."""

from __future__ import annotations

from dataclasses import dataclass

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.dich_vu.phan_quyen import QuyenHeThong, yeu_cau_quyen
from app.mo_hinh.giang_vien import GiangVien, TrangThaiGiangVien
from app.mo_hinh.lop_mon_hoc import LopMonHoc
from app.tien_ich.kiem_tra_du_lieu import (
    kiem_tra_chuoi_khong_rong,
    kiem_tra_dinh_dang_email,
    kiem_tra_dinh_dang_ma_dinh_danh,
    kiem_tra_dinh_dang_so_dien_thoai,
)


class LoiDuLieuGiangVien(Exception):
    """Loi nghiep vu lien quan den du lieu giang vien."""


@dataclass
class ThongTinGiangVien:
    """DTO the hien mot giang vien."""

    id: int
    ma_giang_vien: str
    ho_ten: str
    email: str | None
    so_dien_thoai: str | None
    khoa_id: int | None
    hoc_vi: str | None
    trang_thai: str
    so_lop_mon_hoc_phu_trach: int


def lay_danh_sach_giang_vien(tu_khoa_tim_kiem: str | None = None) -> list[ThongTinGiangVien]:
    """Lay danh sach giang vien, ho tro tim kiem theo ten/ma."""
    with mo_phien_lam_viec() as phien:
        truy_van = phien.query(GiangVien)
        if tu_khoa_tim_kiem:
            mau_tim = f"%{tu_khoa_tim_kiem.strip()}%"
            truy_van = truy_van.filter(
                (GiangVien.ho_ten.ilike(mau_tim)) | (GiangVien.ma_giang_vien.ilike(mau_tim))
            )
        danh_sach = truy_van.order_by(GiangVien.ho_ten).all()
        return [
            ThongTinGiangVien(
                id=gv.id,
                ma_giang_vien=gv.ma_giang_vien,
                ho_ten=gv.ho_ten,
                email=gv.email,
                so_dien_thoai=gv.so_dien_thoai,
                khoa_id=gv.khoa_id,
                hoc_vi=gv.hoc_vi,
                trang_thai=gv.trang_thai.value,
                so_lop_mon_hoc_phu_trach=len(gv.danh_sach_lop_mon_hoc),
            )
            for gv in danh_sach
        ]


def them_giang_vien(
    vai_tro_nguoi_thuc_hien: str,
    ma_giang_vien: str,
    ho_ten: str,
    email: str | None = None,
    so_dien_thoai: str | None = None,
    khoa_id: int | None = None,
    hoc_vi: str | None = None,
    nguoi_dung_id: int | None = None,
    nguoi_thuc_hien_id: int | None = None,
) -> int:
    """Them moi mot giang vien. Tra ve id giang vien vua tao."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_GIANG_VIEN)

    for hop_le, thong_bao in (
        kiem_tra_dinh_dang_ma_dinh_danh(ma_giang_vien, "Ma giang vien"),
        kiem_tra_chuoi_khong_rong(ho_ten, "Ho ten"),
        kiem_tra_dinh_dang_email(email),
        kiem_tra_dinh_dang_so_dien_thoai(so_dien_thoai),
    ):
        if not hop_le:
            raise LoiDuLieuGiangVien(thong_bao)

    with mo_phien_lam_viec() as phien:
        if phien.query(GiangVien).filter_by(ma_giang_vien=ma_giang_vien).first() is not None:
            raise LoiDuLieuGiangVien(f"Ma giang vien '{ma_giang_vien}' da ton tai.")

        giang_vien_moi = GiangVien(
            nguoi_dung_id=nguoi_dung_id,
            ma_giang_vien=ma_giang_vien,
            ho_ten=ho_ten,
            email=email,
            so_dien_thoai=so_dien_thoai,
            khoa_id=khoa_id,
            hoc_vi=hoc_vi,
            trang_thai=TrangThaiGiangVien.DANG_CONG_TAC,
        )
        phien.add(giang_vien_moi)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="THEM_GIANG_VIEN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="giang_vien",
            doi_tuong_id=giang_vien_moi.id,
            noi_dung=f"Them giang vien moi: {ma_giang_vien} - {ho_ten}.",
        )
        return giang_vien_moi.id


def cap_nhat_giang_vien(
    vai_tro_nguoi_thuc_hien: str,
    giang_vien_id: int,
    ho_ten: str,
    email: str | None = None,
    so_dien_thoai: str | None = None,
    khoa_id: int | None = None,
    hoc_vi: str | None = None,
    trang_thai: TrangThaiGiangVien | None = None,
    nguoi_thuc_hien_id: int | None = None,
) -> None:
    """Cap nhat thong tin mot giang vien da ton tai."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_GIANG_VIEN)

    with mo_phien_lam_viec() as phien:
        giang_vien = phien.get(GiangVien, giang_vien_id)
        if giang_vien is None:
            raise LoiDuLieuGiangVien("Khong tim thay giang vien.")

        giang_vien.ho_ten = ho_ten
        giang_vien.email = email
        giang_vien.so_dien_thoai = so_dien_thoai
        giang_vien.khoa_id = khoa_id
        giang_vien.hoc_vi = hoc_vi
        if trang_thai is not None:
            giang_vien.trang_thai = trang_thai
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="CAP_NHAT_GIANG_VIEN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="giang_vien",
            doi_tuong_id=giang_vien_id,
            noi_dung=f"Cap nhat thong tin giang vien {giang_vien.ma_giang_vien}.",
        )


def xoa_giang_vien(
    vai_tro_nguoi_thuc_hien: str, giang_vien_id: int, nguoi_thuc_hien_id: int | None = None
) -> None:
    """Xoa mot giang vien — CHI cho phep neu khong con phu trach lop hoc phan nao."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_GIANG_VIEN)

    with mo_phien_lam_viec() as phien:
        giang_vien = phien.get(GiangVien, giang_vien_id)
        if giang_vien is None:
            raise LoiDuLieuGiangVien("Khong tim thay giang vien.")

        con_phu_trach = (
            phien.query(LopMonHoc).filter_by(giang_vien_id=giang_vien_id).first() is not None
        )
        if con_phu_trach:
            raise LoiDuLieuGiangVien(
                "Khong the xoa giang vien dang phu trach lop hoc phan. "
                "Vui long chuyen giao vien khac phu trach truoc khi xoa."
            )

        ma_giang_vien = giang_vien.ma_giang_vien
        phien.delete(giang_vien)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="XOA_GIANG_VIEN",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="giang_vien",
            doi_tuong_id=giang_vien_id,
            noi_dung=f"Xoa giang vien {ma_giang_vien}.",
        )
